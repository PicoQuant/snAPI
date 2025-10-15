ifneq ($(KERNELRELEASE),)
	obj-m   := th260pcie.o

else
	KDIR    := /lib/modules/$(shell uname -r)/build
	PWD     := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
clean: 
	$(MAKE) -C $(KDIR) M=$(PWD) clean

endif
