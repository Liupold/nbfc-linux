#!/usr/bin/python3 -B

import utils, shell

def generate_man(p, prog=None):
    if prog is None:
        prog = p.parser.prog

    r = ''

    #if hasattr(p.parser, 'markdown_prolog'):
    #    r += p.parser.markdown_prolog

    if p.parser.description:
        r += '.SH DESCRIPTION\n'
        r += '.PP\n\n'
        r += p.parser.description + '\n'
    r += '\n'

    r += '.SH SYNOPSIS\n'
    r += '.PP\n\n'

    if p.parser.usage:
        r += p.parser.usage + '\n'
    else:
        r += f'`{prog}` [OPTIONS]\n\n'

    if p.actions:
        r += '.SH OPTIONS\n'
        r += '.PP\n\n'

    for a in p.actions:
        typ = a.type or str
        typ = utils.type2str(typ)
        r += f"  `{', '.join(a.option_strings)}"
        if a.metavar:
            r += f" {a.metavar}"
        if a.choices:
            r += ' [%s]' % ', '.join(map(str, utils.limit_choices(a.choices)))
        elif shell.action_takes_args(a) and not a.metavar:
            r += f' {typ}'
        r += '`\n'
        r += '    %s\n\n' % a.help

    if p.subparsers:
        r += '.SH COMMANDS\n'
        r += '.PP\n\n'
        r += '%s\n' % ', '.join(p.subparsers.keys())
        for name, sub in p.subparsers.items():
            sub.parser.prog = name
            r += '\n%s\n' % generate_man(sub)

    if p.parser.epilog:
        r += p.parser.epilog

    if hasattr(p.parser, 'man_epilog'):
        r += p.parser.man_epilog

    return r

