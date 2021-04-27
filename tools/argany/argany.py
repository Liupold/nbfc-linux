#!/usr/bin/python3 -B

import sys, os, argparse, importlib
import utils, zsh, bash, fish, printf, man, markdown

def find_ArgumentParser(module):
    for v in dir(module):
        if isinstance(getattr(module, v), argparse.ArgumentParser):
            return getattr(module, v)
    return None

argp = argparse.ArgumentParser('argany', 'Generate shell completions and documentation using python argparse')
argp.add_argument('action')
argp.add_argument('program')
argp.add_argument('parser_variable', nargs='?', default=None)
argp.add_argument('-o', '--output', default=None)

def generate(opts):
    directory, file = os.path.split(opts.program)
    if file.endswith('.py'):
        file = file[:-3]
    if not directory:
        directory = '.'
    if directory not in sys.path:
        sys.path.append(directory)
    module = importlib.import_module(file)

    parser = None
    try:    parser = getattr(module, opts.parser_variable)
    except: parser = find_ArgumentParser(module)

    if parser is None:
        print("Could not get ArgumentParser object from module", opts.program, file=sys.stderr)
        sys.exit(1)

    utils.add_help_to_subparsers(parser)
    actions = utils.remove_help_actions(parser)
    actions.apply()
    actions.prin()

    try:
        r = {
            'bash':     bash.generate_completion,
            'fish':     fish.generate_completion,
            'zsh':      zsh.generate_completion,
            'man':      man.generate_man,
            'printf':   printf.generate_printf_usage,
            'markdown': markdown.generate_markdown,
        }[opts.action](parser)
    finally:
        actions.restore()

    if opts.output is not None:
        with open(opts.output, 'w') as fh:
            fh.write(r)
    else:
        print(r)

commands = [[]]
for arg in sys.argv[1:]:
    if arg == ';':
        commands.append([])
    else:
        commands[-1].append(arg)
commands = [cmd for cmd in commands if len(cmd)]

exit = 0
for cmd in commands:
    opts = None
    try:
        opts = argp.parse_args(cmd)
        generate(opts)
    except Exception as e:
        print('Error:', e, file=sys.stderr)
        print('Opts:', opts, file=sys.stderr)
        raise
        exit = 1
sys.exit(exit)

