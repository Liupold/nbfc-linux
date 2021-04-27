#!/usr/bin/python3 -B

import argparse, shell, utils, sys

class ZshCompleter(shell.ShellCompleter):
    def none(self):
        return "'()'"

    def file(self, glob_pattern=None):
        if not glob_pattern:
            return '_files'
        else:
            return shell.escape('_files -G '+glob_pattern)

    def directory(self, glob_pattern=None):
        if not glob_pattern:
            return '_directories'
        else:
            return shell.escape('_directories -G '+glob_pattern)

    def variable(self):
        return '_vars'

    def command(self):
        return '_command_names'

    def user(self):
        return '_users'

    def group(self):
        return '_groups'

    def signal(self):
        return '_signals'

    def hostname(self):
        return '_hosts'

    def process(self):
        return '_process_names'

    def pid(self):
        return '_pids'

    def choices(self, choices):
        return shell.escape("(%s)" % (' '.join(shell.escape(str(c)) for c in choices)))

    def int(self, *range):
        return (
            "'({{0..255}})'",
            "'({{0..{1}}})'",
            "'({{{0}..{1}}})'",
            "'({{{0}..{2}..{1}}})'"
        )[len(range)].format(*range)

_zsh_complete = ZshCompleter().complete

def _zsh_complete_action(info, p, action):
    if action.option_strings:
        argname = ''
        if action.takes_args():
            if action.metavar:
                argname = shell.escape(action.metavar)
            elif action.type is not None:
                argname = shell.escape(utils.type2str(action.type))
            else:
                argname = shell.escape(action.dest)

        return "'(%s)'%s%s:%s:%s" % (
            _zsh_get_exclusive_options(info, p, action),
            _zsh_get_optstrings_with_brace_expansion(info, action),
            shell.escape('[%s]' % action.help) if action.help else '',
            argname,
            _zsh_complete(*shell.action_get_completer(action)))
    elif isinstance(action, argparse._SubParsersAction):
        return "':command:%s'" % shell.make_subparser_identifier(p.prog)
    else:
        return ":%s:%s" % (
            shell.escape(action.help) if action.help else '',
            _zsh_complete(*shell.action_get_completer(action)))

def _zsh_get_exclusive_options(info, p, action):
    l = set(action.option_strings)
    for a in info.get_conflicting_options(action):
        l.update(a.option_strings)
    return ' '.join(sorted(l))

def _zsh_get_optstrings_with_brace_expansion(info, action):
    if action.takes_args():
        optstrings = [o+'+' if len(o) == 2 else o+'=' for o in action.option_strings]
    else:
        optstrings = action.option_strings

    if len(optstrings) == 1:
        return optstrings[0]
    else:
        return '{%s}' % ','.join(sorted(optstrings))

def _zsh_generate_subcommands_complete(info, p):
    commands = '\n    '.join(f"'{name}:{sub.get_help()}'" for name, sub in p.get_subparsers().items())

    return f'''\
{shell.make_subparser_identifier(p.prog)}() {{
  local commands=(
    {commands}
  )
  _describe -t commands '{p.prog} command' commands "$@"
}}\n\n'''

def _zsh_generate_arguments(info, p, funcname):
    args = []

    for a in p._actions:
        args.append(_zsh_complete_action(info, p, a))
    if len(p.get_subparsers()):
        args.append("'*::arg:->args'")

    if len(args):
        return '  _arguments \\\n    %s\n' % '\\\n    '.join(args)

    return ''

def _zsh_generate_parser_func(info, p, funcname):
    PS = '' # P.S. I love you

    r =  f'{funcname}() {{\n'
    r += _zsh_generate_arguments(info, p, funcname)

    subparsers = p.get_subparsers()
    if len(subparsers):
        PS += _zsh_generate_subcommands_complete(info, p)

        r += '  for w in $line; do\n'
        r += '    case $w in\n'
        for name in subparsers:
            f = shell.make_identifier(f'_{funcname}_{name}')
            PS += _zsh_generate_parser_func(info, subparsers[name], f)
            r += f'      ({name}) {f}; break;;\n'
        r += '    esac\n'
        r += '  done\n'
    r += '}\n\n'

    return r + PS

def generate_completion(p, prog=None):
    if prog is None:
        prog = p.prog

    info = utils.ArgparseInfo.create(p)
    r  = f'#compdef {prog}\n\n'
    r += _zsh_generate_parser_func(info, p, '_'+shell.make_identifier(prog)).rstrip()
    r += f'\n\n_%s "$@"' % shell.make_identifier(prog)
    return r

