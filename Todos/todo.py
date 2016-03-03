# -*- coding: utf-8 -*-

import os
import click
import logging

from .log import setup_logging
from .exc import (
    InvalidTodoFile,
    InvalidTodoStatus
)
from .utils import(
    _todo_from_file,
    format_show,
    _todo_to_file
)
from .consts import (
    WAITING,
    COMPLETE,
    STATUS_CODE,
    NO_TODOS_SHOW
)

logger = logging.getLogger(__name__)


class Todo(object):

    def __init__(self, todo_dir='.', name='Todos.txt'):
        """Todo Base Class
        :param todo_dir: file path to store todos
        :param name: file name

        e.g. ..code python
            t = Todo()
            t.add_todo('contents', status)
            t.show_all_todos()
            t.write()
        """
        self.todos = []
        self.name = name
        self.todo_dir = todo_dir
        self.path = os.path.join(os.path.expanduser(self.todo_dir), name)
        self.current_max_idx = 0
        self.init()

    def __getitem__(self, idx):
        self._show_todos(idx=idx)

    def init(self):
        """init `todo` file
        if file exists, then initialization self.todos
        and record current max index of todos
        : when add a new todo, the `idx` via only `self.current_max_idx + 1`
        """
        if os.path.isdir(self.path):
            raise InvalidTodoFile
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                tls = [tl.strip() for tl in f if tl]
                todos = map(_todo_from_file, tls)
                self.todos = todos
                for todo in todos:
                    if self.current_max_idx< todo['idx']:
                        self.current_max_idx = todo['idx']
        else:
            logger.warning('No todo files found, initialization a empty todo file')
            with open(self.path, 'w') as f:
                f.flush()

    def add_todo(self, text, status=WAITING):
        idx = self.current_max_idx + 1
        self.todos.append({
            'idx': idx,
            'status': status,
            'text': text
        })

    def edit_todo(self, idx, text):
        pass

    def finish_todo(self, idxs):
        for idx in idxs:
            for todo in self.todos:
                if todo['idx'] == int(idx):
                    todo['status'] = COMPLETE

    def remove_todo(self, idx):
        pass

    def clear_all(self):
        """clear todos
        """
        confirm = raw_input('confirm ? (Y/N): ')
        if confirm in ['Y', 'y']:
            self.todos = []

    def _show_todos(self, status=None, idx=None):
        """show todos after format
        :param status: what status's todos wants to show.
        default is None, means show all
        """
        if not self.todos:
            format_show(
                NO_TODOS_SHOW[0],
                NO_TODOS_SHOW[1],
                NO_TODOS_SHOW[2])
        elif idx is not None:
            for todo in self.todos:
                if todo['idx'] == idx:
                    format_show(todo['idx'], todo['status'], todo['text'])
        elif status is not None:
            if status not in STATUS_CODE:
                raise InvalidTodoStatus
            for todo in self.todos:
                if todo['status'] == status:
                    format_show(todo['idx'], todo['status'], todo['text'])
        else:
            for todo in self.todos:
                format_show(todo['idx'], todo['status'], todo['text'])

    def show_waiting_todos(self):
        self._show_todos(status=WAITING)

    def show_done_todos(self):
        self._show_todos(status=COMPLETE)

    def show_all_todos(self):
        self._show_todos()

    def write(self, delete_if_empty=False):
        """flush todos to file
        :param delete_if_empty: delete if todo is empty
        """
        with open(self.path, 'w') as f:
            if not self.todos:
                f.flush()
            else:
                for todo in _todo_to_file(self.todos):
                    f.write(todo)


def check_complete_ids(ctx, param, value):
    if not value:
        return []
    return value.split(',')


@click.command()
@click.version_option()
@click.option('-n', '--new', help='new todo')
@click.option('-c', '--complete_ids', type=str, callback=check_complete_ids,
              help='complete todo by id(s)'
                    ' - usage: todos -c 1,2')
@click.option('--all', is_flag=True, default=False,
              help='show all todos')
@click.option('--clear', is_flag=True, default=False,
              help='clear all todos, need confirm!!')
def todos(new, complete_ids, all, clear):
    setup_logging()
    t = Todo()
    try:
        if clear:
            t.clear_all()
            return
        if new:
            t.add_todo(new)
        elif complete_ids:
            t.finish_todo(complete_ids)
        else:
            if all:
                t.show_all_todos()
            else:
                t.show_waiting_todos()
    except Exception as e:
        logger.error(e)
    finally:
        t.write()
