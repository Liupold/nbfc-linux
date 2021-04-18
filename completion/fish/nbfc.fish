complete -c nbfc -s h -l help -d 'show this help message and exit'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a start -d 'Start the service'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a stop -d 'Stop the service'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a restart -d 'Restart the service'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a status -d 'Show the service status'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a config -d 'List or apply configs'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a set -d 'Control fan speed'
complete -c nbfc -f -n "not __fish_seen_subcommand_from start stop restart status config set help" -a help -d 'Show help'
complete -c nbfc -n '__fish_seen_subcommand_from start' -s h -l help -d 'show this help message and exit'
complete -c nbfc -n '__fish_seen_subcommand_from start' -s e -l enabled -d 'Start in enabled mode (default)'
complete -c nbfc -n '__fish_seen_subcommand_from start' -s r -l readonly -d 'Start in read-only mode'
complete -c nbfc -n '__fish_seen_subcommand_from stop' -s h -l help -d 'show this help message and exit'
complete -c nbfc -n '__fish_seen_subcommand_from restart' -s h -l help -d 'show this help message and exit'
complete -c nbfc -n '__fish_seen_subcommand_from restart' -s e -l enabled -d 'Restart in enabled mode (default)'
complete -c nbfc -n '__fish_seen_subcommand_from restart' -s r -l readonly -d 'Restart in read-only mode'
complete -c nbfc -n '__fish_seen_subcommand_from status' -s h -l help -d 'show this help message and exit'
complete -c nbfc -n '__fish_seen_subcommand_from status' -s a -l all -d 'Show service and fan status (default)'
complete -c nbfc -n '__fish_seen_subcommand_from status' -s s -l service -d 'Show service status'
complete -c nbfc -n '__fish_seen_subcommand_from status' -s f -l fan -d 'Show fan status' -r -f -a "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 '...'"
complete -c nbfc -n '__fish_seen_subcommand_from status' -s w -l watch -d 'Show status periodically' -r
complete -c nbfc -n '__fish_seen_subcommand_from config' -s h -l help -d 'show this help message and exit'
complete -c nbfc -n '__fish_seen_subcommand_from config' -s l -l list -d 'List all available configs (default)'
complete -c nbfc -n '__fish_seen_subcommand_from config' -s s -l set -d 'Set a config' -r
complete -c nbfc -n '__fish_seen_subcommand_from config' -s a -l apply -d 'Set a config and enable fan control' -r
complete -c nbfc -n '__fish_seen_subcommand_from config' -s r -l recommend -d 'List configs which may work for your device'
complete -c nbfc -n '__fish_seen_subcommand_from set' -s h -l help -d 'show this help message and exit'
complete -c nbfc -n '__fish_seen_subcommand_from set' -s a -l auto -d "Set fan speed to 'auto'"
complete -c nbfc -n '__fish_seen_subcommand_from set' -s s -l speed -d 'Set fan speed to <value>' -r
complete -c nbfc -n '__fish_seen_subcommand_from set' -s f -l fan -d 'Fan index (zero based)' -r -f -a "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 '...'"
complete -c nbfc -n '__fish_seen_subcommand_from help' -s h -l help -d 'show this help message and exit'

