#define _XOPEN_SOURCE  500 // unistd.h: export pwrite()/pread()
#define _DEFAULT_SOURCE    // endian.h:

#include "nbfc.h"
#include "macros.h"
#include "ec_linux.h"
#include "ec_sys_linux.h"
#include "optparse/optparse.h"
#include "generated/ec_probe.help.h"

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdarg.h>
#include <limits.h>
#include <signal.h>
#include <unistd.h>

#include "error.c"             // src
#include "ec_linux.c"          // src
#include "ec_sys_linux.c"      // src
#include "optparse/optparse.c" // src
#include "memory.c"            // src
#include "nxjson.c"            // src

#define Console_Black         "\033[0;30m"
#define Console_Red           "\033[0;31m"
#define Console_Green         "\033[0;32m"
#define Console_Yelllow       "\033[0;33m"
#define Console_Blue          "\033[0;34m"
#define Console_Magenta       "\033[0;35m"
#define Console_Cyan          "\033[0;36m"
#define Console_White         "\033[0;37m"
#define Console_Gray          "\033[0;38m"

#define Console_BoldBlack     "\033[1;30m"
#define Console_BoldRed       "\033[1;31m"
#define Console_BoldGreen     "\033[1;32m"
#define Console_BoldYelllow   "\033[1;33m"
#define Console_BoldBlue      "\033[1;34m"
#define Console_BoldMagenta   "\033[1;35m"
#define Console_BoldCyan      "\033[1;36m"
#define Console_BoldWhite     "\033[1;37m"
#define Console_BoldGray      "\033[1;38m"

#define Console_Reset         "\033[0;0m"
#define Console_Clear         "\033[1;1H\033[2J"


#define               RegistersSize 256
typedef uint8_t       RegisterBuf[RegistersSize];
typedef const char*   RegisterColors[RegistersSize];

static inline void    Register_PrintHeader();
static void           Register_PrintRegister(RegisterBuf*, RegisterColors);
static inline void    Register_FromEC(RegisterBuf*);
static void           Register_PrintWatch(RegisterBuf*, RegisterBuf*, RegisterBuf*);
static void           Register_PrintMonitor(RegisterBuf*, int);
static void           Register_WriteMonitorReport(RegisterBuf*, int, FILE*);
static void           Register_PrintDump(RegisterBuf*);


EC_VTable* ec;
static volatile int   quit;
static volatile int   Stress_DummyVar;
static RegisterBuf    Registers_Log[32768];
static void           Stress_SetQuit();
static void           Stress_EndlessTask();
static void           Stress_CPU(int);
static void           Handle_Signal(int);

enum Command {
  Command_Dump,
  Command_Monitor,
  Command_Watch,
  Command_Read,
  Command_Write,
  Command_Help,
};

static const char* HelpTexts[] = {
  DUMP_HELP_TEXT,
  MONITOR_HELP_TEXT,
  MONITOR_HELP_TEXT,
  READ_HELP_TEXT,
  WRITE_HELP_TEXT,
  EC_PROBE_HELP_TEXT,
};

static const cli99_option main_options[] = {
  {"-v|--verbose",             -'v',  0},
  {"-e|--embedded-controller", -'e',  1},
  {"-h|--help",                -'h',  0},
  {"command",                   'C',  1|cli99_required_option},
  cli99_options_end()
};

static const cli99_option monitor_command_options[] = {
  cli99_include_options(&main_options),
  {"-r|--report",              -'r',  1},
  {"-c|--clearly",             -'c',  0},
  {"-d|--decimal",             -'d',  0},
  {"-t|--timespan",            -'t',  1|cli99_type(unsigned)},
  {"-i|--interval",            -'i',  1|cli99_type(unsigned)},
  cli99_options_end()
};

static const cli99_option watch_command_options[] = {
  cli99_include_options(&main_options),
  {"-t|--timespan",            -'t',  1|cli99_type(unsigned)},
  {"-i|--interval",            -'i',  1|cli99_type(unsigned)},
  cli99_options_end()
};

static const cli99_option read_command_options[] = {
  cli99_include_options(&main_options),
  {"register",                  'R',  1|cli99_type(uint16_t)|cli99_required_option},
  cli99_options_end()
};

static const cli99_option write_command_options[] = {
  cli99_include_options(&main_options),
  {"register",                  'R',  1|cli99_type(uint16_t)|cli99_required_option},
  {"value",                     'V',  1|cli99_type(uint16_t)|cli99_required_option},
  cli99_options_end()
};

static const cli99_option dump_command_options[] = {
  cli99_include_options(&main_options),
  cli99_options_end()
};

static const cli99_option* Options[] = {
  dump_command_options,
  monitor_command_options,
  watch_command_options,
  read_command_options,
  write_command_options,
  dump_command_options, // help
};

static struct {
  int             timespan;
  int             interval;
  const char*     report;
  bool            clearly;
  bool            decimal;
  bool            verbose;
  uint16_t        register_;
  uint16_t        value;
  int             stress_cpu;
} options;

static int va_find_string(const char* needle, ...) {
  va_list va;
  va_start(va, needle);

  const char* s;
  for (int i = 0; (s = va_arg(va, const char*)); ++i) {
    if (! strcmp(s, needle)) {
      va_end(va);
      return i;
    }
  }

  va_end(va);
  return -1;
}

int main(int argc, char* const argv[]) {
  options.interval = 500;
  enum Command cmd = Command_Help;

  cli99 p;
  cli99_Init(&p, argc, argv, main_options, cli99_options_python);

  int o;
  while ((o = cli99_GetOpt(&p))) {
    switch (o) {
    case  'C':
      // Important: Same order as in `enum Command`
      cmd = (enum Command)
        va_find_string(p.optarg, "dump", "monitor", "watch", "read", "write", "help", 0);

      if (cmd == (enum Command) -1)
        die(NBFC_EXIT_CMDLINE, "%s: Invalid command: %s\n", argv[0], p.optarg);

      if (cmd == Command_Help) {
        printf(EC_PROBE_HELP_TEXT, argv[0]);
        return 0;
      }
      cli99_SetOptions(&p, Options[cmd], false);
      break;
    case  'R':  options.register_= p.optval.u;        break;
    case  'V':  options.value    = p.optval.u;        break;
    case -'h':  printf(HelpTexts[cmd], argv[0]);      return 0;
    case -'c':  options.clearly  = 1;                 break;
    case -'d':  options.decimal  = 1;                 break;
    case -'v':  options.verbose  = 1;                 break;
    case -'e':  if (!strcmp("ec_sys_linux", p.optarg))    ec = &EC_SysLinux_VTable;
                else if (!strcmp("ec_linux", p.optarg))   ec = &EC_Linux_VTable;
                else die(NBFC_EXIT_CMDLINE, "Invalid value: %s\n", p.optarg);
                break;
    case -'r':  options.report   = p.optarg;          break;
    case -'t':  options.timespan = p.optval.i * 1000; break;
    case -'i':  options.interval = p.optval.i * 1000;
                if (! options.interval)
                  die(NBFC_EXIT_CMDLINE, "%s: %s\n", argv[0], "--interval == 0");
                break;
    default:
      cli99_ExplainError(&p);
      exit(NBFC_EXIT_CMDLINE);
    }
  }

  if (cmd == Command_Help) {
    printf(EC_PROBE_HELP_TEXT, argv[0]);
    return 1;
  }

  if (! cli99_End(&p))
    die(NBFC_EXIT_CMDLINE, "Too much arguments\n");

  if (! cli99_CheckRequired(&p)) {
    cli99_ExplainError(&p);
    exit(NBFC_EXIT_CMDLINE);
  }

  Error* e = NULL;
  signal(SIGINT,  Handle_Signal);
  signal(SIGTERM, Handle_Signal);
  ec = &EC_SysLinux_VTable;
  e = ec->Init();
  e_die();
  e = ec->Open();
  e_die();

  switch (cmd) {
    case Command_Dump: {
      Register_FromEC(Registers_Log);
      Register_PrintDump(Registers_Log);
      break;
    }
    case Command_Read: {
      uint8_t byte;
      e = ec->ReadByte(options.register_, &byte);
      printf("%d (%.2X)\n", byte, byte);
      e_die();
      break;
    }
    case Command_Write: {
      e = ec->WriteByte(options.register_, options.value);
      e_die();
      break;
    }
    case Command_Monitor: {
      if (options.stress_cpu)
        Stress_CPU(options.stress_cpu);

      const int max_loops = (!options.timespan) ? INT_MAX :
        options.timespan / options.interval;

      RegisterBuf* regs = Registers_Log;
      int size = ARRAY_SSIZE(Registers_Log);
      int loops;
      for (loops = 0; !quit && loops < max_loops && --size; ++loops) {
        Register_FromEC(regs + loops);
        Register_PrintMonitor(regs, loops);
        usleep(options.interval * 1000);
      }

      if (options.report) {
        FILE* fh = fopen(options.report, "w");
        if (! fh)
          die(NBFC_EXIT_FAILURE, "%s: %s\n", options.report, strerror(errno));
        Register_WriteMonitorReport(regs, loops, fh);
        fclose(fh);
      }
      break;
    }
    case Command_Watch: {
      const int max_loops = (!options.timespan) ? INT_MAX :
        options.timespan / options.interval;

      int size = ARRAY_SSIZE(Registers_Log);
      RegisterBuf* regs = Registers_Log;
      Register_FromEC(regs);
      Register_PrintRegister(regs, NULL);
      for (int loops = 1; !quit && loops < max_loops && --size; ++loops) {
        Register_FromEC(regs + loops);
        Register_PrintWatch(regs , regs + loops, regs + loops - 1);
        usleep(options.interval * 1000);
      }
    }
    case Command_Help: break;
  }

  return 0;
}

static void Handle_Signal(int s) {
  quit = s;
}

// ============================================================================
// Registers code
// ============================================================================

static inline void Register_PrintHeader() {
  printf(Console_Reset
    "---|------------------------------------------------\n"
    "   | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n"
    "---|------------------------------------------------\n");
}

static void Register_PrintRegister(RegisterBuf* self, RegisterColors color) {
  Register_PrintHeader();
  for (int i = 0; i <= 0xF0; i += 0x10) {
    printf(Console_Reset "%.2X |", i);
    if (color)
      for (int j = 0; j <= 0xF; ++j)
        printf("%s %.2X", color[i + j], my[i + j]);
    else
      for (int j = 0; j <= 0xF; ++j)
        printf("%.2X", my[i + j]);
    printf("\n");
  }
}

static inline void Register_FromEC(RegisterBuf* self) {
  for (int i = 0; i < RegistersSize; i++)
    ec->ReadByte(i, &my[i]);
}

static void Register_PrintWatch(RegisterBuf* self, RegisterBuf* a, RegisterBuf* b) {
  RegisterColors colors;

  for (int i = 0; i < RegistersSize; ++i) {
    const uint8_t byte = (*a)[i];
    const uint8_t diff = byte - (*b)[i];
    bool has_changed = false;

    uint8_t save = byte;
    for (range(RegisterBuf*, r, self, b)) {
      if (save != (*r)[i]) {
        has_changed = true;
        break;
      }
    }

    /**/ if (diff)          colors[i] = Console_Yelllow;
    else if (has_changed)   colors[i] = Console_BoldBlue;
    else if (byte == 0xFF)  colors[i] = Console_White;
    else if (byte)          colors[i] = Console_BoldWhite;
    else                    colors[i] = Console_Black;
  }

  Register_PrintRegister(a, colors);
}

static void Register_PrintMonitor(RegisterBuf* self, int size) {
  printf(Console_Clear);

  for (int i = 0; i < RegistersSize; ++i) {
    bool was_touched = false;
    for (range(int, j, 0, size)) {
      if (my[i] != (*(self + j))[i]) {
        was_touched = true;
        break;
      }
    }

    if (! was_touched)
      continue;

    printf(Console_Green "0x%.2X:", i);
    uint8_t byte = my[i];
    for (range(int, j, max(size - 24, 0), size)) {
      const uint8_t diff = byte - (*(self + j))[i];
      byte = (*(self + j))[i];
      if (diff)
        printf(Console_BoldBlue " %.2X", byte);
      else
        printf(Console_BoldWhite " %.2X", byte);
    }
    printf("\n");
  }
}

static void Register_WriteMonitorReport(RegisterBuf* self, int size, FILE* fh) {
  for (int i = 0; i < RegistersSize; ++i) {
    bool was_touched = false;
    for (range(int, j, 0, size)) {
      if (my[i] != (*(self + j))[i]) {
        was_touched = true;
        break;
      }
    }

    if (! was_touched)
      continue;

    fprintf(fh, "%.2X", i);
    for (range(int, j, 0, size))
      fprintf(fh, ",%.2X", (*(self + j)[i]));
    fprintf(fh, "\n");
  }
}

static void Register_PrintDump(RegisterBuf* self) {
  RegisterColors c;

  for (int i = 0; i < RegistersSize; ++i)
    c[i] = (my[i] == 0x00 ? Console_BoldBlack :
            my[i] == 0xFF ? Console_Green     :
                            Console_Red);

  Register_PrintRegister(self, c);
}

// ============================================================================
// Stress code
// ============================================================================

static void Stress_SetQuit() {
  quit = 1;
}

static void Stress_EndlessTask() {
  for (; !quit; ++Stress_DummyVar);
}

static void Stress_CPU(int forks) {
  atexit(Stress_SetQuit);
  for (range(int, i, 0, forks))
    switch (fork()) {
    case -1: die(NBFC_EXIT_FATAL, "fork: %s\n", strerror(errno));
    case 0:  Stress_EndlessTask(); _exit(0);
    default: break;
    }
}

#if 0
static inline void Show_Help(const char* prog) {
    "NoteBook FanControl EC probing tool\n"
    "\n"
    "usage: %s [--version] [--help] <command> [<args>]\n"
    "\n"
    "commands:\n"
    "  dump                         Dump all EC registers\n"
    "\n"
    "  read <register>              Read a byte from a EC register\n"
    "\n"
    "  write <register> <value> [options]\n"
    "                               Write a byte to a EC register\n"
    "    -v, --verbose                Be verbose\n"
    "\n"
    "  monitor [options]            Monitor all EC registers for changes\n"
    "    -t, --timespan <seconds>     Monitored timespan (default: infinite)\n"
    "    -i, --interval <seconds>     Set poll interval (default: 5)\n"
    "    -r, --report <path>          Save all readings as CSV file\n"
    "    -c, --clearly                Blanks out consecutive duplicate readings\n"
    "    -d, --decimal                Output readings in decimal format instead of hexadecimal format\n"
    "\n"
    "All input values are interpreted as decimal numbers by default.\n"
    "Hexadecimal values may be entered by prefixing them with \"0x\".\n",
}
#endif
