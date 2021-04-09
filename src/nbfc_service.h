#ifndef NBFC_SERVICE_H_
#define NBFC_SERVICE_H_

#include "error.h"

typedef struct Service_Options Service_Options;
struct Service_Options {
  bool         fork;
  bool         read_only;
  int          debug;
  const char*  ec_name;
  const char*  service_config;
  const char*  state_file;
  float        critical_temperature;
};

extern Service_Options options;

Error* Service_Init();
Error* Service_Loop();
void   Service_Error(Error*);
void   Service_Cleanup();

#endif
