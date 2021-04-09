
#ifndef NDEBUG
#include <stdio.h>

static inline const char* cli99_state_tostr(uint64_t state) {
  switch (state) {
    case cli99_state_uninitialized   : return "uninitialized";
    case cli99_state_next_word       : return "next_word";
    case cli99_state_short_opt       : return "short_opt";
    case cli99_state_short_parameter : return "short_parameter";
    case cli99_state_long_opt        : return "long_opt";
    case cli99_state_long_parameter  : return "long_parameter";
    case cli99_state_positional      : return "positional";
    case cli99_state_options_end     : return "options_end";
    case cli99_state_EOF             : return "EOF";
    default:                           return "<invalid state>";
  }
}

static inline const char* cli99_operation_tostr(uint64_t operation) {
  switch (operation) {
    case 0:                             return "0";
    case cli99_op_check_state:          return "op_check_state";
    case cli99_op_next:                 return "op_next_state";
    case cli99_op_getoptarg:            return "op_getoptarg";
    case cli99_op_getarg:               return "op_getarg";
    case cli99_op_rewind_short_opt:     return "op_rewind_short_opt";
    default:                            return "op_unknown";
  }
}
#else
#define cli99_state_tostr(STATE)     "cli99_state_tostr() disabled by NDEBUG"
#define cli99_operation_tostr(STATE) "cli99_operation_tostr() disabled by NDEBUG"
#endif

#if 0
static inline const char* cli99_NextDelimitedOption(const char** options, int* len, const char* delimiters) {
  if (!**options)
    return NULL;

  const char* o = *options;

  while (**options) {
    for (const char* d = delimiters; *d; ++d)
      if (**options == *d) {
        *len = *options - o;
        (*options)++;
        return o;
      }
    (*options)++;
  }

  *len = *options - o;
  return o;
}
#endif

#if 0 //NDEBUG
static inline bool cli99_StateCtl_Debug(cli99* self, uint64_t flags) {
//const uint64_t states    = flags & cli99_states_mask;
  const uint64_t operation = flags & cli99_operations_mask;
  printf("Entering StateCtl: %s, op = %s\n",
      cli99_state_tostr(my._state),
      cli99_operation_tostr(operation)
  );
  bool r = cli99_StateCtl(self, flags);
  printf("Leaving StateCtl: %s\n", cli99_state_tostr(my._state));
  return r;
}
#define cli99_StateCtl(self, flags) \
  cli99_StateCtl_Debug(self, flags)
#endif

