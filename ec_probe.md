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


COMMANDS
---------

dump, read, write, monitor


SYNOPSIS
--------

`dump` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit




SYNOPSIS
--------

`read` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  ` REGISTER [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...]`
    Register source




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

Bugs to https://github.com/braph/nbfc-dev

AUTHOR
------

Benjamin Abendroth (braph93@gmx.de)

SEE ALSO
--------

nbfc(1), nbfc\_service(1), nbfc\_service.json(5), fancontrol(1)
