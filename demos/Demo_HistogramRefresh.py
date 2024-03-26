from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
from threading import Timer
import time

if(__name__ == "__main__"):

    sn = snAPI(libType=LibType.TH260)
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    # temporarily enable logging of configuration
    sn.setLogLevel(LogLevel.Config, True)
    # set the configuration for your device type
    sn.loadIniConfig("config\TH.ini")
    sn.setLogLevel(LogLevel.Config, False)
    
    # change histogram parameter in T2 mode
    #sn.histogram.setRefChannel(0)
    #sn.histogram.setBinWidth(1)
    sn.histogram.measure(acqTime=0, waitFinished=False, savePTU=True)
    
    while True:
        finished = sn.histogram.isFinished()
        data, bins = sn.histogram.getData()
        
        # 1s refresh time
        plt.pause(1)
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(bins, data[c], linewidth=2.0, label=f'chan{c}')

        plt.yscale('log')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Histogram")
        
        # clear measure data
        sn.histogram.clearMeasure()
        if finished:
            sn.setLogLevel(LogLevel.Manipulators, True)
            break
    
    plt.show(block=True)
