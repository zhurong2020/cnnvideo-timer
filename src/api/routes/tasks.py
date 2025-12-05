"""
Tasks API routes.
"""

from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Header, BackgroundTasks, Depends
from fastapi.responses import FileResponse

from ..models import (
    TaskCreateRequest,
    TaskResponse,
    TaskListResponse,
    TaskStatusEnum,
    ProcessingModeEnum,
)
from ...core.task_manager import (
    get_task_manager,
    TaskStatus,
    ProcessingMode,
)
from ...core.downloader import VideoDownloader
from ...core.config import get_settings
from ..dependencies import verify_api_key, get_user_id

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _status_to_enum(status: TaskStatus) -> TaskStatusEnum:
    """Convert internal status to API enum."""
    return TaskStatusEnum(status.value)


def _mode_to_enum(mode: ProcessingMode) -> ProcessingModeEnum:
    """Convert internal mode to API enum."""
    return ProcessingModeEnum(mode.value)


def _task_to_response(task, settings) -> TaskResponse:
    """Convert Task to TaskResponse."""
    download_url = None
    if task.status == TaskStatus.COMPLETED and task.output_file:
        download_url = f"/api/v1/tasks/{task.id}/download"

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        source_id=task.source_id,
        video_id=task.video_id,
        video_url=task.video_url,
        video_title=task.video_title,
        status=_status_to_enum(task.status),
        processing_mode=_mode_to_enum(task.processing_mode),
        progress=task.progress,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        download_url=download_url,
        error_message=task.error_message,
    )


async def process_task_background(task_id: str):
    """Background task to process video download and processing."""
    import logging
    from ...processors.learning_modes import LearningModeProcessor, LearningMode

    logger = logging.getLogger(__name__)
    manager = get_task_manager()
    settings = get_settings()
    task = manager.get_task(task_id)

    if not task:
        return

    try:
        # Step 1: Download the video
        logger.info(f"[Task {task_id}] Starting download")
        manager.update_task(task_id, status=TaskStatus.DOWNLOADING, progress=10)

        downloader = VideoDownloader(output_dir=settings.temp_dir)
        result = downloader.download(task.video_url)

        if not result.success:
            manager.update_task(
                task_id,
                status=TaskStatus.FAILED,
                error_message=result.error or "Download failed"
            )
            return

        logger.info(f"[Task {task_id}] Download completed: {result.file_path}")
        manager.update_task(task_id, progress=40)

        # Step 2: Process video with learning mode
        logger.info(f"[Task {task_id}] Starting processing (mode: {task.processing_mode})")
        manager.update_task(task_id, status=TaskStatus.PROCESSING, progress=50)

        # Generate output filename
        output_path = settings.temp_dir / f"{task.id}_processed.mp4"

        # Apply learning mode
        processor = LearningModeProcessor()
        learning_mode = LearningMode(task.processing_mode.value)

        processed_path = processor.process(
            video_path=result.file_path,
            output_path=output_path,
            mode=learning_mode,
            video_url=task.video_url,
            whisper_model=settings.whisper_model,
            progress_callback=lambda cur, total: manager.update_task(
                task_id,
                progress=min(50 + int((cur / max(total, 1)) * 40), 90)
            ) if total > 0 else None,
        )

        logger.info(f"[Task {task_id}] Processing completed: {processed_path}")
        manager.update_task(task_id, progress=95)

        # Clean up original downloaded file if different from processed
        if processed_path != result.file_path and result.file_path.exists():
            result.file_path.unlink()

        # Mark as completed
        manager.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            output_file=str(processed_path),
        )

        logger.info(f"[Task {task_id}] Task completed successfully")

    except Exception as e:
        logger.error(f"[Task {task_id}] Task failed: {e}", exc_info=True)
        manager.update_task(
            task_id,
            status=TaskStatus.FAILED,
            error_message=str(e)
        )


@router.post("", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """Create a new video download/processing task."""
    settings = get_settings()
    manager = get_task_manager()

    # Check concurrent task limit
    pending_count = manager.get_pending_tasks_count()
    if pending_count >= settings.max_concurrent_tasks * 2:  # Allow some queue
        raise HTTPException(
            status_code=429,
            detail="Too many pending tasks. Please wait and try again."
        )

    # Get video info
    downloader = VideoDownloader()
    video_info = downloader.get_video_info(request.video_url)

    if not video_info:
        raise HTTPException(
            status_code=400,
            detail="Could not get video information. Please check the URL."
        )

    # Create task
    processing_mode = ProcessingMode(request.processing_mode.value)
    task = manager.create_task(
        user_id=user_id,
        source_id=request.source_id,
        video_id=video_info.id,
        video_url=request.video_url,
        video_title=video_info.title,
        processing_mode=processing_mode,
    )

    # Start background processing
    background_tasks.add_task(process_task_background, task.id)

    return _task_to_response(task, settings)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatusEnum] = Query(default=None, description="Filter by status"),
    limit: int = Query(default=20, ge=1, le=100),
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """Get list of tasks for the current user."""
    settings = get_settings()
    manager = get_task_manager()

    task_status = TaskStatus(status.value) if status else None
    tasks = manager.get_user_tasks(user_id, status=task_status, limit=limit)

    return TaskListResponse(
        tasks=[_task_to_response(t, settings) for t in tasks],
        total=len(tasks),
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """Get task details."""
    settings = get_settings()
    manager = get_task_manager()

    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check user owns this task (skip for now, can add auth later)
    # if task.user_id != user_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    return _task_to_response(task, settings)


@router.get("/{task_id}/download")
async def download_task_file(
    task_id: str,
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """Download the processed video file."""
    manager = get_task_manager()

    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Task not completed yet")

    if not task.output_file:
        raise HTTPException(status_code=404, detail="Output file not found")

    file_path = Path(task.output_file)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    # Generate a safe filename
    safe_filename = f"{task.video_title[:50]}_{task.video_id}.mp4".replace(" ", "_")

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type="video/mp4",
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """Delete a task and its files."""
    manager = get_task_manager()

    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    success = manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete task")

    return {"message": "Task deleted successfully"}
