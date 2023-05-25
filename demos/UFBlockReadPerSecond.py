from snAPI.Main import *
import time

if(__name__ == "__main__"):
    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\test2.ptu")
    sn.initDevice(MeasMode.T3)
    sn.device.setSyncChannelEnable(1)
    sn.device.setInputChannelEnable(0,1)
    # `sn.device.setInputChannelEnable(1,1)` is enabling input channel 1 of the device being used
    # by the code. This means that the device will be able to receive input signals from that channel
    # during the measurement.
    sn.device.setInputChannelEnable(1,1)
    sn.device.setInputChannelEnable(2,1)
    #sn.device.setInputChannelEnable(3,1)
    size = 64*1024*1024
    sn.unfold.startBlock(1000000, size)

    to = time.time()
    ti = to
    while True:
        time.sleep(0.1)
        times, channels = sn.unfold.getBlock()
        numRead = sn.unfold.numRead()
        if numRead > 0:
            tn = time.time()
            rate = numRead / (tn - to) / 1000000
            to = tn
            sn.logPrint(f"{Color.On_Yel}{numRead} records read! ({rate:4.1f} Mctns/s)")
        
        if sn.unfold.isFinished() and numRead == 0:
                break

