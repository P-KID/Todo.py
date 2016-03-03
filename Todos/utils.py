# -*- coding: utf-8 -*-

import re
import emoji

from .consts import EMOJI


def _todo_from_file(line):
    _one_todo = line.split()
    idx, status, text = _one_todo[0], _one_todo[1], ' '.join(_one_todo[2:])
    idx = re.sub('\.', '', idx)
    status = re.sub('\[|\]', '', status)
    return {
        'idx': int(idx),
        'status': status,
        'text': text
    }


def _todo_to_file(todos):
    todolines = []
    for todo in todos:
        idx = todo['idx']
        status = todo['status']
        text = todo['text']
        todolines.append('{}. [{}] {}\n'.format(idx, status, text))
    return todolines


def format_show(idx, status, text):
    e = EMOJI.get(status, None)
    if e is None:
        raise
    if idx == -1:
        print emoji.emojize(' {}  {}'.format(e, text), use_aliases=True)
    else:
        print emoji.emojize('{}. {}  {}'.format(idx, e, text), use_aliases=True)
