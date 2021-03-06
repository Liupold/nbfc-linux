complete -c ec_probe -s h -l help -d 'show this help message and exit'
complete -c ec_probe -s e -l embedded-controller -d 'Specify embedded controller to use' -r -f -a 'ec_linux ec_sys_linux'
complete -c ec_probe -n 'test (__fish_number_of_cmd_args_wo_opts) = 1' -f -a 'dump read write monitor'
complete -c ec_probe -f -n "not __fish_seen_subcommand_from dump read write monitor" -a dump -d 'Dump all EC registers'
complete -c ec_probe -f -n "not __fish_seen_subcommand_from dump read write monitor" -a read -d 'Read a byte from a EC register'
complete -c ec_probe -f -n "not __fish_seen_subcommand_from dump read write monitor" -a write -d 'Write a byte to a EC register'
complete -c ec_probe -f -n "not __fish_seen_subcommand_from dump read write monitor" -a monitor -d 'Monitor all EC registers for changes'
complete -c ec_probe -n '__fish_seen_subcommand_from dump' -s h -l help -d 'show this help message and exit'
complete -c ec_probe -n '__fish_seen_subcommand_from read' -s h -l help -d 'show this help message and exit'
complete -c ec_probe -n '__fish_seen_subcommand_from read' -n 'test (__fish_number_of_cmd_args_wo_opts) = 2' -d 'Register source' -r -f -a '(seq 0 255)'
complete -c ec_probe -n '__fish_seen_subcommand_from write' -s h -l help -d 'show this help message and exit'
complete -c ec_probe -n '__fish_seen_subcommand_from write' -n 'test (__fish_number_of_cmd_args_wo_opts) = 2' -d 'Register destination' -r -f -a '(seq 0 255)'
complete -c ec_probe -n '__fish_seen_subcommand_from write' -n 'test (__fish_number_of_cmd_args_wo_opts) = 3' -d 'Value to write' -r -f -a '(seq 0 255)'
complete -c ec_probe -n '__fish_seen_subcommand_from monitor' -s h -l help -d 'show this help message and exit'
complete -c ec_probe -n '__fish_seen_subcommand_from monitor' -s i -l interval -d 'Monitored timespan' -r
complete -c ec_probe -n '__fish_seen_subcommand_from monitor' -s t -l timespan -d 'Set poll intervall' -r
complete -c ec_probe -n '__fish_seen_subcommand_from monitor' -s r -l report -d 'Save all readings as a CSV file' -r -F
complete -c ec_probe -n '__fish_seen_subcommand_from monitor' -s c -l clearly -d 'Blanks out consecutive duplicate readings'
complete -c ec_probe -n '__fish_seen_subcommand_from monitor' -s d -l decimal -d 'Output readings in decimal format instead of hexadecimal format'
