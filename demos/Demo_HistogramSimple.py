from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

if(__name__ == "__main__"):
    
    # select the device library
    sn = snAPI(libType=LibType.HH)
    # get first available device
    sn.getDevice()
    sn.setLogLevel(logLevel=LogLevel.DataFile, onOff=True)
    
    #initialize the device
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig("config\HH.ini")
    
    # start histogram measurement
    sn.histogram.measure(acqTime=1000,savePTU=True)
    
    # get the data
    data, bins = sn.histogram.getData()
    
    # plot the histogram
    if len(data):
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(bins, data[c], linewidth=2.0, label=f'chan{c}')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Counts / Time")
        plt.pause(0.01)

    plt.show(block=True)