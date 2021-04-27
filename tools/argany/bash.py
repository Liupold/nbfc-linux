#!/usr/bin/python3

import shell, utils
# $split && return
#_filedir '@(?(d)patch|dif?(f))'

def compgen(args, word='"$cur"'):
    return '$(compgen %s -- %s)' % (args, word)

class BashCompleter(shell.ShellCompleter):
    def file(self, glob_pattern=None):
        if not glob_pattern:
            return compgen('-f')
        else:
            return compgen('-G ' + shell.escape(glob_pattern))

    def directory(self, glob_pattern=None):
        if not glob_pattern:
            return compgen('-d')
        else:
            return compgen('-G ' + shell.escape(glob_pattern))

    def user(self):
        return compgen('-A user')

    def group(self):
        return compgen('-A group')

    def process(self):
        return '_pnames #direct'

    def pid(self):
        return '_pids #direct'

    def signal(self):
        return compgen('-A signal')

    def service(self):
        return compgen('-A service')

    def variable(self):
        return compgen('-A variable')

    def command(self):
        return compgen('-A command')

    def hostname(self):
        return compgen('-A hostname')

    def choices(self, choices):
        return compgen('-W '+ shell.escape(' '.join(shell.escape(str(c)) for c in choices)))

    def int(self, *range):
        return compgen((
            "-W '{{0..255}}'",
            "-W '{{0..{1}}}'",
            "-W '{{{0}..{1}}}'",
            "-W '{{{0}..{2}..{1}}}'"
        )[len(range)].format(*range))

_bash_complete = BashCompleter().complete

def _bash_complete_action(action, append=True):
    r = _bash_complete(*shell.action_get_completer(action))
    if r.endswith('#direct'):
        return r[0:-len('#direct')].rstrip()
    return 'COMPREPLY%s=(%s)' % (('+' if append else ''), r)

def _bash_case_option_strings(action):
    return '|'.join(map(shell.escape, sorted(action.option_strings)))

def _bash_complete_parser(info, p, funcname, parent_parsers=[]):
    funcname = shell.make_identifier(funcname)

    options     = p.get_options()
    positionals = p.get_positionals()
    subparsers  = p.get_subparsers()

    r  = f'{funcname}() {{\n'

    if len(parent_parsers) == 0:
        r += '  local cur prev words cword split args w\n'
        r += '  _init_completion -s || return\n'
        r += '\n'

        if len(positionals):
            option_strings, short_opts, long_opts = [], [], []
            for a in p._actions:
                if a.option_strings and a.takes_args():
                    option_strings.extend(a.option_strings)
                    for o in a.option_strings:
                        if o.startswith('--'):  long_opts.append(o[2:])
                        elif o.startswith('-'): short_opts.append(o[1:])


            exclude_pattern = ''
            if len(short_opts) and len(long_opts):
                exclude_pattern = "-@([%s]|-@(%s))" % (
                    ''.join(sorted(short_opts)), '|'.join(sorted(long_opts)))
            elif len(short_opts):
                exclude_pattern = "-@([%s])" % ''.join(sorted(short_opts))
            elif len(long_opts):
                exclude_pattern = "--@(%s)" % '|'.join(sorted(long_opts))

            r += '  _count_args "" "%s"\n' % exclude_pattern

    if len(subparsers):
        r += '  for w in "${COMP_WORDS[@]}"; do\n'
        r += '    case "$w" in\n'
        for name in subparsers.keys():
            f = shell.make_identifier('_%s_%s' % (p.prog, name))
            r += '      %s) %s && return 0;;\n' % (shell.escape(name), f)
        r += '    esac\n'
        r += '  done\n'
        r += '\n'

    if len(options):
        s = ''
        for a in options:
            if a.takes_args():
                s += '    %s)\n' % _bash_case_option_strings(a)
                s += '       %s;\n'  %_bash_complete_action(a, append=False)
                s += '       return 0;;\n'
        if s:
            r += '  case "$prev" in\n'
            r += s
            r += '  esac\n'
            r += '\n'

    r += '  if [[ "$cur" = -* ]]; then\n'
    r += '    COMPREPLY+=(%s)\n' % _bash_complete('choices', p.get_all_optstrings())
    r += '  fi\n'
    r += '\n'

    if len(positionals):
        r += '  case $args in\n'
        for a in positionals:
            r += '    %d)\n' % (info.get_positional_index(a) + 1)
            r += '       %s;\n' % _bash_complete_action(a)
            r += '       return 0;;\n'
        r += '  esac\n'
        r += '\n'

    r += '  return 1\n'
    r += '}\n\n'

    for name, sub in subparsers.items():
        f = shell.make_identifier('_%s_%s' % (p.prog, name))
        r += _bash_complete_parser(info, sub, f, parent_parsers+[p])

    return r

def generate_completion(p, prog=None):
    if prog is None:
        prog = p.prog

    info = utils.ArgparseInfo.create(p)
    funcname = shell.make_identifier('_'+prog)
    r  = '#!/bin/bash\n\n'
    r += _bash_complete_parser(info, p, funcname).rstrip()
    r += '\n\n'
    r += 'complete -F %s %s' % (funcname, prog)
    return r
