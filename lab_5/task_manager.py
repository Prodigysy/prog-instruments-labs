from datetime import datetime
from typing import List, Optional


class Task:
    """
    Класс для представления задачи.

    Атрибуты:
        title (str): Заголовок задачи.
        description (str): Описание задачи.
        due_date (Optional[datetime]): Дата выполнения задачи.
        priority (str): Приоритет задачи (например, "Low", "Medium", "High").
        status (str): Статус задачи (например, "Pending", "Completed").
        created_at (datetime): Время создания задачи.
    """

    def __init__(
            self,
            title: str,
            description: str = '',
            due_date: Optional[datetime] = None,
            priority: str = 'Low',
            status: str = 'Pending') -> None:
        """
        Инициализирует новую задачу.

        Аргументы:
            title (str): Заголовок задачи.
            description (str): Описание задачи.
            due_date (Optional[datetime]): Дата выполнения задачи.
            priority (str): Приоритет задачи.
            status (str): Статус задачи.
        """
        self.title = title
        self.description = description
        self.due_date = due_date if isinstance(due_date, datetime) else None
        self.priority = priority
        self.status = status
        self.created_at = datetime.now()

    def __str__(self) -> str:
        """Возвращает строковое представление задачи."""
        return f"{self.title} ({self.status})"

    def mark_completed(self) -> None:
        """Помечает задачу как выполненную."""
        self.status = 'Completed'

    def update(self, **kwargs: str) -> None:
        """
        Обновляет атрибуты задачи с помощью переданных аргументов.

        Аргументы:
            **kwargs: Ключи могут быть 'title', 'description', 'due_date',
             'priority', 'status'.
        """
        valid_fields = [
            'title', 'description', 'due_date', 'priority', 'status']

        for key, value in kwargs.items():
            if key in valid_fields:
                if key == 'due_date' and not isinstance(value, datetime):
                    continue  # Игнорировать неправильный формат даты
                setattr(self, key, value)


class TaskManager:
    """
    Класс для управления задачами.

    Атрибуты:
        tasks (List[Task]): Список задач.
    """

    def __init__(self) -> None:
        """Инициализирует менеджер задач с пустым списком задач."""
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """
        Добавляет новую задачу в список.

        Аргументы:
            task (Task): Экземпляр задачи для добавления.
        Исключения:
            ValueError: Если переданный объект не является экземпляром
            класса Task.
        """
        if isinstance(task, Task):
            self.tasks.append(task)
        else:
            raise ValueError("Задача должна быть экземпляром класса Task.")

    def remove_task(self, task: Task) -> None:
        """
        Удаляет задачу из списка.

        Аргументы:
            task (Task): Экземпляр задачи для удаления.
        Выводит сообщение, если задача не найдена.
        """
        if task in self.tasks:
            self.tasks.remove(task)
        else:
            print("Задача не найдена.")

    def get_tasks(self) -> List[Task]:
        """Возвращает все задачи."""
        return self.tasks

    def get_task_by_status(self, status: str) -> List[Task]:
        """
        Фильтрует задачи по статусу.

        Аргументы:
            status (str): Статус задачи для фильтрации.
        Возвращает:
            List[Task]: Список задач с указанным статусом.
        """
        return [task for task in self.tasks if task.status == status]

    def get_task_by_priority(self, priority: str) -> List[Task]:
        """
        Фильтрует задачи по приоритету.

        Аргументы:
            priority (str): Приоритет задачи для фильтрации.
        Возвращает:
            List[Task]: Список задач с указанным приоритетом.
        """
        return [task for task in self.tasks if task.priority == priority]

    def sort_tasks_by_due_date(self) -> List[Task]:
        """
        Сортирует задачи по дате выполнения (по возрастанию).

        Возвращает:
            List[Task]: Список отсортированных задач.
        """
        return sorted(
            self.tasks,
            key=lambda x: x.due_date if x.due_date else datetime.max)

    def group_tasks_by_priority(self) -> dict:
        """
        Группирует задачи по приоритету.

        Возвращает:
            dict: Словарь с приоритетами как ключами
            и списками задач как значениями.
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
        Фильтрует задачи по диапазону дат.

        Аргументы:
            start_date (datetime): Начальная дата диапазона.
            end_date (datetime): Конечная дата диапазона.
        Возвращает:
            List[Task]: Список задач, попадающих в указанный диапазон дат.
        """
        return [
            task for task in self.tasks
            if task.due_date and start_date <= task.due_date <= end_date]
