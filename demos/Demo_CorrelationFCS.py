from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI(libType=LibType.HH)
    sn.getDeviceIDs()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig("config\HH.ini")
    
    # 1. shift the signals to max correlation max at tau = 0
    #sn.device.setInputChannelOffset(1, 1564)
    
    # 2. set windowSize and startTime
    sn.correlation.setFCSParameters(1, 2, 1e10, 1e5)
    sn.correlation.measure(100,savePTU=True)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getFCSData()
        time.sleep(.3)
        
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='AB')
        plt.plot(bins, data[1], linewidth=2.0, label='BA')
        plt.xlabel('Time [s]')
        plt.xscale('log')
        plt.ylabel('FCS')
        #plt.yscale('log')
        plt.legend()
        plt.title("FCS")
        plt.pause(0.1)
        
        if finished:
            break

    plt.show(block=True)    
