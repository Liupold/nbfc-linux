NBFC\_SERVICE 1 "MARCH 2021" Notebook FanControl
================================================

NAME
----

nbfc\_service - Notebook FanControl service

DESCRIPTION
-----------

NoteBook FanControl CLI Client

SYNOPSIS
--------

`nbfc` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit


COMMANDS
---------

start, stop, restart, status, config, set, help


SYNOPSIS
--------

`start` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-e, --enabled`
    Start in enabled mode (default)

  `-r, --readonly`
    Start in read-only mode




SYNOPSIS
--------

`stop` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit




SYNOPSIS
--------

`restart` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-e, --enabled`
    Restart in enabled mode (default)

  `-r, --readonly`
    Restart in read-only mode




SYNOPSIS
--------

`status` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-a, --all`
    Show service and fan status (default)

  `-s, --service`
    Show service status

  `-f, --fan FAN INDEX`
    Show fan status

  `-w, --watch SECONDS`
    Show status periodically




SYNOPSIS
--------

`config` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-l, --list`
    List all available configs (default)

  `-s, --set config`
    Set a config

  `-a, --apply config`
    Set a config and enable fan control

  `-r, --recommend`
    List configs which may work for your device




SYNOPSIS
--------

`set` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit

  `-a, --auto`
    Set fan speed to 'auto'

  `-s, --speed PERCENT`
    Set fan speed to <value>

  `-f, --fan FAN INDEX`
    Fan index (zero based)




SYNOPSIS
--------

`help` [OPTIONS]

OPTIONS
-------

  `-h, --help`
    show this help message and exit



FILES
-----

*/var/run/nbfc_service.pid*
  File containing the PID of current running nbfc\_service.

*/var/run/nbfc_service.state.json*
  State file of nbfc\_service. Updated every *EcPollInterval* miliseconds See nbfc\_service.json(5) for further details.

*/etc/nbfc/nbfc.json*
  The system wide configuration file. See nbfc\_service.json(5) for further details.

*/etc/nbfc/configs/\*.json*
  Configuration files for various notebook models. See nbfc\_service.json(5) for further details.

BUGS
----

Bugs to https://github.com/braph/nbfc-linux

AUTHOR
------

Benjamin Abendroth (braph93@gmx.de)

SEE ALSO
--------

nbfc_service(1), nbfc\_service.json(5), ec_probe(1), fancontrol(1)
