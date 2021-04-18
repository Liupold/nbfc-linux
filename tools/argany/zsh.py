#!/usr/bin/python3 -B

import shell, utils

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

_zsh_complete = ZshCompleter().complete

def _zsh_complete_action(p, action):
    if action.option_strings:
        argname = ''
        if shell.action_takes_args(action):
            if action.metavar:
                argname = shell.escape(action.metavar)
            elif action.type is not None:
                argname = shell.escape(utils.type2str(action.type))
            else:
                argname = shell.escape(action.dest)

        return "'(%s)'%s%s:%s:%s" % (
            _zsh_get_exclusive_options(p, action),
            _zsh_get_optstrings_with_brace_expansion(action),
            shell.escape('[%s]' % action.help),
            argname,
            _zsh_complete(*shell.action_get_completer(action)))
    else:
        return ":%s:%s" % (
            shell.escape(action.help),
            _zsh_complete(*shell.action_get_completer(action)))

def _zsh_get_exclusive_options(p, action):
    l = set(action.option_strings)
    for a in utils.get_exclusive_actions(p.parser, action):
        l.add(*a.option_strings)
    return ' '.join(l)

def _zsh_get_optstrings_with_brace_expansion(action):
    if shell.action_takes_args(action):
        optstrings = [o+'+' if len(o) == 2 else o+'=' for o in action.option_strings]
    else:
        optstrings = action.option_strings

    if len(optstrings) == 1:
        return optstrings[0]
    else:
        return '{%s}' % ','.join(optstrings)

def _zsh_generate_subcommands_complete(p, funcname):
    commands = '\n    '.join(f"'{name}:{shell.get_help(sub)}'" for name, sub in p.subparsers.items())

    return f'''\
{funcname}() {{
  local commands; commands=(
    {commands}
  )
  _describe -t commands '{p.parser.prog} command' commands "$@"
}}\n\n'''

def _zsh_generate_arguments(p, funcname):
    r =  '  _arguments \\\n'
    for a in p.actions:
        r += '    %s \\\n' % _zsh_complete_action(p, a)
    if p.subparsers:
        r += f"    '1:command:{funcname}_subcommands' \\\n"
        r +=  "    '*::arg:->args' \\\n"
    r = r[:-3] + '\n\n'
    return r

def _zsh_generate_parser_func(p, funcname):
    PS = '' # P.S. I love you

    r =  f'{funcname}() {{\n'
    r += _zsh_generate_arguments(p, funcname)

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

    r  = f'#compdef {prog}\n\n'
    r += _zsh_generate_parser_func(p, '_'+prog)
    r += f'\n_{prog} "$@"'
    return r

