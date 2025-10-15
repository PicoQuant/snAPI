/***************************************************************************
 *   Copyright (C) PicoQuant GmbH 2014-2024                                *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 ***************************************************************************/


#include <linux/module.h>
#include <linux/pci.h>
#include <linux/interrupt.h>
#include <linux/sched.h>	
#include <linux/fs.h>
#include <linux/cdev.h>		
#include <linux/uaccess.h>
#include <linux/version.h>
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4, 11, 0)
#include <linux/sched/signal.h>
#endif

#if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 0, 0)
#define _access_ok(a,b,c) access_ok(b,c)
#else
#define _access_ok(a,b,c) access_ok(a,b,c)
#endif

#include "th260ioctl.h"

#define	th260dbg 	0

#define VER_MAJOR	1       // will change when interface changes, do not change at will
#define VER_MINOR	0	// will change when interface changes, do not change at will
#define REV_MAJOR	0
#define REV_MINOR	0

#define DRVVERSION (((VER_MAJOR)<<24)+((VER_MINOR)<<16)+((REV_MAJOR)<<8)+(REV_MINOR))

#define MAX_DEVICES		4
#define DEVICE_NAME 		"th260pcie"
#define BAR_0			0
#define BAR_0_LEN		65536

#define DCR_OFFSET		0x0
#define	DCSR_OFFSET		0x4
#define WRITE_ADDR_OFFSET	0x8
#define WRITE_SIZE_OFFSET	0xC
#define WRITE_COUNT_OFFSET	0x10
#define TRANS_SIZE_OFFSET	0x40
#define MB_SERIAL_OFFSET	0x140 

#define BUSMASTERED_READ_DONE	0x100


#define MIN(a,b)		(((a) < (b)) ? (a) : (b))
#define BUFFER_SIZE(ord)    	(1UL << ((ord) + PAGE_SHIFT))


MODULE_DESCRIPTION("TimeHarp 260 PCIe driver");
MODULE_AUTHOR("Michael Wahl (wahl@picoquant.com)");
MODULE_LICENSE("GPL");

static struct pci_device_id th260_ids[] = {
	{ PCI_DEVICE(0x10EE, 0x1012), },
	{ 0, }
};

MODULE_DEVICE_TABLE(pci, th260_ids);

static int major;
static struct class *th260_class;

// structure holding device data, one for each card
struct th260_cdev {
	int minor;
	volatile int busy;
	struct pci_dev *pci_dev;
	struct cdev *cdev;
	void __iomem *bar0base;	
	uint32_t bar0offset;
	uint64_t serial;
	uint32_t maxtlpsize;
	char* dmabuf;
	int dmabuf_order;
	volatile int irq_received;
	volatile unsigned dmacount;
	volatile unsigned bytes_done;
	spinlock_t lock;	
	wait_queue_head_t wq;
};

static struct th260_cdev th260_cdev[MAX_DEVICES];



static void th260_cdev_init(void)
{
	int i;

	for(i=0; i<MAX_DEVICES; i++) {
		th260_cdev[i].minor = i;
		th260_cdev[i].busy = 0;
		th260_cdev[i].pci_dev = NULL;
		th260_cdev[i].cdev = NULL;
		th260_cdev[i].bar0base = NULL;
		th260_cdev[i].bar0offset = 0;
		th260_cdev[i].serial = 0;
		th260_cdev[i].maxtlpsize = 0;
		th260_cdev[i].dmabuf = NULL;
		th260_cdev[i].dmabuf_order = 0;	
		th260_cdev[i].bytes_done = 0;
		th260_cdev[i].irq_received = 0;
		th260_cdev[i].dmacount = 0;
		spin_lock_init(&th260_cdev[i].lock);		
		init_waitqueue_head(&(th260_cdev[i].wq));
	}
}

static int th260_cdev_add(struct pci_dev *pdev)
{
	int i, ret = -1;

	for(i=0; i<MAX_DEVICES; i++) {
		if (th260_cdev[i].pci_dev == NULL) {
			th260_cdev[i].pci_dev = pdev;
			ret = th260_cdev[i].minor;
			break;
		}
	}
	
	return ret;
}

static void th260_cdev_del(struct pci_dev *pdev)
{
	int i;

	for(i=0; i<MAX_DEVICES; i++) {
		if (th260_cdev[i].pci_dev == pdev) {
			th260_cdev[i].pci_dev = NULL;
		}
	}
}

// called when the device node is opened
static int th260_open(struct inode *inode, struct file *file)
{ 
  	file->private_data = (void *)&(th260_cdev[iminor(inode)]);		
	return 0;
}

// called when the device node is closed
static int th260_release(struct inode *inode, struct file *file)
{			
	return 0;
}


static void th260_dma_start (struct th260_cdev* pcard)
{
	u32 tlpsize, ndwords, tlpcount, rest;
	
	if(th260dbg)
	printk(KERN_DEBUG "th260pcie: dma start, %d bytes\n",pcard->dmacount);
    
	iowrite32(1, pcard->bar0base + DCR_OFFSET);
	iowrite32(0, pcard->bar0base + DCR_OFFSET);		
	
	tlpsize = pcard->maxtlpsize; // in dwords
	ndwords = pcard->dmacount/4;
	tlpcount = ndwords / tlpsize;
	rest = ndwords % tlpsize;

	while(rest&&tlpsize>2)
	{
		tlpsize>>=1;
		rest = ndwords % tlpsize;
		tlpcount = ndwords / tlpsize;
	}

	if(th260dbg)
		printk(KERN_DEBUG "th260pcie: StartTransfer: TLP size = %u  TLP count = %u\n", tlpsize, tlpcount);

	if(tlpcount>0xFFFF)
	{
		printk(KERN_DEBUG "th260pcie: StartTransfer: OOPS, tlpcount too large!\n");
		return;
	}

	if(pcard->dmacount != tlpsize * 4 * tlpcount)
	{
		printk(KERN_DEBUG "th260pcie: StartTransfer: OOPS, odd size!\n");
		return; 
	}

	iowrite32(virt_to_phys(pcard->dmabuf), pcard->bar0base + WRITE_ADDR_OFFSET);
	iowrite32(tlpsize                   , pcard->bar0base + WRITE_SIZE_OFFSET);
	iowrite32(tlpcount                  , pcard->bar0base + WRITE_COUNT_OFFSET);
		
	iowrite32(1, pcard->bar0base + DCSR_OFFSET); // enable int and start dma	
}


static ssize_t th260_read(struct file *file,	
			   char *buffer,	// buffer to fill with data 
			   size_t count,	// count of bytes to read   
			   loff_t * offset)
{
	struct th260_cdev* pcard = (struct th260_cdev *)file->private_data;	
	int total_bytes_read = 0;
	unsigned long flags;
	int timeout = ((HZ/2) ? (HZ/2) : 1); // 0.5s but at least one tick
	int rc;
	
	if(count==0) return 0;
	
	if (file->f_flags & O_NONBLOCK)
	  return -EFAULT; // we do not support async calls for now
	    
	if (!_access_ok (VERIFY_WRITE, buffer, count))
	{
	    printk (KERN_WARNING "th260pcie: read: verify error, buf 0x%08lx, count %lu\n",
	    (unsigned long)buffer, (unsigned long)count);
	    return -EFAULT;
	}	
	
	do
	{
	    pcard->bytes_done = 0;
	    pcard->dmacount = MIN(count, BUFFER_SIZE(pcard->dmabuf_order));
	   
	    while (pcard->dmacount)
	    {		
		spin_lock_irqsave(&(pcard->lock),flags);
		    		
		pcard->irq_received = 0; 
		
		th260_dma_start(pcard);
		
		spin_unlock_irqrestore(&(pcard->lock),flags);
			
		rc = wait_event_interruptible_timeout(pcard->wq, pcard->irq_received!=0, timeout);
		if (rc == 0)     // retcode is zero only after timeout 
		{                     
		    printk(KERN_DEBUG "th260pcie: read: timeout!\n");	
		    return -EINTR;
		}
      
		// we are awake now, copy the data 
		if (pcard->bytes_done)
		  if(copy_to_user (buffer, pcard->dmabuf, pcard->bytes_done)) 
		  {
		    printk(KERN_DEBUG "th260pcie: read: copy_to_user failed\n");
		    return -EFAULT;
		  }
      
		if (signal_pending(current)) // we received a signal? 
		{
		  rc = total_bytes_read + pcard->bytes_done;
		  return ((rc) ? (rc) : -EINTR);
		}

		if (pcard->irq_received) 
		{
		    if(th260dbg)
			printk(KERN_DEBUG "th260pcie: read: IRQ received.\n");
		    total_bytes_read += pcard->bytes_done;
		    buffer += pcard->bytes_done;
		    count -= pcard->bytes_done;
		    break;
		}
	    }		
	    
	    if(th260dbg)
		printk(
		      KERN_DEBUG "th260pcie: read:     total_bytes_read %d\n"
		      KERN_DEBUG "th260pcie: read:     bytes_done %d\n"
		      KERN_DEBUG "th260pcie: read:     irq_received %d\n",
		      total_bytes_read, pcard->bytes_done, pcard->irq_received);	    
	    
	} while (count > 0);
	
	return total_bytes_read;
}


static long th260_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    struct th260_cdev* pcard = (struct th260_cdev *)file->private_data;
    uint32_t version = DRVVERSION;
 	 
    switch (cmd)
    {
	case IOCTL_GET_VERSION:  // arg is pointer to 32-bit destination
	    if (!_access_ok(VERIFY_WRITE, (void *)arg, sizeof(uint32_t)))
	    {
		printk(KERN_DEBUG "th260pcie: Invalid user area 0x%08lx\n", arg);
		return -EFAULT;
	    }	  
           if (copy_to_user((uint64_t *)arg, &version, sizeof(uint32_t)))
            {
		printk(KERN_DEBUG "th260pcie: copy_to_user failed 0x%08lx\n", arg);		      
                return -EACCES;
            }
            break;      
      
        case IOCTL_GET_SERIAL:   // arg is pointer to 64-bit destination
	    if (!_access_ok(VERIFY_WRITE, (void *)arg, sizeof(uint64_t)))
	    {
		printk(KERN_DEBUG "th260pcie: Invalid user area 0x%08lx\n", arg);
		return -EFAULT;
	    }
            if (copy_to_user((uint64_t *)arg, &(pcard->serial), sizeof(uint64_t)))
            {
		printk(KERN_DEBUG "th260pcie: copy_to_user failed 0x%08lx\n", arg);	      
                return -EACCES;
            }
            break;
	    
	case IOCTL_GET_BAROFFS:  // arg is pointer to 32-bit destination
	    if (!_access_ok(VERIFY_WRITE, (void *)arg, sizeof(uint32_t)))
	    {
		printk(KERN_DEBUG "th260pcie: Invalid user area 0x%08lx\n", arg);
		return -EFAULT;
	    }	  
           if (copy_to_user((uint64_t *)arg, &(pcard->bar0offset), sizeof(uint32_t)))
            {
		printk(KERN_DEBUG "th260pcie: copy_to_user failed 0x%08lx\n", arg);		      
                return -EACCES;
            }
            break;	  
 	    	    
        default:
            return -EINVAL;
    }
 
    return 0;
}

void th260_vma_open(struct vm_area_struct *area) // will not really be called
{      
}

void th260_vma_close(struct vm_area_struct *area)
{    	
	  struct th260_cdev* pcard = (struct th260_cdev *)area->vm_file->private_data;

	  if(th260dbg)
	  printk(KERN_DEBUG "th260pcie: vma_close: minor=%d  busy=%d\n", pcard->minor, pcard->busy); 
   
	  pcard->busy = 0; // card can now be used by other process
    
}

static struct vm_operations_struct th260_vm_ops = 
{
	  th260_vma_open,
	  th260_vma_close,
};


static int th260_mmap (struct file *file, struct vm_area_struct *vma)
{
	struct th260_cdev* pcard = (struct th260_cdev *)file->private_data;
	unsigned long flags;
	int tmp;

	if(th260dbg)
	    printk(KERN_DEBUG "th260pcie: mmap start: %08lx, end: %08lx, pt_region: %1ld, flags: %08lx\n",
		vma->vm_start, vma->vm_end, vma->vm_pgoff, vma->vm_flags);

	// check if in use by other process, do it under lock to avoid races
	spin_lock_irqsave(&(pcard->lock),flags);
	
	if(th260dbg)
	    printk(KERN_DEBUG "th260pcie: th260_mmap: busy = %d\n", pcard->busy);	
	if(pcard->busy) 
	{
		spin_unlock_irqrestore(&(pcard->lock),flags);
		return -EBUSY; 
	}
	pcard->busy = 1;  	// mark as busy
	spin_unlock_irqrestore(&(pcard->lock),flags);
     
	// check dimension 
	if ((vma->vm_end - vma->vm_start) > PAGE_ALIGN (BAR_0_LEN) )
	{
		printk(KERN_WARNING "th260pcie: dimension check fail: %08lx > %08lx (%08x)\n",
		(vma->vm_end - vma->vm_start), (unsigned long)PAGE_ALIGN (BAR_0_LEN), BAR_0_LEN);
       
		pcard->busy = 0;
		return -EINVAL;
	}

	vma->vm_pgoff = pci_resource_start(pcard->pci_dev, BAR_0);

	if(th260dbg)
	    printk(KERN_DEBUG "th260pcie: mapping BAR_0 physical address %08lx\n", vma->vm_pgoff);
   
	// store the offset for later use by IOCTL_GET_BAROFFS 
	pcard->bar0offset = vma->vm_pgoff & ~PAGE_MASK;
     
	if(th260dbg)
	    printk(KERN_DEBUG "th260pcie: BAR_0 page offset is %08x\n", pcard->bar0offset);

	// finally, map the pages
	vma->vm_pgoff = vma->vm_pgoff >> PAGE_SHIFT; 
	if ((tmp = remap_pfn_range(vma, vma->vm_start, vma->vm_pgoff, 
                           (vma->vm_end - vma->vm_start), vma->vm_page_prot))) 
	{
		printk(KERN_WARNING "th260pcie: error remapping page range, %d\n", tmp);
		pcard->busy = 0;
		return -EAGAIN;
	}

	if(th260dbg)
     		printk(KERN_DEBUG "th260pcie: mmapped: start 0x%08lx ofs 0x%08x len 0x%08lx)\n",
                        vma->vm_start, pcard->bar0offset,(vma->vm_end - vma->vm_start));

	// set up vm_ops to have vma_close called upon release
	vma->vm_ops =  &th260_vm_ops;      
	vma->vm_file = file;

	if(th260dbg)
	    printk(KERN_DEBUG "th260pcie: remap start: %08lx, end: %08lx, offset: %08lx, flags: %08lx\n",
		vma->vm_start, vma->vm_end, vma->vm_pgoff, vma->vm_flags);

	return 0;
}

static void th260_reset(struct th260_cdev* pcard)
{
	// ints disabled and transfers off
	iowrite32(0x800080, pcard->bar0base + DCSR_OFFSET);

	// initiator reset
	iowrite32(1, pcard->bar0base + DCR_OFFSET);
	iowrite32(0, pcard->bar0base + DCR_OFFSET);	
}

// the interrupt handler 
static irqreturn_t th260_interrupt(int irq, void *dev_instance)
{
  	int handled = 0;	
	u32 dcsr;

	struct th260_cdev* pcard = (struct th260_cdev* )dev_instance;
	
	spin_lock(&pcard->lock);

	dcsr = ioread32(pcard->bar0base + DCSR_OFFSET);

	// check if this is our interrupt, otherwise bail out
	if (!(dcsr & BUSMASTERED_READ_DONE))
	{
	    //printk(KERN_DEBUG "th260_interrupt: NOT MINE!\n");
	    goto interrupt_ex;
	}	

	while(dcsr & BUSMASTERED_READ_DONE) // still interrupting?
	{
		dcsr |= 0x00000080; // bit 7 = high: disable int
		iowrite32(dcsr, pcard->bar0base + DCSR_OFFSET);

		// initiator reset to clear interrupt-flag
		iowrite32(1, pcard->bar0base + DCR_OFFSET);
		iowrite32(0, pcard->bar0base + DCR_OFFSET);		

		dcsr = ioread32(pcard->bar0base + DCSR_OFFSET);
	}
	
	handled = 1;
	
	if(th260dbg)
        printk(KERN_INFO "th260pcie: isr: %d bytes done.\n",pcard->dmacount );    	
	
	pcard->bytes_done += pcard->dmacount;
	pcard->dmacount = 0;
	
	pcard->irq_received = 1;  		// set the wakeup condition        
	wake_up_interruptible (&(pcard->wq));	// force check of condition
	
interrupt_ex:
	spin_unlock(&pcard->lock);

	return IRQ_RETVAL(handled);
}


static struct file_operations th260_ops = {
	.owner		= THIS_MODULE,
	.unlocked_ioctl = th260_ioctl,
	.compat_ioctl   = th260_ioctl,
	.mmap		= th260_mmap,
	.read 		= th260_read,
	.open 		= th260_open,
	.release 	= th260_release
};


/**
 * This function is called when a new pci device is associated with a driver
 *
 * return: 0 => this driver does not handle this device
 *         1 => this driver handles this device
 *
 */
static int th260_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
	int ret, minor, order;
	struct cdev *cdev;
	dev_t devno;
	uint32_t dltrsstat;
	union {
		uint64_t allbits;
		uint32_t dwords[2];
		char bytes[8];
	      } serialreg;	
		
	printk(KERN_DEBUG "th260pcie probe\n");

	// add this pci device in th260_cdev
	if ((minor = th260_cdev_add(pdev)) < 0) {
		dev_err(&(pdev->dev), "th260_cdev_add failed\n");
		goto error;
	}
	
	devno = MKDEV(major, minor);
	cdev = cdev_alloc();
	cdev_init(cdev, &th260_ops);
	cdev->owner = THIS_MODULE;

	// register cdev
	ret = cdev_add(cdev, devno, 1);
	if (ret < 0) {
		dev_err(&(pdev->dev), "Can't register character device\n");
		goto error;
	}
	th260_cdev[minor].cdev = cdev;
	
	pci_set_drvdata(pdev, &(th260_cdev[minor])); // will give us quick access to associated entry in th260_cdev

	dev_info(&(pdev->dev), "Registration OK. Major/Minor is %d/%d.\n", MAJOR(devno), MINOR(devno));

	// enable the device
	ret = pci_enable_device(pdev);
	if (ret < 0) 
	{
		dev_err(&(pdev->dev), "Can't enable pci device\n");
		cdev_del(cdev);
		goto error;
	}	

	// request BAR 0
	if (pci_request_region(pdev, BAR_0, DEVICE_NAME) != 0) 
	{
		dev_err(&(pdev->dev), "Failed requesting BAR\n");
		cdev_del(cdev);
		goto error;
	}
	
	// check that BAR 0 is a mem region
	if ((pci_resource_flags(pdev, BAR_0) & IORESOURCE_MEM) != IORESOURCE_MEM) {
		dev_err(&(pdev->dev), "BAR 0 is not a memory region!\n");
		cdev_del(cdev);	
		goto error;
	}

	th260_cdev[minor].bar0base = ioremap(pci_resource_start(pdev, BAR_0), BAR_0_LEN);
	if (!th260_cdev[minor].bar0base) {
		dev_err(&(pdev->dev),"Failed to ioremap BAR 0!\n");
		cdev_del(cdev);
		goto error;		
		}	
	
	// get the serial number (need two 32-bit reads because of bad alignment)
	serialreg.dwords[0] = ioread32(th260_cdev[minor].bar0base + MB_SERIAL_OFFSET);
	serialreg.dwords[1] = ioread32(th260_cdev[minor].bar0base + MB_SERIAL_OFFSET + 4);
	serialreg.bytes[7] = 0;
	dev_info(&(pdev->dev), "Serial = %s\n",serialreg.bytes); 
	th260_cdev[minor].serial = serialreg.allbits;	
		
	// determine maxtlpsize
	dltrsstat = ioread32(th260_cdev[minor].bar0base + TRANS_SIZE_OFFSET);
	th260_cdev[minor].maxtlpsize = 32<<((dltrsstat>>8)&7);
	
	dev_info(&(pdev->dev), "Maxtlpsize = %u\n", th260_cdev[minor].maxtlpsize);
	if ((th260_cdev[minor].maxtlpsize<32)||(th260_cdev[minor].maxtlpsize>4096))
	{
		dev_err(&(pdev->dev),"Unexpected maxtlpsize!\n");
		cdev_del(cdev);	
		goto error;	
	}
	
	th260_reset(&th260_cdev[minor]); // interrupts disabled etc
	
	// set up for DMA	
	// We want a large DMA buffer but must try and see what we get.
	// The largest we can use is 512kB so we start there and decrement if need be
	for(order = get_order(512*1024); order >= 0; order--)
	{
		th260_cdev[minor].dmabuf_order = order;
		th260_cdev[minor].dmabuf = (char*)__get_free_pages(GFP_KERNEL|GFP_DMA,order);
		if(th260_cdev[minor].dmabuf)
		  break;
		else
		  dev_info(&(pdev->dev),"Cannot allocate DMA memory of order %d\n",order);
	}
	if (th260_cdev[minor].dmabuf==NULL)
	{
		dev_err(&(pdev->dev),"Cannot allocate DMA memory!\n");
		cdev_del(cdev);
		goto error;	
	}	
	else
	{	
		dev_info(&(pdev->dev),"Allocated %lu bytes for DMA buffer.\n",
			 BUFFER_SIZE(th260_cdev[minor].dmabuf_order));
	}
	
	pci_set_master(pdev);
	
	if (dma_set_mask(&(pdev->dev), DMA_BIT_MASK(32))
	    || dma_set_coherent_mask(&(pdev->dev), DMA_BIT_MASK(32))) 
		{
			dev_err(&(pdev->dev), "Failed to set dma mask!\n");
			iounmap (th260_cdev[minor].bar0base);
			cdev_del(cdev);
			goto error;
		}	
		
	// set up the interrupt handler
	ret = request_irq(pdev->irq, th260_interrupt, IRQF_SHARED, DEVICE_NAME, (void*)&(th260_cdev[minor]));
	if (ret) {
		dev_err(&(pdev->dev), "Error requesting IRQ");
		iounmap (th260_cdev[minor].bar0base);
		cdev_del(cdev);		
		goto error;
	}
	
	// create device node in /dev
	device_create(th260_class, NULL, devno, NULL, "th260pcie%d", minor);	
	
	return 0; // success

error:
	pci_set_drvdata(pdev, NULL);
	pci_disable_device(pdev);
	
	return -ENODEV; // fail
}

static void th260_remove(struct pci_dev *pdev)
{
	struct th260_cdev* pcard = pci_get_drvdata(pdev);
		
	if(!pcard)
	{
	      if(th260dbg)
		  dev_info(&(pdev->dev), " th260_remove: skip on pcard == NULL\n"); 
	      return;
	}
	
	if(!pcard->pci_dev)
	{
	      if(th260dbg)
		  dev_info(&(pdev->dev), " th260_remove: skip on pcard->pci_dev == NULL\n"); 
	      return;
	}
	
	dev_info(&(pdev->dev), "REMOVING\n"); 
	
	if (pcard->cdev != NULL) 
		cdev_del(pcard->cdev);
	
	// remove device node
	device_destroy(th260_class, MKDEV(major, pcard->minor));
			
	// reset to disable interrupts etc
	th260_reset(pcard);	

	free_irq(pdev->irq,(void*)pcard);	
	
	iounmap(pcard->bar0base);
		
	pci_release_region(pdev, BAR_0);
	
	if(pcard->dmabuf)
	  free_pages ((unsigned long)(pcard->dmabuf), pcard->dmabuf_order);
	
	th260_cdev_del(pdev);		
}


static struct pci_driver th260_driver = {
	.name 		= DEVICE_NAME,
	.id_table 	= th260_ids,
	.probe 		= th260_probe,
	.remove 	= th260_remove,
};


// called when the module is loaded
static int __init pci_init_module(void)
{
	int ret;
	dev_t devno;

	printk(KERN_DEBUG "th260pcie init\n");
	
	// register a class for device nodes
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 4, 0) 
	th260_class = class_create(DEVICE_NAME); 
#else 
	th260_class = class_create(THIS_MODULE, DEVICE_NAME);
#endif 	
	if (IS_ERR(th260_class))
	{
		printk(KERN_ERR "th260pcie: can't register class for device nodes. \n");	  
		return PTR_ERR(th260_class);
	}
	// dynamically allocate a major number and a range 0..MAX_DEVICES of minor numbers
	ret = alloc_chrdev_region(&devno, 0, MAX_DEVICES, "th260pcie_devs");
	if (ret < 0) {
		printk(KERN_ERR "th260pcie: can't alloc_chrdev_region. \n");
		class_destroy(th260_class);
		return ret;
	}
	if(MINOR(devno)!=0)
	{
		printk(KERN_ERR "th260pcie: can't alloc requested minor numbers \n");
		unregister_chrdev_region(devno, MAX_DEVICES); // free major/minor numbers 
		class_destroy(th260_class);
		return -ENODEV;
	}	  
	  	  
	// If the alloc_chrdev_region succeeded then the devno variable will have the combination 
	// major number that the kernel has allocated to us and the first minor we had selected.
	// To extract the major number from the dev_no we can use the macro MAJOR. 
	major = MAJOR(devno);

	th260_cdev_init();

	ret = pci_register_driver(&th260_driver);
	if (ret < 0) {
		unregister_chrdev_region(devno, MAX_DEVICES); // free major/minor numbers 
		class_destroy(th260_class);
		printk(KERN_ERR "th260pcie: can't register pci driver\n");
		return ret;
	}

	return 0;
}

// called when the module is unloaded
static void pci_exit_module(void)
{
  	int i;

	// This loop doing th260_remove is a bit of a hack. We should not need to call 
	// our remove function explicitly. Normally it gets called via callback upon
	// pci_unregister_driver. However, on some kernels this did not seem to happen.
	// (seen on OpenSuse 13.1 with 3.11.6-4-desktop)
	// On the other hand, because on other kernels it DOES get called via callback
	// we ensure inside th260_remove that it does not try to do its job twice.	
	for(i=0; i< MAX_DEVICES; i++) {
		if (th260_cdev[i].pci_dev != NULL)
			th260_remove(th260_cdev[i].pci_dev); 
	}

	unregister_chrdev_region(MKDEV(major,th260_cdev[0].minor), MAX_DEVICES);
	
	class_destroy(th260_class);
	
	pci_unregister_driver(&th260_driver);

	printk(KERN_DEBUG "th260pcie exit\n");	
}

module_init(pci_init_module);
module_exit(pci_exit_module);
