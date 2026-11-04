import argparse
import sys
from pathlib import Path

from .storage import TaskStore
from .upcoming import upcoming, validate_days


def parser():
    p = argparse.ArgumentParser(prog='studyflow', description='Локальні навчальні задачі')
    p.add_argument('--db', default=str(Path.home()/'.studyflow/tasks.db'))
    sub = p.add_subparsers(dest='command', required=True)
    add = sub.add_parser('add'); add.add_argument('title'); add.add_argument('--course', required=True); add.add_argument('--due')
    ls = sub.add_parser('list'); ls.add_argument('--course'); ls.add_argument('--status', choices=['open','done'])
    done = sub.add_parser('done'); done.add_argument('id', type=int)
    sub.add_parser('summary')
    export = sub.add_parser('export'); export.add_argument('path')
    up = sub.add_parser('upcoming'); up.add_argument('--days', type=int, required=True)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'upcoming':
            validate_days(args.days)
        store = TaskStore(args.db)
        if args.command == 'add':
            print(f'Створено задачу #{store.add(args.title, args.course, args.due)}')
        elif args.command == 'list':
            for task in store.list(args.course, args.status):
                print(f'{task.id}\t{task.status}\t{task.course}\t{task.due or "—"}\t{task.title}')
        elif args.command == 'done':
            if not store.done(args.id):
                raise ValueError(f'Відкриту задачу #{args.id} не знайдено')
            print(f'Задачу #{args.id} завершено')
        elif args.command == 'summary':
            data = store.summary()
            print(f'Відкриті: {data["open"]}; завершені: {data["done"]}; прострочені: {data["overdue"]}')
        elif args.command == 'export':
            print(f'Експортовано {store.export_csv(args.path)} задач у {args.path}')
        elif args.command == 'upcoming':
            tasks = upcoming(store, args.days)
            for task in tasks:
                print(f'{task.id}\t{task.status}\t{task.course}\t{task.due}\t{task.title}')
            if not tasks:
                print(f'Немає відкритих задач на найближчі {args.days} дн.')
        return 0
    except (ValueError, OSError) as exc:
        print(f'Помилка: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
