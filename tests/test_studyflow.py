from datetime import date

import pytest

from studyflow.storage import TaskStore


def test_validation_and_task_lifecycle(tmp_path):
    store = TaskStore(tmp_path/'tasks.db')
    with pytest.raises(ValueError): store.add(' ', 'English')
    with pytest.raises(ValueError): store.add('Read', 'English', '2026-99-99')
    first = store.add('Read chapter', 'English', '2026-11-01')
    second = store.add('Submit report', 'Data', '2026-11-20')
    assert [t.id for t in store.list(status='open')] == [first, second]
    assert [t.id for t in store.list(course='English')] == [first]
    assert store.summary(date(2026,11,4)) == {'open': 2, 'done': 0, 'overdue': 1}
    assert store.done(first)
    assert not store.done(first)
    assert store.summary(date(2026,11,4)) == {'open': 1, 'done': 1, 'overdue': 0}


def test_csv_export(tmp_path):
    store = TaskStore(tmp_path/'tasks.db')
    store.add('Task', 'Course')
    output = tmp_path/'tasks.csv'
    assert store.export_csv(output) == 1
    assert output.read_text().splitlines() == ['id,title,course,due,status', '1,Task,Course,,open']
