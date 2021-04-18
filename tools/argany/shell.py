#!/usr/bin/python3

import sys, re, argparse

def make_identifier(s):
    ''' Make `s` a valid shell identifier '''
    s = s.replace('-', '_')
    s = re.sub('[^a-zA-Z0-9_]', '', s)
    while '__' in s:
        s = s.replace('__', '_')
    while s[0] in '0123456789':
        s = s[1:]
    return s

def escape(s):
    ''' Shell escape `s` '''
    if re.fullmatch('[a-zA-Z0-9_-]+', s): return s
    if "'" not in s: return "'"+s+"'"
    if '"' not in s: return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')
    return "'%s'" % s.replace("'", '\'"\'"\'')

def get_help(o):
    if isinstance(o, argparse.ArgumentParser):
        try:    return getattr(o, 'help')
        except: return o.description
    else: return get_help(o.parser)

def action_takes_args(action):
    try:    return action.nargs in '?+*'
    except: return action.nargs != 0
    #return isinstance(action, argparse.BooleanOptionalAction)

def action_requires_args(action):
    if action.nargs: # nargs takes precedence
        return action.nargs == '+' or (action.nargs.isdigit() and int(action.nargs))

    # Check by action
    return isinstance(action, (
        argparse._StoreAction,
        argparse._AppendAction,
        argparse._ExtendAction) )

def action_get_completer(action):
    if hasattr(action, 'completer'):
        return getattr(action, 'completer')

    if action.choices:
        if isinstance(action.choices, (list, tuple)):
            return ('choices', action.choices)

        if isinstance(action.choices, dict):
            return ('choices', list(action.choices.keys()))

        raise Exception("Unknown type for choices: %r" % type(action.choices))

    if action_takes_args(action):
        if action.type is int:
            return ('int',)
        return ('files',)

    return ('none',)

class ShellCompleter:
    def complete(self, completer, *a, **kw):
        if not hasattr(self, completer):
            print("Warning: ShellCompleter: Falling back from `%s` to `none`" % (completer,), file=sys.stderr)
            completer = 'none'

        return getattr(self, completer)(*a, **kw)

    def fallback(self, from_, to, *a, **kw):
        print("Warning: ShellCompleter: Falling back from `%s` to `%s`" % (from_, to), file=sys.stderr)
        return self.complete(to, *a, **kw)

    def none(self):
        return ''

    def signal(self):
        return self.fallback('signal', 'choices', ['SIGINT', 'SIGTERM', 'SIGKILL'])

    def int(self, *_range):
        if not _range: _range = (20,)
        return self.fallback('int', 'choices', list(range(*_range)[0:20]) + ['...'])

    def directory(self, glob_pattern=None):
        return self.fallback('directory', 'file', glob_pattern)

    def process(self):
        return self.fallback('process', 'none')

    def command(self):
        return self.fallback('command', 'file')

    def user(self):
        return self.fallback('user', 'none')

    def group(self):
        return self.fallback('group', 'none')

