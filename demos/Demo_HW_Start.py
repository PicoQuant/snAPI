from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Hardware-triggered start of a time trace measurement
# ====================================================
# This demo demonstrates how a time trace measurement can be prepared in snAPI
# and started by an external hardware trigger on a PicoQuant time tagging device.
#
# The script initializes the device in T2 mode, loads an ini configuration file,
# and configures the measurement control so that a trigger signal on control
# input C1 starts the measurement.
#
# Setup:
# Connect the external start trigger to control input C1. After the measurement
# has been armed in software, the time trace acquisition starts when the trigger
# is detected on C1 and then runs for the selected acquisition time.
#
# During acquisition, the script repeatedly reads the time trace data and plots
# the count rates of the sync input and all enabled detector channels.
#
# This is useful for measurements where the acquisition should be synchronized
# to an external event, for example a laser trigger, experiment sequence, or
# external control system.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    # a trigger signal on C1 starts the measurement
    sn.device.setMeasControl(MeasControl.C1StartCtcStop)
    sn.loadIniConfig("config\MH.ini")
    
    # configure timetrace
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    # prepare measurement for triggered start (stop after 10s)
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)
    
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
