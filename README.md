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

Сім звітів Word збережено в сусідній директорії `../Звіти/`. Деталі реалізації та перевірок наведено у файлах `docs/`. Векторний індекс у `.cache/` генерується повторно з vault.

Для ПР7 `search_notes(query, limit=5)` за замовчуванням використовує локальні багатомовні embeddings FastEmbed. Перший запуск завантажує модель `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (близько 220 МБ) у `.cache/models/`. Для відтворення базового пошуку встановіть `STUDYFLOW_RETRIEVAL_MODE=lexical`; інтерфейс MCP-інструмента не змінюється. Порівняння запускається командою `../../.venv/bin/python scripts/evaluate_retrieval.py`.
