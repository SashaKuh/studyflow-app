# StudyFlow

Локальний застосунок для навчальних задач і навчальний agent harness.

## Запуск

```bash
python3.12 -m venv ../../.venv
../../.venv/bin/pip install -e '.[test]'
../../.venv/bin/studyflow --db demo.db add 'Прочитати розділ' --course Англійська --due 2026-11-10
../../.venv/bin/studyflow --db demo.db list
../../.venv/bin/studyflow --db demo.db summary
../../.venv/bin/studyflow --db demo.db upcoming --days 7
../../.venv/bin/pytest -q
```

Vault має бути окремим сусіднім каталогом `../studyflow-knowledge-base`. Для локальної роботи Claude Code відкрийте саме цей репозиторій. MCP-конфігурація лежить у `.mcp.json`; GitHub MCP використовує змінну середовища `GITHUB_PERSONAL_ACCESS_TOKEN`, яку не можна комітити. Скрипт `scripts/run-vault-server.sh` використовує курсова `.venv` у директорії на два рівні вище; при іншому розміщенні змініть його шлях до Python.

Результати семи практичних описані в `docs/practical-*.md`. Векторний індекс у `.cache/` генерується повторно з vault.
