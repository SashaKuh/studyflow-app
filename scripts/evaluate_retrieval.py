"""Compare the original lexical search and the semantic MCP implementation."""

import os
from pathlib import Path

from harness.vault_server import VaultService


VAULT = Path(__file__).resolve().parents[2]/'studyflow-knowledge-base'
QUESTIONS = [
    ('Як студент позначає виконане завдання?', 'Статус задачі'),
    ('Чому навчальні дані зберігаються локально без окремого сервера?', 'Локальне зберігання'),
    ('Як запити до бази захищені від підстановки довільного SQL?', 'Параметризовані SQL-запити'),
    ('Як агент може зафіксувати архітектурне рішення без прямого доступу до нотаток?', 'Окремий vault'),
    ('Де реалізований відбір найближчих дедлайнів?', 'Фільтрація upcoming в окремому модулі'),
    ('Що зупиняє автоматичне відправлення коду прямо в основну гілку?', 'Блокування push у main через hook'),
    ('Яке правило перевіряє формат терміну задачі?', 'Валідація вводу'),
    ('Як отримати список завдань у табличному файлі?', 'CSV-експорт'),
    ('Як рахуються прострочені відкриті задачі?', 'Зведення'),
    ('Як навчальна задача пов’язана з предметом?', 'Дисципліна'),
]


def evaluate():
    svc = VaultService(VAULT)
    rows = []
    for query, gold in QUESTIONS:
        results = {}
        for mode in ('lexical', 'semantic'):
            os.environ['STUDYFLOW_RETRIEVAL_MODE'] = mode
            hits = svc.search_notes(query, 3)
            results[mode] = [h['title'] for h in hits]
        rows.append((query, gold, results['lexical'], results['semantic']))
    return rows


def main():
    rows = evaluate()
    out = Path(__file__).resolve().parents[1]/'docs/retrieval-comparison.md'
    lines = ['# ПР7: порівняння retrieval на однакових питаннях', '',
             'Одиниця chunking — одна Obsidian-нотатка. Модель: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 виміри); локальний індекс `.cache/index.npy`, метадані `.cache/index.json`. Джерело істини — Markdown vault.', '',
             '| № | Питання | Еталонна нотатка | Lexical top 3 | Semantic top 3 | L / S hit@3 |',
             '|---|---|---|---|---|---|']
    lexical_hits = semantic_hits = 0
    for i,(q,gold,lex,sem) in enumerate(rows,1):
        l = gold in lex; s = gold in sem
        lexical_hits += l; semantic_hits += s
        lines.append(f'| {i} | {q} | {gold} | {", ".join(lex) or "—"} | {", ".join(sem) or "—"} | {int(l)} / {int(s)} |')
    lines += ['', f'**Hit@3:** lexical {lexical_hits}/10; semantic {semantic_hits}/10.',
              '', 'Це вимірює лише знаходження релевантної нотатки, а не якість сформульованої відповіді агента. Для питань, що потребують поєднання нотаток, додатково перевіряється зміст відповіді у транскрипті Claude Code.']
    out.write_text('\n'.join(lines)+'\n', encoding='utf8')
    print('lexical', lexical_hits, 'semantic', semantic_hits, 'out', out)
    for i,(_,gold,lex,sem) in enumerate(rows,1):
        print(i,gold,'| L',lex,'| S',sem)


if __name__ == '__main__':
    main()
