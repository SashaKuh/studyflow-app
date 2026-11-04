import hashlib
from datetime import date, timedelta

import pytest

from studyflow.cli import main
from studyflow.domain import Task
from studyflow.storage import TaskStore
from studyflow.upcoming import select_upcoming, upcoming, validate_days

TODAY = date(2026, 11, 4)


def make_store(tmp_path):
    store = TaskStore(tmp_path/'tasks.db')
    ids = {
        'overdue': store.add('Overdue', 'C', '2026-11-03'),
        'today': store.add('Today', 'C', '2026-11-04'),
        'last': store.add('Last day', 'C', '2026-11-07'),
        'after': store.add('After window', 'C', '2026-11-08'),
        'nodue': store.add('No due', 'C'),
        'done': store.add('Done in window', 'C', '2026-11-05'),
    }
    store.done(ids['done'])
    return store, ids


def test_upcoming_inclusive_window(tmp_path):
    store, ids = make_store(tmp_path)
    assert [t.id for t in upcoming(store, 3, TODAY)] == [ids['today'], ids['last']]


def test_upcoming_zero_days(tmp_path):
    store, ids = make_store(tmp_path)
    assert [t.id for t in upcoming(store, 0, TODAY)] == [ids['today']]


def test_upcoming_order_by_due_then_id(tmp_path):
    store = TaskStore(tmp_path/'tasks.db')
    late = store.add('Late', 'C', '2026-11-06')
    a = store.add('A', 'C', '2026-11-05')
    b = store.add('B', 'C', '2026-11-05')
    assert [t.id for t in upcoming(store, 7, TODAY)] == [a, b, late]


def test_select_upcoming_is_pure_and_sorts():
    tasks = [
        Task(3, 'x', 'C', '2026-11-05', 'open'),
        Task(1, 'y', 'C', '2026-11-05', 'open'),
        Task(2, 'z', 'C', '2026-11-04', 'open'),
        Task(4, 'w', 'C', '2026-11-04', 'done'),
    ]
    assert [t.id for t in select_upcoming(tasks, 1, TODAY)] == [2, 1, 3]


@pytest.mark.parametrize('days', [-1, -100])
def test_upcoming_rejects_negative(tmp_path, days):
    with pytest.raises(ValueError):
        validate_days(days)
    store, _ = make_store(tmp_path)
    with pytest.raises(ValueError):
        upcoming(store, days, TODAY)


def test_upcoming_read_only(tmp_path):
    store, _ = make_store(tmp_path)
    db = tmp_path/'tasks.db'
    before_hash, before_list = hashlib.sha256(db.read_bytes()).hexdigest(), store.list()
    upcoming(store, 3, TODAY)
    assert hashlib.sha256(db.read_bytes()).hexdigest() == before_hash
    assert store.list() == before_list


def test_upcoming_huge_days(tmp_path):
    store, ids = make_store(tmp_path)
    assert [t.id for t in upcoming(store, 10**9, TODAY)] == [ids['today'], ids['last'], ids['after']]


def test_cli_upcoming_negative(tmp_path, capsys):
    db = tmp_path/'t.db'
    assert main(['--db', str(db), 'upcoming', '--days', '-1']) == 2
    captured = capsys.readouterr()
    assert 'Помилка' in captured.err
    assert captured.out == ''
    assert not db.exists()


def test_cli_upcoming_non_integer(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(['--db', str(tmp_path/'t.db'), 'upcoming', '--days', 'abc'])
    assert exc.value.code == 2


def test_cli_upcoming_lists(tmp_path, capsys):
    db = str(tmp_path/'t.db')
    today = date.today()
    store = TaskStore(db)
    store.add('Inside', 'C', (today + timedelta(days=2)).isoformat())
    store.add('Outside', 'C', (today + timedelta(days=3)).isoformat())
    store.add('Past', 'C', (today - timedelta(days=1)).isoformat())
    assert main(['--db', db, 'upcoming', '--days', '2']) == 0
    out = capsys.readouterr().out
    assert 'Inside' in out
    assert 'Outside' not in out and 'Past' not in out


def test_cli_upcoming_empty(tmp_path, capsys):
    assert main(['--db', str(tmp_path/'t.db'), 'upcoming', '--days', '5']) == 0
    assert capsys.readouterr().out.strip() == 'Немає відкритих задач на найближчі 5 дн.'
