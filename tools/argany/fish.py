#!/usr/bin/python3

import sys, shell, utils

class FishCompleter(shell.ShellCompleter):
    def none(self):
        return ''

    def choices(self, choices):
        return '-f -a ' + shell.escape(' '.join(shell.escape(str(c)) for c in choices))

    def file(self, glob_pattern=None):
        if glob_pattern:
            print("Warning, glob_pattern `%s' ignored\n" % glob_pattern, file=sys.stderr)
        return '-F'

    def directory(self, glob_pattern=None):
        if glob_pattern:
            return "-f -a '(__fish_complete_directories %s)'" % shell.escape(glob_pattern)
        return "-f -a '(__fish_complete_directories)'"

    def hostname(self):
        return "-f -a '(__fish_print_hostnames)'"

    def process(self):
        return "-f -a '(__fish_complete_proc)'"

    def command(self):
        return "-f -a '(__fish_complete_command)'"

    def service(self):
        return "-f -a '(__fish_systemctl_services)'"

    def variable(self):
        return "-f -a '(set -n)'"

    def user(self):
        return "-f -a '(__fish_complete_users)'"

    def pid(self):
        return "-f -a '(__fish_complete_pids)'"

    def group(self):
        return "-f -a '(__fish_complete_groups)'"

    def range(self, range):
        if range.step == 1:
            return f"-f -a '(seq {range.start} {range.stop})'"
        else:
            return f"-f -a '(seq {range.start} {range.step} {range.stop})'"


_fish_complete = FishCompleter().complete

def _fish_get_exclusive_options(info, p, action):
    l = set()
    for a in info.get_conflicting_options(action):
        l.update(a.option_strings)

    if l:
        s = ' '.join(o[2:] if o.startswith('--') else '-s '+o[1] for o in sorted(l))
        return " -n 'not __fish_contains_opt %s'" % s

    return ''

def _fish_complete_action(info, p, action, prog, subcommand=None):
    r = "complete -c %s" % shell.escape(prog)

    r += _fish_get_exclusive_options(info, p, action)

    if subcommand:
        r += f" -n '__fish_seen_subcommand_from {subcommand}'"

    if not action.option_strings:
        r += " -n 'test (__fish_number_of_cmd_args_wo_opts) = %d'" % (1+info.get_positional_index(action))
    else:
        for optstr in action.option_strings:
            if optstr.startswith('--'):
                r += " -l %s" % shell.escape(optstr[2:])
            elif optstr.startswith('-'):
                r += " -s %s" % shell.escape(optstr[1:])

    if action.help:
            r += ' -d %s' % shell.escape(action.help)

    if action.requires_args():
        r += ' -r'

    r += ' ' + _fish_complete(*shell.action_get_completer(action))

    return r.rstrip()

def _fish_generate_subcommands_complete(info, p, prog):
    r = ''
    subcommands = ' '.join(shell.escape(s) for s in p.get_subparsers().keys())
    for name, sub in p.get_subparsers().items():
      r += "complete -c %s -f -n \"not __fish_seen_subcommand_from %s\" -a %s -d %s\n" % (
        shell.escape(prog), subcommands, shell.escape(name), shell.escape(sub.get_help()))
    return r

def _fish_generate_completion(info, p, prog, subparser=None):
    r = ''
    for a in p._actions:
        r += '%s\n' % _fish_complete_action(info, p, a, prog, subparser)

    subparsers = p.get_subparsers()
    if len(subparsers):
        r += _fish_generate_subcommands_complete(info, p, prog)

        for name, sub in subparsers.items():
            r += _fish_generate_completion(info, sub, prog, name)

    return r

def generate_completion(p, prog=None):
    if prog is None:
        prog = p.prog

    info = utils.ArgparseInfo.create(p)
    return _fish_generate_completion(info, p, prog)

