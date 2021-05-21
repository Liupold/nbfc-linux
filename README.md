NoteBook FanControl
===================

This is a C port of [Stefan Hirschmann's](https://github.com/hirschmann) [NoteBook FanControl](https://github.com/hirschmann/nbfc).

It provides the same utilities with the same interfaces as the original NBFC, although the implementation differs.

Comparison of NBFC C# and NBFC Linux
------------------------------------

|What                             | NBFC Mono                             | NBFC Linux                                  |
|---------------------------------|---------------------------------------|----------------------------------------------
|Portability                      | Crossplatform                         | Linux                                       |
|Configuration files              | XML (956KB)                           | [JSON](etc/nbfc/configs) (840KB)            |
|Runtime                          | Mono                                  | Native                                      |
|Memory consumption (ps\_mem)     | ~50MB                                 | ~350KB                                      |
|Package size (pkg.tar.gz)        | 448K	                                | 100K                                        |
|Service control rights           | Any user                              | Only root                                   |
|IPC Concept                      | TCP/IP                                | Files                                       |
|IPC Protocol                     | Binary                                | JSON                                        |

The [service](doc/nbfc_service.md) and the [probing tool](doc/ec_probe.md) are written in C.
The [client](doc/nbfc.md) is written in Python.

Installation
------------

- Arch Linux:
  - Either via AUR (`yaourt -S nbfc-linux`)
  - Or by using one of the PKGBUILDs [nbfc-linux-git](pkgbuilds/nbfc-linux-git/PKGBUILD) / [nbfc-linux](pkgbuilds/nbfc-linux/PKGBUILD)

- In general:
  - `make && sudo make install`

Getting started
---------------

When running NBFC for the first time, you need to give it a configuration file for your laptop model.

If you are lucky, `sudo nbfc config --set auto` will find a matching one and set it.

`sudo nbfc config --recommend` (required `dmidecode`) will give a list of configuration files that may match your laptop.

With `sudo nbfc config --set <MODEL>` a configuration is selected.

`sudo nbfc start` will start the service.

It can be queried by `sudo nbfc status -a`.

If you wish `nbfc_service` to get started on boot, use `sudo systemctl enable nbfc_service`.


Differences en detail
---------------------

|Files                            | NBFC C#                               | NBFC C                                      |
|---------------------------------|---------------------------------------|----------------------------------------------
|Systemd service file             | nbfc.service                          | nbfc\_service.service                       |
|EC Probing tool                  | ec-probe                              | ec\_probe                                   |
|Notebook configuration files     | /opt/nbfc/Configs/*.xml               | /etc/nbfc/Configs/*.json                    |
|Service binary                   | /opt/nbfc/nbfcservice.sh              | /bin/nbfc\_service                          |
|PID File                         | /run/nbfc.pid                         | /run/nbfc\_service.pid                      |
|State file                       | -                                     | /run/nbfc\_service.state.json               |
|Config file                      | ?                                     | /etc/nbfc/nbfc.json                         |

- The original NBFC service is queried and controlled by the client using TCP/IP. - NBFC Linux does not implement any "real" IPC. Information about the service can be queried by reading its state file. The client controls the service by simply rewriting its configuration file and reloading it.

- The original NBFC service adjusts the fan speeds in intervals of `EcPollIntervall` according to `TemperatureThresholds`. - NBFC Linux directly sets the fan speed (also according to `TemperatureThresholds`).

- The original NBFC service provided an `Autostart` option. - NBFC Linux dropped that option, it relies on the systemd service file only.

Shell autocompletion
--------------------

NBFC-Linux comes with shell completion scripts for bash, fish and zsh.

```
~ $ nbfc_service <TAB>
--config-file          -c  -- Use alternative config file (default /etc/nbfc/nbfc.json)
--debug                -d  -- Enable tracing of reads and writes of the embedded controller
--embedded-controller  -e  -- Specify embedded controller to use
--fork                 -f  -- Switch process to background after sucessfully started
--help                 -h  -- show this help message and exit
--readonly             -r  -- Start in read-only mode
--state-file           -s  -- Write state to an alternative file (default /var/run/nbfc_service.state.json)

~ $ nbfc <TAB>
config   -- List or apply configs
help     -- Show help
restart  -- Restart the service
set      -- Control fan speed
start    -- Start the service
status   -- Show the service status
stop     -- Stop the service
```

See also the documentation about the [nbfc configuration](doc/nbfc_service.json.md).

