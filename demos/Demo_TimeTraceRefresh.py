from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
from threading import Timer
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    
    # temporarily enable logging of configuration
    sn.setLogLevel(LogLevel.Config, True)
    # set the configuration for your device type
    sn.loadIniConfig(r"config\TH260N.ini")
    sn.setLogLevel(LogLevel.Config, False)
    sn.setLogLevel(LogLevel.Api, True)
    sn.setLogLevel(LogLevel.Device, True)
    
    sn.timeTrace.setSequenceMode(sequenceMode=SequenceMode.Timer, wait4newData=False, param = 1) # 1s
    sn.timeTrace.setNumBins(1000)
    sn.timeTrace.setHistorySize(1)
    sn.timeTrace.measure(acqTime=10000, waitFinished=False, savePTU=False)
    
    while True:
        if sn.timeTrace.isFinished():
            break
        data, times = sn.timeTrace.getData()
        
        plt.pause(.1)
        plt.clf()
        plt.plot(times, data[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(times, data[c], linewidth=2.0, label=f'chan{c}') 

        plt.yscale('log')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Time Trace")
    
    plt.show(block=True)
