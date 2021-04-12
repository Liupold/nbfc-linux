#define EC_PROBE_HELP_TEXT "usage: %s [-e EC] {dump,read,write,monitor} ...\n"\
 "\n"\
 "Probing tool for embedded controllers\n"\
 "\n"\
 "optional arguments:\n"\
 "  -e EC, --embedded-controller EC\n"\
 "                        Specify embedded controller to use\n"\
 "\n"\
 "subcommands:\n"\
 "  commands\n"\
 "\n"\
 "  {dump,read,write,monitor}\n"\
 "    dump                Dump all EC registers\n"\
 "    read                Read a byte from a EC register\n"\
 "    write               Write a byte to a EC register\n"\
 "    monitor             Monitor all EC registers for changes\n"\
 "\n"\
 "All input values are interpreted as decimal numbers by default. Hexadecimal\n"\
 "values may be entered by prefixing them with \"0x\".\n"\
 ""
#define DUMP_HELP_TEXT "usage: %s dump\n"\
 ""

#define READ_HELP_TEXT "usage: %s read REGISTER\n"\
 "\n"\
 "positional arguments:\n"\
 "  REGISTER  Register source\n"\
 ""

#define WRITE_HELP_TEXT "usage: %s write REGISTER VALUE\n"\
 "\n"\
 "positional arguments:\n"\
 "  REGISTER  Register destination\n"\
 "  VALUE     Value to write\n"\
 ""

#define MONITOR_HELP_TEXT "usage: %s monitor [-i seconds] [-t seconds] [-r REPORT] [-c] [-d]\n"\
 "\n"\
 "optional arguments:\n"\
 "  -i seconds, --interval seconds\n"\
 "                        Monitored timespan\n"\
 "  -t seconds, --timespan seconds\n"\
 "                        Set poll intervall\n"\
 "  -r REPORT, --report REPORT\n"\
 "                        Save all readings as a CSV file\n"\
 "  -c, --clearly         Blanks out consecutive duplicate readings\n"\
 "  -d, --decimal         Output readings in decimal format instead of\n"\
 "                        hexadecimal format\n"\
 ""


