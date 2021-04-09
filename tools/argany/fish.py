#!/usr/bin/python3 -B

import shell

class FishCompleter(shell.ShellCompleter):
    def none(self):
        return ''

    def choices(self, choices):
        return shell.escape("%s" % (' '.join(shell.escape(str(c)) for c in choices)))

_fish_complete = FishCompleter().complete

def _fish_complete_action(action, prog, subcommand=None):
    r = f"complete -c '{prog}'"

    if subcommand:
        r += f" -n '__fish_seen_subcommand_from {subcommand}'"

    for optstr in action.option_strings:
        if optstr.startswith('--'):
            r += " -l '%s'" % optstr[2:]
        else:
            r += " -s '%s'" % optstr[1:]

    if action.help:
            r += ' -d %s' % shell.escape(action.help)

    if shell.action_requires_args(action):
        r += ' -r'
            
    comp_action =_fish_complete(*shell.action_get_completer(action))
    if comp_action:
        r += ' -a %s' % comp_action

    return r

def _fish_generate_subcommands_complete(p, prog):
    r = f'set -l {prog}_cmds %s\n' % ' '.join(shell.escape(s) for s in p.subparsers.keys())
    for name, sub in p.subparsers.items():
      r += f"complete -f -c '{prog}' -n \"not __fish_seen_subcommand_from ${prog}_cmds\" -a {name} -d {shell.escape(shell.get_help(sub))}\n"
    return r

def _fish_generate_parser_func(p, prog, subparser=None):
    r = ''
    for a in p.actions:
        r += '%s\n' % _fish_complete_action(a, prog, subparser)

    if p.subparsers:
        r += _fish_generate_subcommands_complete(p, prog)

        for name, sub in p.subparsers.items():
            r += _fish_generate_parser_func(sub, prog, name)

    return r

def generate_completion(p, prog=None):
    if prog is None:
        prog = p.parser.prog

    print(_fish_generate_parser_func(p, prog))

