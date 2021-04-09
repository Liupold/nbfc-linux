#!/usr/bin/python3 -B

import shell

class ZshCompleter(shell.ShellCompleter):
    def none(self):
        return "'()'"

    def files(self, glob_pattern=None):
        if not glob_pattern:
            return '_files'
        else:
            return shell.escape('_files -G '+glob_pattern)

    def users(self):
        return '_users'

    def groups(self):
        return '_groups'

    def signals(self):
        return '_signals'

    def hostnames(self):
        return '_hostnames'

    def choices(self, choices):
        return shell.escape("(%s)" % (' '.join(shell.escape(str(c)) for c in choices)))

_zsh_complete = ZshCompleter().complete

def _zsh_complete_action(action):
    if action.option_strings:
        return "'(%s)'{%s}%s:%s:%s" % (
            _zsh_get_optstrings(action),
            _zsh_get_optstrings_with_brace_expansion(action),
            shell.escape('[%s]' % action.help),
            shell.escape(action.metavar if action.metavar else ''),
            _zsh_complete(*shell.action_get_completer(action)))
    else:
        return ":%s:%s" % (
            shell.escape(action.help),
            _zsh_complete(*shell.action_get_completer(action)))

def _zsh_get_optstrings(action):
    return ' '.join(action.option_strings)

def _zsh_get_optstrings_with_brace_expansion(action):
    if action.metavar:
        return ','.join(o+'+' if len(o) == 2 else o+'=' for o in action.option_strings)
    else:
        return ','.join(action.option_strings)

def _zsh_generate_subcommands_complete(p, funcname):
    commands = '\n    '.join(f"'{name}:{shell.get_help(sub)}'" for name, sub in p.subparsers.items())

    return f'''\
{funcname}() {{
  local commands; commands=(
    {commands}
  )
  _describe -t commands '{p.parser.prog} command' commands "$@"
}}\n\n'''

def _zsh_generate_parser_func(p, funcname):
    PS = '' # P.S. I love you

    r =  f'{funcname}() {{\n'
    r +=  '  _arguments \\\n'
    for a in p.actions:
        r += '    %s \\\n' % _zsh_complete_action(a)
    if p.subparsers:
        r += f"    '1:command:{funcname}_subcommands' \\\n"
        r +=  "    '*::arg:->args' \\\n"
    r = r[:-3] + '\n\n'

    if p.subparsers:
        PS += _zsh_generate_subcommands_complete(p, funcname+'_subcommands')

        r += '  case $state in\n'
        r += '    (args)\n'
        r += '      case $line[1] in\n'
        for name in p.subparsers:
            f = shell.make_identifier(f'_{funcname}_{name}')
            PS += _zsh_generate_parser_func(p.subparsers[name], f)
            r += f'        ({name}) {f};;\n'
        r += '      esac\n'
        r += '  esac\n'
    r += '}\n\n'

    return r + PS

def generate_completion(p, prog=None):
    if prog is None:
        prog = p.parser.prog

    print(f'#compdef {prog}\n')
    print(_zsh_generate_parser_func(p, '_'+prog))
    print(f'_{prog} "$@"')

