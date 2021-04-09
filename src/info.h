#ifndef NBFC_INFO_H_
#define NBFC_INFO_H_

#include "config.h"
#include "error.h"
#include "fan.h"

Error* Info_Init(const char*);
void   Info_Close();
Error* Info_Write(Config*, float temperature, bool readonly, array_of(Fan)*);

#endif
