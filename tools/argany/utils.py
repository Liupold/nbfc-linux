#!/usr/bin/python3 -B

import argparse

def _complete(self, action, *a):
    setattr(self, 'completer', (action, *a))
    return self

argparse.Action.complete = _complete

#def get_exclusive_actions(parser, action):
#    for group in parser._mutually_exclusive_groups:
#        if action in group._actions:
#            return group._actions
#    return []

def get_exclusive_actions(self, action):
    action_conflicts = {}
    for mutex_group in self._mutually_exclusive_groups:
        group_actions = mutex_group._group_actions
        for i, mutex_action in enumerate(mutex_group._group_actions):
            conflicts = action_conflicts.setdefault(mutex_action, [])
            conflicts.extend(group_actions[:i])
            conflicts.extend(group_actions[i + 1:])
    return action_conflicts.get(action, [])

def type2str(type):
    try:
        return {
            str:    'str',
            int:    'int',
            bool:   'bool',
            float:  'float'
        }[type]
    except:
        return '%r' % type

def limit_choices(choices, n=10):
    if len(choices) > n:
        return choices[:10] + ['...']
    return choices
