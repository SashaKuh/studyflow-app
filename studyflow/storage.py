import csv
import sqlite3
from datetime import date
from pathlib import Path

from .domain import Task, validate_task


class TaskStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                course TEXT NOT NULL,
                due TEXT,
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'done')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )''')

    def connect(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    def add(self, title: str, course: str, due: str | None = None) -> int:
        title, course, due = validate_task(title, course, due)
        with self.connect() as db:
            cur = db.execute('INSERT INTO tasks(title, course, due) VALUES (?, ?, ?)', (title, course, due))
            return cur.lastrowid

    def list(self, course: str | None = None, status: str | None = None) -> list[Task]:
        if status not in (None, 'open', 'done'):
            raise ValueError('Невідомий статус')
        sql = 'SELECT id, title, course, due, status FROM tasks WHERE 1=1'
        params = []
        if course:
            sql += ' AND course = ?'; params.append(course)
        if status:
            sql += ' AND status = ?'; params.append(status)
        sql += ' ORDER BY id'
        with self.connect() as db:
            return [Task(**dict(row)) for row in db.execute(sql, params)]

    def done(self, task_id: int) -> bool:
        with self.connect() as db:
            cur = db.execute("UPDATE tasks SET status = 'done' WHERE id = ? AND status = 'open'", (task_id,))
            return cur.rowcount == 1

    def summary(self, today: date | None = None) -> dict[str, int]:
        day = (today or date.today()).isoformat()
        with self.connect() as db:
            row = db.execute('''SELECT
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open,
                SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS done,
                SUM(CASE WHEN status = 'open' AND due < ? THEN 1 ELSE 0 END) AS overdue
                FROM tasks''', (day,)).fetchone()
        return {key: row[key] or 0 for key in ('open', 'done', 'overdue')}

    def export_csv(self, output: str | Path) -> int:
        tasks = self.list()
        with Path(output).open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'course', 'due', 'status'])
            for t in tasks:
                writer.writerow([t.id, t.title, t.course, t.due or '', t.status])
        return len(tasks)
