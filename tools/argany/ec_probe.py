#!/usr/bin/python3

import argparse

PROLOG = '''\
NBFC\_SERVICE 1 "MARCH 2021" Notebook FanControl
================================================

NAME
----

nbfc\_service - Notebook FanControl service

'''

argp = argparse.ArgumentParser(prog='ec_probe', description='Probing tool for embedded controllers')
argp.add_argument('-e', '--embedded-controller', help='Specify embedded controller to use',
        metavar='EC', choices=['ec_linux', 'ec_sys_linux'])
subp = argp.add_subparsers(description='commands')

cmdp = subp.add_parser('dump',        help='Dump all EC registers')

cmdp = subp.add_parser('read',        help='Read a byte from a EC register')
cmdp.add_argument('register',         type=int, metavar='REGISTER', help='Register source',      choices=list(range(0, 255)))

cmdp = subp.add_parser('write',       help='Write a byte to a EC register')
cmdp.add_argument('register',         type=int, metavar='REGISTER', help='Register destination', choices=list(range(0, 255)))
cmdp.add_argument('value',            type=int, metavar='VALUE',    help='Value to write',       choices=list(range(0, 255)))

cmdp = subp.add_parser('monitor',     help='Monitor all EC registers for changes')
cmdp.add_argument('-i', '--interval', help='Monitored timespan', metavar='seconds', type=int)
cmdp.add_argument('-t', '--timespan', help='Set poll intervall', metavar='seconds', type=int)
cmdp.add_argument('-r', '--report',   help='Save all readings as a CSV file')
cmdp.add_argument('-c', '--clearly',  help='Blanks out consecutive duplicate readings', action='store_true')
cmdp.add_argument('-d', '--decimal',  help='Output readings in decimal format instead of hexadecimal format', action='store_true')

argp.epilog = '''
All input values are interpreted as decimal numbers by default.
Hexadecimal values may be entered by prefixing them with "0x".
'''

argp.markdown_prolog = PROLOG
argp.markdown_epilog = '''
FILES
-----

*/var/run/nbfc_service.pid*
  File containing the PID of current running nbfc\_service.

*/var/run/nbfc_service.state.json*
  State file of nbfc\_service. Updated every *EcPollInterval* miliseconds See nbfc\_service.json(5) for further details.

*/etc/nbfc/configs/\*.json*
  Configuration files for various notebook models. See nbfc\_service.json(5) for further details.

EXIT STATUS
-----------

   - 0    Everything fine
   - 1    Generic error
   - 2    Command line error
   - 3    Initialization error
   - 5    Fatal error

BUGS
----

Bugs to https://github.com/braph/nbfc-linux

AUTHOR
------

Benjamin Abendroth (braph93@gmx.de)

SEE ALSO
--------

nbfc(1), nbfc\_service(1), nbfc\_service.json(5), fancontrol(1)'''

