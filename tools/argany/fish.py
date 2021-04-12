#!/usr/bin/python3 -B

import shell

class FishCompleter(shell.ShellCompleter):
    def none(self):
        return ''

    def choices(self, choices):
        return shell.escape("%s" % (' '.join(shell.escape(str(c)) for c in choices)))

_fish_complete = FishCompleter().complete

def _fish_complete_action(action, prog, subcommand=None):
    r = "complete -c %s" % shell.escape(prog)

    if subcommand:
        r += f" -n '__fish_seen_subcommand_from {subcommand}'"

    for optstr in action.option_strings:
        if optstr.startswith('--'):
            r += " -l %s" % shell.escape(optstr[2:])
        else:
            r += " -s %s" % shell.escape(optstr[1:])

    if action.help:
            r += ' -d %s' % shell.escape(action.help)

    if shell.action_requires_args(action):
        r += ' -r'
            
    comp_action =_fish_complete(*shell.action_get_completer(action))
    if comp_action:
        r += ' -f -a %s' % comp_action

    return r

def _fish_generate_subcommands_complete(p, prog):
    r = ''
    subcommands = ' '.join(shell.escape(s) for s in p.subparsers.keys())
    for name, sub in p.subparsers.items():
      r += "complete -c %s -f -n \"not __fish_seen_subcommand_from %s\" -a %s -d %s\n" % (
        shell.escape(prog), subcommands, shell.escape(name), shell.escape(shell.get_help(sub)))
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

    return _fish_generate_parser_func(p, prog)

