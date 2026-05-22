from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

# Second-order correlation measurement with two detector channels
# ===============================================================
# This demo demonstrates how a second-order correlation measurement, g(2), can
# be acquired and plotted from photon events recorded with a time tagging device
# or from a PTU file.
#
# The script configures two detector channels for correlation analysis and starts
# a g(2) measurement. The correlation module calculates the coincidence rate as a
# function of the time delay tau between photon events on the two channels.
#
# Setup:
# The device is initialized in T3 mode and configured from an ini file. If needed,
# input channel offsets can be adjusted so that the correlation feature is
# centered at tau = 0. The g(2) parameters define the detector channels, the
# correlation window, the bin width, and the start time used for the analysis.
#
# During acquisition, the script repeatedly reads the correlation data and plots
# the resulting g(2)(tau) curve.
#
# This is useful for experiments that analyze photon statistics and temporal
# correlations, for example antibunching or bunching measurements, single-photon
# source characterization, and timing checks between two detector channels.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDeviceIDs()
    sn.getDevice()
    #sn.getFileDevice(r"D:\Data\PicoQuant\CW_Shelved.ptu") # T2 File
    #sn.getFileDevice(r"\mnt\d\Data\PicoQuant\CW_Shelved.ptu") # T2 File

    sn.initDevice(MeasMode.T2)
        
    # set the configuration for your device type
    sn.loadIniConfig("config\MH.ini")
    
    # 1. shift the signals to max correlation max at tau = 0
    sn.device.setInputChannelOffset(1, 1588)
    
    # only process data from 70s to end of file 
    sn.manipulators.subStream(70)
    
    # 2. set windowSize and startTime
    sn.correlation.setG2Parameters(1, 2, 500000, 250, True)
    sn.correlation.measure(0,savePTU=False)

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
