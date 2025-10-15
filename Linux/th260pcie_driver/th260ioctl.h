
#include <linux/ioctl.h>
  
#define IOCTL_GET_VERSION _IOR('t', 0, uint64_t)  //actually an address
#define IOCTL_GET_SERIAL  _IOR('t', 1, uint64_t)  //actually an address
#define IOCTL_GET_BAROFFS _IOR('t', 2, uint64_t)  //actually an address


