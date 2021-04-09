#define NBFC_SERVICE_HELP_TEXT "usage: %s [-r] [-f] [-d] [-c config] [-s state.json] [-e EC]\n"\
 "\n"\
 "NoteBook FanControl service\n"\
 "\n"\
 "optional arguments:\n"\
 "  -r, --readonly        Start in read-only mode\n"\
 "  -f, --fork            Switch process to background after sucessfully started\n"\
 "  -d, --debug           Enable tracing of reads and writes of the embedded\n"\
 "                        controller\n"\
 "  -c config, --config-file config\n"\
 "                        Use alternative config file (default\n"\
 "                        /etc/nbfc/nbfc.json)\n"\
 "  -s state.json, --state-file state.json\n"\
 "                        Write state to an alternative file (default\n"\
 "                        /var/run/nbfc_service.state.json)\n"\
 "  -e EC, --embedded-controller EC\n"\
 "                        Specify embedded controller to use\n"\
 ""
