#include "nbfc.h"
#include "nbfc_service.h"

#include "ec_linux.h"
#include "ec_sys_linux.h"
#include "ec_dummy.h"
#include "ec_debug.h"

#include "error.h"
#include "memory.h"
#include "optparse/optparse.h"
#include "generated/nbfc_service.help.h"

#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <locale.h>

EC_VTable* ec;

static volatile int quit;
static void sig_handler(int i) { quit = i; }

static cli99_option cli_options[] = {
#define G1 cli99_exclusive_group(1) // readonly <or> fork
#define G2 cli99_exclusive_group(2) // debug    <or> fork
  {"-h|--help",                'h',  0},
  {"-e|--embedded-controller", 'e',  1},
  {"-r|--readonly",            'r',  0},
  {"-f|--fork",                'f',  0},
  {"-d|--debug",               'd',  0},
  {"-s|--state-file",          's',  1},
  {"-c|--config-fie",          'c',  1},
  {"--critical-temperature",   '!',  1|cli99_type(float)},
  cli99_options_end()
#undef G1
#undef G2
};

static void parse_opts(int argc, char* const argv[]) {
  cli99 p;
  cli99_Init(&p, argc, argv, cli_options, cli99_options_python);

  int o;
  while ((o = cli99_GetOpt(&p))) {
    switch (o) {
    case 'e':
      /**/ if (! strcmp(p.optarg, "dummy"))        ec = &EC_Dummy_VTable;
      else if (! strcmp(p.optarg, "ec_linux"))     ec = &EC_Linux_VTable;
      else if (! strcmp(p.optarg, "ec_sys_linux")) ec = &EC_SysLinux_VTable;
      else {
        fprintf(stderr, "Invalid value for %s: %s\n", p.optopt, p.optarg);
        exit(NBFC_EXIT_CMDLINE);
      }
      break;
    case 'h':  printf(NBFC_SERVICE_HELP_TEXT, argv[0]); exit(0);   break;
    case 'r':  options.read_only      = 1;                         break;
    case 'f':  options.fork           = 1;                         break;
    case 'd':  options.debug          = 1;                         break;
    case 's':  options.state_file     = p.optarg;                  break;
    case 'c':  options.service_config = p.optarg;                  break;
    case '!':  options.critical_temperature = p.optval.d;          break;
    default:
      cli99_ExplainError(&p);
      exit(NBFC_EXIT_CMDLINE);
    }
  }

  if (!cli99_End(&p)) {
    fprintf(stderr, "Too much arguments\n");
    exit(NBFC_EXIT_CMDLINE);
  }
}

int main(int argc, char* const argv[])
{
  char stack_buffer[16000];
  char temp_buffer[16000];

  Mem_AddPool(stack_buffer, sizeof(stack_buffer));
  Temp_AddPool(temp_buffer, sizeof(temp_buffer));
  setlocale(LC_NUMERIC, "C"); // for json floats
  signal(SIGINT, sig_handler);
  signal(SIGTERM, sig_handler);

  options.service_config = NBFC_SERVICE_CONFIG;
  options.state_file     = NBFC_STATE_FILE;
  options.ec_name        = "";
  parse_opts(argc, argv);

  if (options.read_only)
    fprintf(stderr, "readonly mode enabled\n");

  atexit(Service_Cleanup);

  Error* e = Service_Init();
  if (e) {
    err_print_all(e);
    exit(NBFC_EXIT_INIT);
  }

  while (!quit) {
    Temp_Reset();
    Service_Error(Service_Loop());
  }

  // Important! We dont *return* from main,
  // because stack_buffer will be destroyed then.
  exit(0);
}

