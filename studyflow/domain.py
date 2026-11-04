from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    course: str
    due: str | None
    status: str


def validate_task(title: str, course: str, due: str | None) -> tuple[str, str, str | None]:
    title = title.strip()
    course = course.strip()
    if not title:
        raise ValueError("Назва задачі не може бути порожньою")
    if not course:
        raise ValueError("Назва дисципліни не може бути порожньою")
    if due:
        try:
            due = date.fromisoformat(due).isoformat()
        except ValueError as exc:
            raise ValueError("Термін має формат YYYY-MM-DD") from exc
    return title, course, due
