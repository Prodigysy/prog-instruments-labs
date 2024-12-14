import pytest

from unittest.mock import patch
from datetime import datetime
from task_manager import Task, TaskManager


@pytest.fixture
def task():
    return Task(title="Test Task", description="Test Description",
                due_date="2024-12-20", priority="High", status="Pending")


@pytest.fixture
def task_manager():
    return TaskManager()


def test_task_creation(task):
    """Test task creation with valid data."""
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.due_date == datetime(2024, 12, 20)
    assert task.priority == "High"
    assert task.status == "Pending"
    assert task.created_at is not None


def test_task_default_status():
    """Test the default status of a task."""
    task = Task(title="Another Task")
    assert task.status == "Pending"


def test_task_mark_completed(task):
    """Test task completion."""
    task.mark_completed()
    assert task.status == "Completed"


def test_update_task(task):
    """Test updating a task."""
    task.update(title="Updated Task", description="Updated Description",
                status="Completed")
    assert task.title == "Updated Task"
    assert task.description == "Updated Description"
    assert task.status == "Completed"


def test_add_task_to_manager(task_manager, task):
    """Test adding a task to the manager."""
    task_manager.add_task(task)
    tasks = task_manager.get_tasks()
    assert len(tasks) == 1
    assert tasks[0] == task


def test_task_removal(task_manager, task):
    """Test removing a task from the manager."""
    task_manager.add_task(task)
    task_manager.remove_task(task)
    tasks = task_manager.get_tasks()
    assert len(tasks) == 0


@pytest.mark.parametrize(
    "due_date, expected_due_date",
    [
        ("2024-12-20", datetime(2024, 12, 20)),
        ("2025-01-01", datetime(2025, 1, 1)),
        (None, None)
    ]
)
def test_task_due_date_parametrized(due_date, expected_due_date):
    """Test parametrized task creation with different due dates."""
    task = Task(title="Param Task", due_date=due_date)
    assert task.due_date == expected_due_date


@patch('task_manager.datetime')
def test_task_due_date_with_mocked_time(mock_datetime, task):
    """Test using mock to simulate time-related behavior."""
    mock_datetime.now.return_value = datetime(2024, 12, 14, 10, 0, 0)
    task = Task(title="Mocked Task", due_date="2024-12-20")
    assert task.created_at == datetime(2024, 12, 14, 10, 0, 0)


def test_filter_tasks_by_date_range(task_manager):
    """Test filtering tasks by date range."""
    task1 = Task(title="Task 1", due_date="2024-12-19")
    task2 = Task(title="Task 2", due_date="2024-12-21")
    task_manager.add_task(task1)
    task_manager.add_task(task2)
    start_date = datetime(2024, 12, 18)
    end_date = datetime(2024, 12, 20)
    filtered_tasks = task_manager.filter_tasks_by_date_range(
        start_date, end_date)
    assert len(filtered_tasks) == 1
    assert filtered_tasks[0] == task1


def test_group_tasks_by_priority(task_manager):
    """Test grouping tasks by priority."""
    task1 = Task(title="Low Priority Task", priority="Low")
    task2 = Task(title="High Priority Task", priority="High")
    task_manager.add_task(task1)
    task_manager.add_task(task2)
    grouped_tasks = task_manager.group_tasks_by_priority()
    assert "Low" in grouped_tasks
    assert "High" in grouped_tasks
    assert len(grouped_tasks["Low"]) == 1
    assert len(grouped_tasks["High"]) == 1
