from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Hardware-gated time trace measurement
# =====================================
# This demo demonstrates how a time trace measurement can be controlled by an
# external gate signal on a PicoQuant time tagging device.
#
# The script initializes the device in T2 mode, loads an ini configuration file,
# and configures the measurement control so that the signal level on control
# input C1 gates the acquisition.
#
# Setup:
# Connect the external gate signal to control input C1. A low-to-high transition
# starts the measurement, and the measurement remains active while the gate
# signal is high. When the signal on C1 goes low again, the acquisition is
# paused or stopped according to the selected hardware control mode.
#
# During acquisition, the script repeatedly reads the time trace data and plots
# the count rates of the sync input and all enabled detector channels.
#
# This is useful for experiments where photon events should only be recorded
# during defined time windows, for example during externally controlled
# illumination periods, sample excitation intervals, or repeated experimental
# cycles.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    # a trigger signal on C1 starts and holds the measurement
    # a low to high slope starts the measurement until the signal on the control connector Pin C1
    # is getting low again. 
    sn.device.setMeasControl(MeasControl.C1Gated, 1, 0)
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
