NBFC\_SERVICE 1 "MARCH 2021" Notebook FanControl
================================================

NAME
----

nbfc\_service - Notebook FanControl service

DESCRIPTION
-----------

Probing tool for embedded controllers

SYNOPSIS
--------

`ec_probe` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-e, --embedded-controller EC [ec_linux, ec_sys_linux]`
    Specify embedded controller to use

  ` [dump, read, write, monitor]`
    None


COMMANDS
---------

dump, read, write, monitor

DESCRIPTION
-----------

Dump all EC registers

SYNOPSIS
--------

`dump` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit



DESCRIPTION
-----------

Read a byte from a EC register

SYNOPSIS
--------

`read` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  ` REGISTER [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...]`
    Register source



DESCRIPTION
-----------

Write a byte to a EC register

SYNOPSIS
--------

`write` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  ` REGISTER [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...]`
    Register destination

  ` VALUE [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...]`
    Value to write



DESCRIPTION
-----------

Monitor all EC registers for changes

SYNOPSIS
--------

`monitor` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-i, --interval seconds`
    Monitored timespan

  `-t, --timespan seconds`
    Set poll intervall

  `-r, --report str`
    Save all readings as a CSV file

  `-c, --clearly`
    Blanks out consecutive duplicate readings

  `-d, --decimal`
    Output readings in decimal format instead of hexadecimal format



All input values are interpreted as decimal numbers by default.
Hexadecimal values may be entered by prefixing them with "0x".
