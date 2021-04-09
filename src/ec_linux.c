﻿#include "ec_linux.h"

#include "error.h"

#include <unistd.h>
#include <stdbool.h>
#include <endian.h>
#include <fcntl.h>
#include <sys/stat.h>

/* ========================================================================== *
 *            Core/Plugins/StagWare.Plugins.ECLinux/ECLinux.cs                *
 * ========================================================================== */

#define EC_Linux_PortFilePath "/dev/port"

static int EC_Linux_FD = -1;

Error* EC_Linux_Init() {
  return err_success();
}

Error* EC_Linux_Open() {
  EC_Linux_FD = open(EC_Linux_PortFilePath, O_RDWR | O_EXCL);
  if (EC_Linux_FD < 0)
    return err_stdlib(0, EC_Linux_PortFilePath);
  return err_success();
}

void EC_Linux_Close() {
  if (EC_Linux_FD >= 0) {
    close(EC_Linux_FD);
    EC_Linux_FD = -1;
  }
}

static bool EC_Linux_WritePort(int port, uint8_t value)
{
  return (1 == pwrite(EC_Linux_FD, &value, 1, port));
}

static bool EC_Linux_ReadPort(int port, uint8_t* out)
{
  return (1 != pread(EC_Linux_FD, out, 1, port));
}

/* ========================================================================== *
 *        Core/Plugins/StagWare.Hardware.LPC/EmbeddedControllerBase.cs        *
 * ========================================================================== */

// See ACPI specs ch.12.2
enum ECStatus
{
  ECStatus_OutputBufferFull = 0x01,  // EC_OBF
  ECStatus_InputBufferFull  = 0x02,  // EC_IBF
  //                          0x04,     -- IGNORED
  ECStatus_Command          = 0x08,  // CMD
  ECStatus_BurstMode        = 0x10,  // BURST
  ECStatus_SCIEventPending  = 0x20,  // SCI_EVT
  ECStatus_SMIEventPending  = 0x40,  // SMI_EVT
  //                          0x80,     -- IGNORED
};

// See ACPI specs ch.12.3
enum ECCommand
{
  ECCommand_Read            = 0x80,  // RD_EC
  ECCommand_Write           = 0x81,  // WR_EC
  ECCommand_BurstEnable     = 0x82,  // BE_EC
  ECCommand_BurstDisable    = 0x83,  // BD_EC
  ECCommand_Query           = 0x84,  // QR_EC
};

static const int EC_Linux_CommandPort        = 0x66; // EC_SC
static const int EC_Linux_DataPort           = 0x62; // EC_DATA
static const int EC_Linux_RWTimeout          = 500;  // spins
static const int EC_Linux_FailuresBeforeSkip = 20;
static const int EC_Linux_MaxRetries         = 5;

static int EC_Linux_WaitReadFailures         = 0;

// ============================================================================
// PRIVATE
// ============================================================================

static bool EC_Linux_WaitForEcStatus(enum ECStatus status, bool isSet)
{
  for (int timeout = EC_Linux_RWTimeout; timeout--;) {
    uint8_t value;
    if (! EC_Linux_ReadPort(EC_Linux_CommandPort, &value))
      continue;

    if (isSet)
      value = ~value;

    if ((status & value) == 0)
      return true;
  }

  errno = ETIME;
  return false;
}

static inline bool EC_Linux_WaitWrite()
{
  return EC_Linux_WaitForEcStatus(ECStatus_InputBufferFull, false);
}

static bool EC_Linux_WaitRead()
{
  if (EC_Linux_WaitReadFailures > EC_Linux_FailuresBeforeSkip) {
    return true;
  }
  else if (EC_Linux_WaitForEcStatus(ECStatus_OutputBufferFull, true)) {
    EC_Linux_WaitReadFailures = 0;
    return true;
  }
  else {
    EC_Linux_WaitReadFailures++;
    return false;
  }
}

static bool EC_Linux_TryReadByte(int register_, uint8_t* value)
{
  bool success = true
    && EC_Linux_WaitWrite()
    && EC_Linux_WritePort(EC_Linux_CommandPort, ECCommand_Read)
    && EC_Linux_WaitWrite()
    && EC_Linux_WritePort(EC_Linux_DataPort, register_)
    && EC_Linux_WaitWrite()
    && EC_Linux_WaitRead()
    && EC_Linux_ReadPort(EC_Linux_DataPort, value);

  if (! success)
    *value = 0;
  return success;
}

static bool EC_Linux_TryWriteByte(int register_, uint8_t value)
{
  return true
    && EC_Linux_WaitWrite()
    && EC_Linux_WritePort(EC_Linux_CommandPort, ECCommand_Write)
    && EC_Linux_WaitWrite()
    && EC_Linux_WritePort(EC_Linux_DataPort, register_)
    && EC_Linux_WaitWrite()
    && EC_Linux_WritePort(EC_Linux_DataPort, value);
}

static bool EC_Linux_TryReadWord(int register_, uint16_t* value)
{
  // Byte order: little endian
 
  uint8_t result[2];

  if (EC_Linux_TryReadByte(register_+0, &result[0]) &&
      EC_Linux_TryReadByte(register_+1, &result[1]))
  {
    *value = ((uint16_t) result[0]) | (((uint16_t) result[1]) << 8);
    return true;
  }

  *value = 0;
  return false;
}

static bool EC_Linux_TryWriteWord(int register_, uint16_t value)
{
  // Byte order: little endian

  value = htole16(value);

  uint8_t msb = value >> 8;
  uint8_t lsb = value;

  return EC_Linux_TryWriteByte(register_+0, lsb)
      && EC_Linux_TryWriteByte(register_+1, msb);
}

// ============================================================================
// PUBLIC
// ============================================================================

Error* EC_Linux_WriteByte(int register_, uint8_t val) {
  for (int i = EC_Linux_MaxRetries; i--;)
    if (EC_Linux_TryWriteByte(register_, val))
      return err_success();
  return err_stdlib(0, "EC_Linux_WriteByte");
}

Error* EC_Linux_WriteWord(int register_, uint16_t val) {
  for (int i = EC_Linux_MaxRetries; i--;)
    if (EC_Linux_TryWriteWord(register_, val))
      return err_success();
  return err_stdlib(0, "EC_Linux_WriteWord");
}

Error* EC_Linux_ReadByte(int register_, uint8_t* val) {
  for (int i = EC_Linux_MaxRetries; i--;)
    if (EC_Linux_TryReadByte(register_, val))
      return err_success();
  *val = 0;
  return err_stdlib(0, "EC_Linux_ReadByte");
}

Error* EC_Linux_ReadWord(int register_, uint16_t* val) {
  for (int i = EC_Linux_MaxRetries; i--;)
    if (EC_Linux_TryReadWord(register_, val))
      return err_success();
  *val = 0;
  return err_stdlib(0, "EC_Linux_ReadWord");
}

EC_VTable EC_Linux_VTable = {
  EC_Linux_Init,
  EC_Linux_Open,
  EC_Linux_Close,
  EC_Linux_ReadByte,
  EC_Linux_ReadWord,
  EC_Linux_WriteByte,
  EC_Linux_WriteWord,
};
