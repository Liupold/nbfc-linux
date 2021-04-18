#!/usr/bin/python3

import argparse

try:    import utils
except: argparse.Action.complete = lambda s, *_: s

argp = argparse.ArgumentParser(prog='argany-test', description='Test argument parser for shell completion')

argp.add_argument('--file',       help='Complete a file').complete('file')
argp.add_argument('--directory',  help='Complete a directory').complete('directory')
argp.add_argument('--user',       help='Complete a user').complete('user')
argp.add_argument('--group',      help='Complete a group').complete('group')
argp.add_argument('--command',    help='Complete a command').complete('command')
argp.add_argument('--process',    help='Complete a process').complete('process')
argp.add_argument('--pid',        help='Complete a pid').complete('pid')
argp.add_argument('--signal',     help='Complete a signal').complete('signal')
argp.add_argument('--hostname',   help='Complete a hostname').complete('hostname')
argp.add_argument('--choices',    help='Complete from choices', choices=(1,2,3))
argp.add_argument('-f', '--flag', help='A option flag', action='store_true')
argp.add_argument('--integer',    help='Option with integer', type=int)

grp = argp.add_mutually_exclusive_group()
grp.add_argument('--linux',   action='store_const', const='linux',   dest='os')
grp.add_argument('--windows', action='store_const', const='windows', dest='os')

subp = argp.add_subparsers(description='commands')

cmdp = subp.add_parser('dummy',        help='Dummy command')
cmdp = subp.add_parser('positionals',  help='For testing positionals')
cmdp.add_argument('pos', help='First positional')
cmdp.add_argument('opt', help='Optional positional', nargs='?')

if __name__ == '__main__':
    argp.parse_args()
