#!/usr/bin/python3 -B

import argparse, re
import zsh, bash, fish

# =============================================================================
# Utils =======================================================================
# =============================================================================

def RemoveHelpActions(p):
    # TODO: This isn't working?!
    def is_help_action(o):
        return type(o) is argparse._HelpAction

    memoized = {}

    def replace_help_object(o):
        if id(o) in memoized:
            return memoized[id(o)]
        memoized[id(o)] = o

        if type(o) is list:
            memoized[id(o)] = new = list()
            memoized[id(new)] = new
            for e in o:
                if not is_help_action(e):
                    new.append(replace_help_object(e))
            return new
        elif type(o) is dict:
            memoized[id(o)] = new = dict()
            memoized[id(new)] = new
            for k, v in o.items():
                if not is_help_action(v):
                    new[k] = replace_help_object(v)
            return new
        else:
            try:
                for k in list(o.__dict__.keys()):
                    try:
                        o.__dict__[k] = replace_help_object(o.__dict__[k])
                    except:
                        pass
            except:
                pass
            return o

    p.parser = replace_help_object(p.parser)
    return p

def action_takes_args(action):
    try:    return action.nargs in '?+*'
    except: return action.nargs != 0

def limit_choices(choices, n=10):
    if len(choices) > n:
        return choices[:10] + ['...']
    return choices

class Parser:
    __slots__ = ('parser', 'actions', 'subparsers')
    def __init__(self, parser):
        self.parser     = parser
        self.actions    = []
        self.subparsers = {}

    def __repr__(self):
        return "[\n\t%s,\n\t%s,\n\t%s\n]" % (self.parser, self.actions, self.subparsers)

    def yield_all_option_strings(self):
        for a in self.actions:
            for o in a.option_strings:
                yield o


    @staticmethod
    def from_ArgumentParser(parser):
        r = Parser(parser)

        for a in parser._actions:
            if isinstance(a, argparse._SubParsersAction):
                i = 0
                for name, subparser in a.choices.items():
                    sub = Parser.from_ArgumentParser(subparser)
                    sub.parser.help = a._get_subactions()[i].help
                    r.subparsers[name] = sub
                    i += 1
            else:
                r.actions.append(a)

        return r

def type2str(type):
    return {
        str:    'str',
        int:    'int',
        bool:   'bool',
        float:  'float'
    }[type]

def generate_markdown(p, prog=None):
    if prog is None:
        prog = p.parser.prog

    r = ''

    if hasattr(p.parser, 'markdown_prolog'):
        r += p.parser.markdown_prolog

    if p.parser.description:
        r += 'DESCRIPTION\n'
        r += '-----------\n\n'
        r += p.parser.description + '\n'
    r += '\n'

    r += 'SYNOPSIS\n'
    r += '--------\n\n'

    if p.parser.usage:
        r += p.parser.usage + '\n'
    else:
        r += f'`{prog}` [OPTIONS]\n\n'

    if p.actions:
        r += 'OPTIONS\n'
        r += '-------\n\n'

    for a in p.actions:
        typ = a.type or str
        typ = type2str(typ)
        r += f"  `{', '.join(a.option_strings)}"
        if a.metavar:
            r += f" {a.metavar}"
        if a.choices:
            r += ' [%s]' % ', '.join(map(str, limit_choices(a.choices)))
        elif action_takes_args(a) and not a.metavar:
            r += f' {typ}'
        r += '`\n'
        r += '    %s\n\n' % a.help

    if p.subparsers:
        r += '\nCOMMANDS\n'
        r += '---------\n\n'
        r += '%s\n' % ', '.join(p.subparsers.keys())
        for name, sub in p.subparsers.items():
            sub.parser.prog = name
            r += '\n%s\n' % generate_markdown(sub)

    if p.parser.epilog:
        r += p.parser.epilog

    if hasattr(p.parser, 'markdown_epilog'):
        r += p.parser.markdown_epilog

    return r

def c_identifier(s):
    s = s.replace('-', '_')
    s = re.sub('[^a-zA-Z0-9_]', '', s)
    s = s.replace('__', '_')
    s = s.replace('__', '_')
    return s

def str_to_c(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = '"' + s.replace('\n', '\\n"\n"') + '"'
    return s

def define_macro(name, value):
    return '#define %s %s' % (name, value.replace('\n', '\\\n '))

def generate_printf_usage(p, macro=None, prog='%s'):
    if prog is None:
        prog = p.parser.prog

    r = ''

    if macro is None:
        macro = c_identifier(p.parser.prog).upper() + '_HELP_TEXT'

    p.parser.prog = '$$$ PROG $$$'
    help = p.parser.format_help()
    help = str_to_c(help)
    help = help.replace('%', '%%')
    help = help.replace('$$$ PROG $$$', prog)
    r += '%s\n' % define_macro(macro, help)

    if p.subparsers:
        for name, sub in p.subparsers.items():
            sub.parser.prog = name
            r += '%s\n' % generate_printf_usage(sub, None, '%s '+name)

    return r

def find_ArgumentParser(module):
    for v in dir(module):
        if isinstance(getattr(module, v), argparse.ArgumentParser):
            return getattr(module, v)
    return None

if __name__ == '__main__':
    import sys, os, importlib

    arg0       = sys.argv.pop(0)
    action     = sys.argv.pop(0)
    program    = sys.argv.pop(0)
    parser_obj = None
    try:    parser_obj = sys.argv.pop(0)
    except: pass

    directory, file = os.path.split(program)
    if file.endswith('.py'):
        file = file[:-3]
    if not directory:
        directory = '.'
    sys.path.append(directory)
    module = importlib.import_module(file)

    if parser_obj:
        argp = getattr(module, parser_obj)
    else:
        argp = find_ArgumentParser(module)

    if not argp:
        print("Could not get ArgumentParser object from module", program, file=sys.stderr)
        sys.exit(1)

    p = Parser.from_ArgumentParser(argp)
    RemoveHelpActions(p)

    r = {
        'bash':     bash.generate_completion,
        'fish':     fish.generate_completion,
        'zsh':      zsh.generate_completion,
        'printf':   generate_printf_usage,
        'markdown': generate_markdown
    }[action](p)
    print(r)

