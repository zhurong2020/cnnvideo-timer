"""
Task management system using SQLite.

Handles task creation, status tracking, and background processing.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from .config import get_settings

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingMode(str, Enum):
    """Video processing mode for learning."""

    ORIGINAL = "original"  # Original video only
    WITH_SUBTITLE = "with_subtitle"  # Original + subtitle
    REPEAT_TWICE = "repeat_twice"  # Play twice, second time with subtitle
    SLOW_WITH_SUBTITLE = "slow"  # Slow playback with subtitle


@dataclass
class Task:
    """Task data model."""

    id: str
    user_id: str
    source_id: str
    video_id: str
    video_url: str
    video_title: str
    status: TaskStatus
    processing_mode: ProcessingMode
    progress: int  # 0-100
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    output_file: str | None = None
    subtitle_file: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source_id": self.source_id,
            "video_id": self.video_id,
            "video_url": self.video_url,
            "video_title": self.video_title,
            "status": self.status.value,
            "processing_mode": self.processing_mode.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "output_file": self.output_file,
            "subtitle_file": self.subtitle_file,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class TaskManager:
    """Manages video download and processing tasks."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.settings = get_settings()
        self.db_path = self.settings.data_dir / "tasks.db"
        self._init_database()
        self._processing_tasks: dict[str, asyncio.Task] = {}
        self._semaphore = asyncio.Semaphore(self.settings.max_concurrent_tasks)
        self._initialized = True

    def _init_database(self):
        """Initialize the SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    video_title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    processing_mode TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    output_file TEXT,
                    subtitle_file TEXT,
                    error_message TEXT,
                    metadata TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
            """
            )

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert database row to Task object."""
        return Task(
            id=row["id"],
            user_id=row["user_id"],
            source_id=row["source_id"],
            video_id=row["video_id"],
            video_url=row["video_url"],
            video_title=row["video_title"],
            status=TaskStatus(row["status"]),
            processing_mode=ProcessingMode(row["processing_mode"]),
            progress=row["progress"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            ),
            output_file=row["output_file"],
            subtitle_file=row["subtitle_file"],
            error_message=row["error_message"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
        )

    def create_task(
        self,
        user_id: str,
        source_id: str,
        video_id: str,
        video_url: str,
        video_title: str,
        processing_mode: ProcessingMode = ProcessingMode.WITH_SUBTITLE,
    ) -> Task:
        """Create a new task."""
        now = datetime.now()
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            source_id=source_id,
            video_id=video_id,
            video_url=video_url,
            video_title=video_title,
            status=TaskStatus.PENDING,
            processing_mode=processing_mode,
            progress=0,
            created_at=now,
            updated_at=now,
        )

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, user_id, source_id, video_id, video_url, video_title,
                    status, processing_mode, progress, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.user_id,
                    task.source_id,
                    task.video_id,
                    task.video_url,
                    task.video_title,
                    task.status.value,
                    task.processing_mode.value,
                    task.progress,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
            conn.commit()

        logger.info(f"Created task {task.id} for video {video_id}")
        return task

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return self._row_to_task(row) if row else None

    def get_user_tasks(
        self, user_id: str, status: TaskStatus | None = None, limit: int = 20
    ) -> list[Task]:
        """Get tasks for a user."""
        with self._get_connection() as conn:
            if status:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY created_at DESC LIMIT ?",
                    (user_id, status.value, limit),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                )
            return [self._row_to_task(row) for row in cursor.fetchall()]

    def update_task(
        self,
        task_id: str,
        status: TaskStatus | None = None,
        progress: int | None = None,
        output_file: str | None = None,
        subtitle_file: str | None = None,
        error_message: str | None = None,
    ) -> Task | None:
        """Update a task."""
        updates = ["updated_at = ?"]
        params = [datetime.now().isoformat()]

        if status:
            updates.append("status = ?")
            params.append(status.value)
            if status == TaskStatus.COMPLETED:
                updates.append("completed_at = ?")
                params.append(datetime.now().isoformat())

        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)

        if output_file is not None:
            updates.append("output_file = ?")
            params.append(output_file)

        if subtitle_file is not None:
            updates.append("subtitle_file = ?")
            params.append(subtitle_file)

        if error_message is not None:
            updates.append("error_message = ?")
            params.append(error_message)

        params.append(task_id)

        with self._get_connection() as conn:
            conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

        return self.get_task(task_id)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        task = self.get_task(task_id)
        if not task:
            return False

        # Clean up files
        if task.output_file and Path(task.output_file).exists():
            Path(task.output_file).unlink()
        if task.subtitle_file and Path(task.subtitle_file).exists():
            Path(task.subtitle_file).unlink()

        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

        logger.info(f"Deleted task {task_id}")
        return True

    def cleanup_old_tasks(self) -> int:
        """Clean up tasks older than retention period."""
        cutoff = datetime.now() - timedelta(hours=self.settings.task_retention_hours)

        with self._get_connection() as conn:
            # Get old completed tasks
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE status IN (?, ?) AND completed_at < ?",
                (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, cutoff.isoformat()),
            )
            old_tasks = [self._row_to_task(row) for row in cursor.fetchall()]

            # Clean up files
            for task in old_tasks:
                if task.output_file and Path(task.output_file).exists():
                    Path(task.output_file).unlink()
                if task.subtitle_file and Path(task.subtitle_file).exists():
                    Path(task.subtitle_file).unlink()

            # Delete from database
            conn.execute(
                "DELETE FROM tasks WHERE status IN (?, ?) AND completed_at < ?",
                (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, cutoff.isoformat()),
            )
            conn.commit()

        logger.info(f"Cleaned up {len(old_tasks)} old tasks")
        return len(old_tasks)

    def get_pending_tasks_count(self) -> int:
        """Get count of pending tasks."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status IN (?, ?, ?)",
                (
                    TaskStatus.PENDING.value,
                    TaskStatus.DOWNLOADING.value,
                    TaskStatus.PROCESSING.value,
                ),
            )
            return cursor.fetchone()[0]


# Global instance
def get_task_manager() -> TaskManager:
    """Get the task manager singleton."""
    return TaskManager()
