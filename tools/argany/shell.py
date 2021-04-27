#!/usr/bin/python3

import sys, re, argparse

def make_identifier(s):
    ''' Make `s` a valid shell identifier '''
    s = s.replace('-', '_')
    s = re.sub('[^a-zA-Z0-9_]', '', s)
    while '__' in s:
        s = s.replace('__', '_')
    return s.lstrip('0123456789')

def escape(s):
    ''' Shell escape `s` '''
    if re.fullmatch('[a-zA-Z0-9_,-]+', s): return s
    if "'" not in s: return "'%s'" % s
    if '"' not in s: return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')
    return "'%s'" % s.replace("'", '\'"\'"\'')

def make_subparser_identifier(s):
    return make_identifier(f'_{s}_subcommands')

def action_get_completer(action):
    if hasattr(action, 'completer'):
        return getattr(action, 'completer')

    if isinstance(action, argparse._SubParsersAction):
        pass # TODO!

    if action.choices:
        if isinstance(action.choices, (list, tuple)):
            return ('choices', action.choices)

        if isinstance(action.choices, dict):
            return ('choices', list(action.choices.keys()))

        if isinstance(action.choices, range):
            return ('int', action.choices.start, action.choices.step, action.choices.stop)

        raise Exception("Unknown type for choices: %r" % type(action.choices))

    if action.takes_args():
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

    def pid(self):
        return self.fallback('pid', 'none')

    def command(self):
        return self.fallback('command', 'file')

    def variable(self):
        return self.fallback('variable', 'none')

    def service(self):
        return self.fallback('service', 'none')

    def user(self):
        return self.fallback('user', 'none')

    def group(self):
        return self.fallback('group', 'none')

