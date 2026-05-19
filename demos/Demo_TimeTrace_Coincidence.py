from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Time trace measurement with coincidence channels
# ================================================
# This demo demonstrates how virtual coincidence channels can be added to a time
# trace measurement with snAPI.
#
# The script initializes a PicoQuant time tagging device in T2 mode and creates
# coincidence channels from two detector channels, Ch1 and Ch2. Photon events on
# these channels are tested against the selected coincidence window, and matching
# events are counted in additional virtual channels.
#
# Setup:
# The device configuration is loaded from an ini file. Two coincidence
# manipulators are created with different counting modes: `CountAll` counts all
# coincidence combinations within the selected window, while `CountOnce` counts
# only one coincidence event per matching group.
#
# During acquisition, the script reads the time trace data and plots the count
# rates of the sync input, the original detector channels, and the generated
# coincidence channels together.
#
# This is useful for monitoring coincidence rates in real time, comparing raw
# detector count rates with coincidence signals, and checking coincidence-window
# settings during experiments involving correlated photon events.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice("C:\Data\PicoQuant\default.ptu")
    
    # alternatively read data from file
    sn.setLogLevel(LogLevel.DataFile, True)
    sn.initDevice(MeasMode.T2)
    
    # enable this to get info about loading config
    #sn.setLogLevel(logLevel=LogLevel.Config, onOff=True)
    sn.loadIniConfig("config\HH.ini")
    
    coincidenceAll = sn.manipulators.coincidence([1,2], windowTime=1e7, mode=CoincidenceMode.CountAll, keepChannels=True)
    coincidenceOnce = sn.manipulators.coincidence([1,2], windowTime=1e7, mode=CoincidenceMode.CountOnce, keepChannels=True)
    # measure 10s
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)
    
    while True: 
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData() 
        plt.clf()
        plt.plot(times, counts[0], linewidth=2.0, label='sync')
        plt.plot(times, counts[1], linewidth=2.0, label='chan1')
        plt.plot(times, counts[2], linewidth=2.0, label='chan2')
        plt.plot(times, counts[coincidenceAll], linewidth=2.0, label='coincidenceAll')
        plt.plot(times, counts[coincidenceOnce], linewidth=2.0, label='coincidenceOnce')

        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
