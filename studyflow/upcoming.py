"""Відкриті задачі з терміном у вікні [сьогодні, сьогодні + N днів] включно.

Модуль лише читає дані через ``TaskStore.list(status='open')`` і нічого не
змінює в базі. Фільтрація чиста й залежить тільки від переданої дати, тому
результат відтворюваний для однакових даних і дати перевірки.
"""

from collections.abc import Iterable
from datetime import date, timedelta

from .domain import Task
from .storage import TaskStore


def validate_days(days: int) -> int:
    if days < 0:
        raise ValueError("Кількість днів не може бути від'ємною")
    return days


def window_end(start: date, days: int) -> date:
    # Дуже велике N (наприклад 10**9) виходить за межі date/timedelta;
    # тоді вікно просто триває до кінця календаря, без traceback.
    try:
        return start + timedelta(days=days)
    except OverflowError:
        return date.max


def select_upcoming(tasks: Iterable[Task], days: int, today: date) -> list[Task]:
    validate_days(days)
    start = today.isoformat()
    end = window_end(today, days).isoformat()
    # `due` зберігається як ISO-рядок YYYY-MM-DD (validate_task), тому
    # порівняння рядків збігається з порівнянням дат, як і в TaskStore.summary.
    selected = [
        t for t in tasks
        if t.status == 'open' and t.due and start <= t.due <= end
    ]
    return sorted(selected, key=lambda t: (t.due, t.id))


def upcoming(store: TaskStore, days: int, today: date | None = None) -> list[Task]:
    return select_upcoming(store.list(status='open'), days, today or date.today())
