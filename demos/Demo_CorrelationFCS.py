from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDeviceIDs()
    sn.getFileDevice(r"D:\Data\PicoQuant\OpenCLTest\Atto655+Cy5_diff_FCS+FLCS_Conv.ptu")
    #sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig(r"config\MH.ini")
    
    # 1. shift the signals to max correlation max at tau = 0
    #sn.device.setInputChannelOffset(1, 1564)
    
    # 2. set windowSize and startTime
    sn.correlation.setFFCSParameters(1, 2, 1e6, 1e12, 100)
    sn.correlation.measure(2000,savePTU=False)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getFCSData()
        time.sleep(.1)
        
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='AA')
        plt.plot(bins, data[1], linewidth=2.0, label='AB')
        plt.plot(bins, data[2], linewidth=2.0, label='BB')
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
