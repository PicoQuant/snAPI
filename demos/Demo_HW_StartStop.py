from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Hardware-triggered start and stop of a time trace measurement
# =============================================================
# This demo demonstrates how a time trace measurement can be started and stopped
# by external hardware trigger signals on a PicoQuant time tagging device.
#
# The script initializes the device in T2 mode, loads an ini configuration file,
# and configures the measurement control so that a trigger signal on C1 starts
# the acquisition and a trigger signal on C2 stops it.
#
# Setup:
# Connect the external start trigger to control input C1 and the external stop
# trigger to control input C2. After the measurement has been armed in software,
# the acquisition begins when the selected edge is detected on C1 and ends when
# the selected edge is detected on C2.
#
# During acquisition, the script repeatedly reads the time trace data and plots
# the count rates of the sync input and all enabled detector channels.
#
# This is useful for measurements where both the beginning and the end of the
# acquisition are defined by external hardware, for example event-based
# experiments, triggered measurement windows, or synchronization with an external
# control sequence.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    # a trigger signal on C1 starts and one on C2 stops the measurement
    sn.device.setMeasControl(MeasControl.C1StartC2Stop, startEdge = 1, stopEdge = 1)
    sn.loadIniConfig("config\MH.ini")
    
    # configure timetrace
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    # prepare measurement for triggered start and stop
    sn.timeTrace.measure(waitFinished=False, savePTU=False)
    
    plt.figure(f'Figure: {sn.deviceConfig["Model"]}')
    while True: 
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData() 
        plt.clf()
        plt.plot(times, counts[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(times, counts[c], linewidth=2.0, label=f'chan{c}')

        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.legend()
        plt.title(f'TimeTrace Master {sn.deviceConfig["ID"]}')
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
