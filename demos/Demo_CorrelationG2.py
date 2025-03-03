from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDeviceIDs()
    #sn.getDevice()
    sn.getFileDevice(r"D:\Data\PicoQuant\CW_Shelved.ptu") # T2 File
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig("config\MH.ini")
    
    # 1. shift the signals to max correlation max at tau = 0
    #sn.device.setInputChannelOffset(1, 1588)
    
    # 2. set windowSize and startTime
    sn.correlation.setG2Parameters(1, 2, 50000, 50)
    sn.correlation.measure(1000,savePTU=False)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getG2Data()
        time.sleep(.3)
        
        plt.clf()
        plt.plot(bins, data, linewidth=2.0, label='g(2)')
        plt.xlabel('Time [s]')
        plt.ylabel('g(2)')
        plt.legend()
        plt.title("g(2)")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
