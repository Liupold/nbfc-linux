#!/usr/bin/python3 -B

import shell

class BashCompleter(shell.ShellCompleter):
    def files(self, glob_pattern=None):
        if not glob_pattern:
            return '$(compgen -f -- $cur)'
        else:
            return '$(compgen -G %s -- $cur)' % shell.escape(glob_pattern)

    def users(self):
        return '$(compgen -A user -- $cur)'

    def groups(self):
        return '$(compgen -A group -- $cur)'

    def signals(self):
        return '$(compgen -A signal -- $cur)'

    def hostnames(self):
        return '$(compgen -A hostname -- $cur)'

    def choices(self, choices):
        return '$(compgen -W %s -- $cur)' % (
            shell.escape(' '.join(shell.escape(str(c)) for c in choices)))

_bash_complete = BashCompleter().complete

def _bash_complete_action(action):
    r = ''
    if action.option_strings:
        r += '    %s)\n' % ') ;& '.join(map(shell.escape, action.option_strings))
        r += '      COMPREPLY+=(%s);;\n' % _bash_complete(*shell.action_get_completer(action))
    return r

def _bash_complete_parser(p, funcname, root_parser=True):
    funcname = shell.make_identifier(funcname)

    r  = f'{funcname}() {{\n'
    if root_parser:
        r += '  COMPREPLY=();\n'
    r += _bash_complete_subcommand(p)
    r += '  local cur=${COMP_WORDS[COMP_CWORD]}\n'
    r += '  local prev=${COMP_WORDS[COMP_CWORD - 1]}\n'
    r += '\n'
    r += '  case "$prev" in\n'
    for a in p.actions:
        r += _bash_complete_action(a)
    r += '  esac\n'
    r += '\n'
    r += '  COMPREPLY+=(%s)\n' % _bash_complete('choices', p.yield_all_option_strings())
    r += '}\n\n'
    return r

def _bash_complete_subcommand(p):
    if not p.subparsers:
        return ''

    r  = '  local arg0=${COMP_WORDS[1]}\n'
    r += '  case "$arg0" in\n'
    for name, subparser in p.subparsers.items():
        funcname = shell.make_identifier('_%s_%s' % (p.parser.prog, name))
        r += f'    {name}) {funcname};;\n'
    r += '    *) COMPREPLY+=(%s);;\n' % _bash_complete('choices', p.subparsers.keys())
    r += '  esac\n\n'
    return r

def generate_completion(p, prog=None):
    if prog is None:
        prog = p.parser.prog

    r  = '#!/bin/bash\n\n'
    r += _bash_complete_parser(p, '_'+prog)

    for name, sub in p.subparsers.items():
        r += _bash_complete_parser(sub, '_%s_%s' % (prog, name), False)

    r += 'complete -F _%s %s' % (prog, prog)
    print(r)

