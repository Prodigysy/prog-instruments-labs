from datetime import datetime
from typing import List, Optional


class Task:
    def __init__(self, title: str, description: str = '', due_date: Optional[
            str] = None, priority: str
              = 'Low', status: str = 'Pending') -> None:
        self.title = title
        self.description = description
        if isinstance(due_date, str):
            try:
                self.due_date = datetime.fromisoformat(due_date)
            except ValueError:
                self.due_date = None
        elif isinstance(due_date, datetime):
            self.due_date = due_date
        else:
            self.due_date = None  # Если дата не передана или некорректна
        self.priority = priority
        self.status = status
        self.created_at = datetime.now()

    def __str__(self) -> str:
        """Returns a string representation of the task."""
        return f"{self.title} ({self.status})"

    def mark_completed(self) -> None:
        """Marks the task as completed."""
        self.status = 'Completed'

    def update(self, **kwargs: str) -> None:
        """
        Updates task attributes using the provided arguments.

        Arguments:
            **kwargs: Keys may include 'title', 'description', 'due_date',
                      'priority', 'status'.
        """
        valid_fields = [
            'title', 'description', 'due_date', 'priority', 'status']

        for key, value in kwargs.items():
            if key in valid_fields:
                if key == 'due_date' and not isinstance(value, datetime):
                    continue  # Ignore incorrect date format
                setattr(self, key, value)


class TaskManager:
    """
    A class to manage tasks.

    Attributes:
        tasks (List[Task]): A list of tasks.
    """

    def __init__(self) -> None:
        """Initializes the task manager with an empty task list."""
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """
        Adds a new task to the list.

        Arguments:
            task (Task): The task instance to add.
        Exceptions:
            ValueError: If the provided object is not an instance of Task.
        """
        if isinstance(task, Task):
            self.tasks.append(task)
        else:
            raise ValueError("Task must be an instance of the Task class.")

    def remove_task(self, task: Task) -> None:
        """
        Removes a task from the list.

        Arguments:
            task (Task): The task instance to remove.
        Prints a message if the task is not found.
        """
        if task in self.tasks:
            self.tasks.remove(task)
        else:
            print("Task not found.")

    def get_tasks(self) -> List[Task]:
        """Returns all tasks."""
        return self.tasks

    def get_task_by_status(self, status: str) -> List[Task]:
        """
        Filters tasks by status.

        Arguments:
            status (str): The status of tasks to filter by.
        Returns:
            List[Task]: A list of tasks with the specified status.
        """
        return [task for task in self.tasks if task.status == status]

    def get_task_by_priority(self, priority: str) -> List[Task]:
        """
        Filters tasks by priority.

        Arguments:
            priority (str): The priority of tasks to filter by.
        Returns:
            List[Task]: A list of tasks with the specified priority.
        """
        return [task for task in self.tasks if task.priority == priority]

    def sort_tasks_by_due_date(self) -> List[Task]:
        """
        Sorts tasks by due date (ascending).

        Returns:
            List[Task]: A list of sorted tasks.
        """
        return sorted(
            self.tasks,
            key=lambda x: x.due_date if x.due_date else datetime.max)

    def group_tasks_by_priority(self) -> dict:
        """
        Groups tasks by priority.

        Returns:
            dict: A dictionary with priorities as keys and lists of
            tasks as values.
        """
        grouped = {}
        for task in self.tasks:
            if task.priority not in grouped:
                grouped[task.priority] = []
            grouped[task.priority].append(task)
        return grouped

    def filter_tasks_by_date_range(
            self,
            start_date: datetime, end_date: datetime) -> List[Task]:
        """
        Filters tasks by a date range.

        Arguments:
            start_date (datetime): The start date of the range.
            end_date (datetime): The end date of the range.
        Returns:
            List[Task]: A list of tasks that fall within
            the specified date range.
        """
        return [
            task for task in self.tasks
            if task.due_date and start_date <= task.due_date <= end_date]
