#include "ec_sys_linux.h"

#include "error.h"

#include <stdlib.h>
#include <unistd.h>
#include <endian.h>
#include <limits.h>
#include <fcntl.h>
#include <sys/stat.h>

#define EC_SysLinux_EC0_IO_Path "/sys/kernel/debug/ec/ec0/io"
#define EC_SysLinux_Module_Cmd  "modprobe ec_sys write_support=1"

static int EC_SysLinux_FD = -1;

static inline Error* EC_SysLinux_LoadKernelModule();

Error* EC_SysLinux_Init() {
  return EC_SysLinux_LoadKernelModule();
}

Error* EC_SysLinux_Open() {
  EC_SysLinux_FD = open(EC_SysLinux_EC0_IO_Path, O_RDWR | O_EXCL);
  if (EC_SysLinux_FD == -1)
    return err_stdlib(0, EC_SysLinux_EC0_IO_Path);
  return err_success();
}

void EC_SysLinux_Close() {
  if (EC_SysLinux_FD > -1) {
    close(EC_SysLinux_FD);
    EC_SysLinux_FD = -1;
  }
}

Error* EC_SysLinux_WriteByte(int register_, uint8_t value) {
  if (1 != pwrite(EC_SysLinux_FD, &value, 1, register_))
    return err_stdlib(0, EC_SysLinux_EC0_IO_Path);
  return err_success();
}

Error* EC_SysLinux_WriteWord(int register_, uint16_t value) {
  value = htole16(value);
  if (2 != pwrite(EC_SysLinux_FD, &value, 2, register_))
    return err_stdlib(0, EC_SysLinux_EC0_IO_Path);
  return err_success();
}

Error* EC_SysLinux_ReadByte(int register_, uint8_t* out) {
  uint8_t value;
  if (1 != pread(EC_SysLinux_FD, &value, 1, register_))
    return err_stdlib(0, EC_SysLinux_EC0_IO_Path);
  *out = value;
  return err_success();
}

Error* EC_SysLinux_ReadWord(int register_, uint16_t* out) {
  uint16_t value;
  if (2 != pread(EC_SysLinux_FD, &value, 2, register_))
    return err_stdlib(0, EC_SysLinux_EC0_IO_Path);
  *out = le16toh(value);
  return err_success();
}

static inline Error* EC_SysLinux_LoadKernelModule() {
  switch (system(EC_SysLinux_Module_Cmd)) {
  case 0:  return err_success();
  case -1: return err_stdlib(0, "system");
  default: return err_string(0, "Could not load `ec_sys' kernel module");
  }
}

EC_VTable EC_SysLinux_VTable = {
  EC_SysLinux_Init,
  EC_SysLinux_Open,
  EC_SysLinux_Close,
  EC_SysLinux_ReadByte,
  EC_SysLinux_ReadWord,
  EC_SysLinux_WriteByte,
  EC_SysLinux_WriteWord,
};

