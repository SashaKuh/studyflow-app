# Guardrails StudyFlow

## Allow

| Правило | Приклад | Перевірка |
|---|---|---|
| A1 Читання коду й документації | `Read docs/app-requirements.md` | без додаткового запиту |
| A2 Локальні тести | `pytest -q` | без додаткового запиту |
| A3 Пошук у vault через MCP | `search_notes("SQLite")` | без додаткового запиту |

## Warn / ask

| Правило | Приклад | Перевірка |
|---|---|---|
| W1 Редагування ядра зберігання | `Edit studyflow/storage.py` | hook повертає `ask` |
| W2 Зміна схеми бази | Bash з `ALTER TABLE` | hook повертає `ask` |
| W3 Коміт із Claude Code | Bash `git commit` | hook повертає `ask` |

## Block

| Правило | Приклад | Перевірка |
|---|---|---|
| B1 Прямий push у main агентом | `git push origin main` | hook повертає `deny` |
| B2 Руйнівне видалення | `rm -rf` | hook повертає `deny` |
| B3 Прямий запис у Decisions/ поза MCP | `Write ../studyflow-knowledge-base/Decisions/X.md` | hook повертає `deny` |

Hook перехоплює `Bash`, `Write` і `Edit` у Claude Code. Він перевіряє поширені форми команд і демонструє технічне блокування. Це навчальний механізм, а не повноцінна ізоляція процесів: для production потрібні додаткові права ОС та захист гілки на GitHub.
