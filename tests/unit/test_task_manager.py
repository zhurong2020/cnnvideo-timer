"""
Unit tests for task manager module.
"""

import pytest


class TestTaskManager:
    """Tests for TaskManager class."""

    @pytest.fixture
    def task_manager(self, test_config):
        """Get task manager instance (uses singleton)."""
        from src.core.task_manager import TaskManager

        # Reset singleton for clean test state
        TaskManager._instance = None

        manager = TaskManager()
        yield manager

        # Cleanup: delete all test tasks
        with manager._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE user_id LIKE 'test-%'")
            conn.commit()

    def test_create_task(self, task_manager):
        """Test creating a new task."""
        from src.core.task_manager import ProcessingMode

        task = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        assert task is not None
        assert task.id is not None
        assert task.user_id == "test-user"
        assert task.source_id == "cnn10"
        assert task.video_id == "abc123"
        assert task.video_title == "Test Video"

    def test_get_task(self, task_manager):
        """Test retrieving a task by ID."""
        from src.core.task_manager import ProcessingMode

        created = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        retrieved = task_manager.get_task(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.video_title == "Test Video"

    def test_get_nonexistent_task(self, task_manager):
        """Test retrieving a non-existent task returns None."""
        task = task_manager.get_task("nonexistent-id")
        assert task is None

    def test_update_task_status(self, task_manager):
        """Test updating task status."""
        from src.core.task_manager import ProcessingMode, TaskStatus

        task = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        updated = task_manager.update_task(
            task.id,
            status=TaskStatus.DOWNLOADING,
            progress=25,
        )

        assert updated.status == TaskStatus.DOWNLOADING
        assert updated.progress == 25

    def test_update_task_completion(self, task_manager):
        """Test marking task as completed."""
        from src.core.task_manager import ProcessingMode, TaskStatus

        task = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        updated = task_manager.update_task(
            task.id,
            status=TaskStatus.COMPLETED,
            progress=100,
            output_file="/path/to/output.mp4",
        )

        assert updated.status == TaskStatus.COMPLETED
        assert updated.progress == 100
        assert updated.output_file == "/path/to/output.mp4"
        assert updated.completed_at is not None

    def test_update_task_failure(self, task_manager):
        """Test marking task as failed with error message."""
        from src.core.task_manager import ProcessingMode, TaskStatus

        task = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        updated = task_manager.update_task(
            task.id,
            status=TaskStatus.FAILED,
            error_message="Download failed: network error",
        )

        assert updated.status == TaskStatus.FAILED
        assert "network error" in updated.error_message

    def test_delete_task(self, task_manager):
        """Test deleting a task."""
        from src.core.task_manager import ProcessingMode

        task = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="abc123",
            video_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        result = task_manager.delete_task(task.id)
        assert result is True

        # Verify task is deleted
        deleted = task_manager.get_task(task.id)
        assert deleted is None

    def test_delete_nonexistent_task(self, task_manager):
        """Test deleting a non-existent task returns False."""
        result = task_manager.delete_task("nonexistent-id")
        assert result is False

    def test_get_user_tasks(self, task_manager):
        """Test getting all tasks for a user."""
        from src.core.task_manager import ProcessingMode

        # Create multiple tasks for same user
        for i in range(3):
            task_manager.create_task(
                user_id="test-user",
                source_id="cnn10",
                video_id=f"video{i}",
                video_url=f"https://youtube.com/watch?v=video{i}",
                video_title=f"Test Video {i}",
                processing_mode=ProcessingMode.WITH_SUBTITLE,
            )

        # Create task for different user
        task_manager.create_task(
            user_id="test-other-user",
            source_id="cnn10",
            video_id="other",
            video_url="https://youtube.com/watch?v=other",
            video_title="Other User Video",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )

        tasks = task_manager.get_user_tasks("test-user")

        assert len(tasks) == 3
        assert all(t.user_id == "test-user" for t in tasks)

    def test_get_user_tasks_with_status_filter(self, task_manager):
        """Test filtering user tasks by status."""
        from src.core.task_manager import ProcessingMode, TaskStatus

        # Create tasks with different statuses
        task1 = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="video1",
            video_url="https://youtube.com/watch?v=video1",
            video_title="Test Video 1",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )
        task_manager.update_task(task1.id, status=TaskStatus.COMPLETED)

        task2 = task_manager.create_task(
            user_id="test-user",
            source_id="cnn10",
            video_id="video2",
            video_url="https://youtube.com/watch?v=video2",
            video_title="Test Video 2",
            processing_mode=ProcessingMode.WITH_SUBTITLE,
        )
        # task2 remains PENDING

        completed = task_manager.get_user_tasks("test-user", status=TaskStatus.COMPLETED)
        pending = task_manager.get_user_tasks("test-user", status=TaskStatus.PENDING)

        assert len(completed) == 1
        assert len(pending) == 1
        assert completed[0].id == task1.id
        assert pending[0].id == task2.id

    def test_get_pending_tasks_count(self, task_manager):
        """Test counting pending tasks."""
        from src.core.task_manager import ProcessingMode, TaskStatus

        # Get initial count
        initial_count = task_manager.get_pending_tasks_count()

        # Create some tasks
        task_ids = []
        for i in range(5):
            task = task_manager.create_task(
                user_id="test-user",
                source_id="cnn10",
                video_id=f"video{i}",
                video_url=f"https://youtube.com/watch?v=video{i}",
                video_title=f"Test Video {i}",
                processing_mode=ProcessingMode.WITH_SUBTITLE,
            )
            task_ids.append(task.id)
            # Complete some tasks
            if i < 2:
                task_manager.update_task(task.id, status=TaskStatus.COMPLETED)

        count = task_manager.get_pending_tasks_count()

        # 5 created, 2 completed = 3 pending (plus initial)
        assert count == initial_count + 3


class TestProcessingMode:
    """Tests for ProcessingMode enum."""

    def test_processing_mode_values(self):
        """Test ProcessingMode enum has expected values."""
        from src.core.task_manager import ProcessingMode

        # Check actual enum values from implementation
        assert ProcessingMode.ORIGINAL.value == "original"
        assert ProcessingMode.WITH_SUBTITLE.value == "with_subtitle"
        assert ProcessingMode.REPEAT_TWICE.value == "repeat_twice"
        assert ProcessingMode.SLOW_WITH_SUBTITLE.value == "slow"


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_task_status_values(self):
        """Test TaskStatus enum has expected values."""
        from src.core.task_manager import TaskStatus

        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.DOWNLOADING.value == "downloading"
        assert TaskStatus.PROCESSING.value == "processing"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
