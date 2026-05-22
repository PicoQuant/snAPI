from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
from threading import Timer
import time

# Live-refresh histogram from photon arrival times
# ================================================
# This demo demonstrates how a histogram measurement can be acquired and
# refreshed during acquisition from photon events recorded with a PicoQuant time
# tagging device.
#
# The script initializes the device, loads an ini configuration file, and
# configures a histogram measurement with a selected reference channel, bin
# width, and number of bins. Photon arrival times are accumulated relative to the
# reference channel and displayed as time-resolved histograms for the sync input
# and all enabled detector channels.
#
# Setup:
# The device configuration is loaded from an ini file. The histogram parameters
# define the reference channel, the temporal resolution of the histogram bins,
# and the total histogram range.
#
# During acquisition, the script repeatedly reads the current histogram data and
# plots the result on a logarithmic count scale. After each refresh, the
# accumulated measurement data are cleared so that the plot shows only the newly
# acquired data for the latest update interval.
#
# This is useful for monitoring photon arrival-time distributions in real time,
# checking timing alignment between channels, optimizing measurement settings,
# and observing changes in the signal during an ongoing experiment.

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
    
    sn.histogram.setSequenceMode(sequenceMode=SequenceMode.Timer, wait4newData=True, param = 1) # 1s
    #sn.histogram.setSequenceMode(sequenceMode=SequenceMode.Counts, wait4newData=True, param = 5000000) # 5M counts
    # change histogram parameter in T2 mode
    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(100)
    sn.histogram.setNumBins(2000)
    sn.histogram.measure(acqTime=10000, waitFinished=False, savePTU=False)
    
    while True:
        if sn.histogram.isFinished():
            break
        data, bins = sn.histogram.getData()
        if(len(data) == 0):
            break
        
        # 1s refresh time
        plt.pause(.1)
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(bins, data[c], linewidth=2.0, label=f'chan{c}')

        plt.yscale('log')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Histogram")
    
    plt.show(block=True)
