from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

# Fluorescence correlation spectroscopy with two detector channels
# ================================================================
# This demo demonstrates how fluorescence correlation spectroscopy (FCS) data
# can be acquired and plotted from photon events recorded with a time tagging
# device or from a PTU file.
#
# The script configures two detector channels for FCS analysis and starts a
# correlation measurement. The correlation module calculates the autocorrelation
# curves for the individual channels as well as the cross-correlation between
# them.
#
# Setup:
# The device is initialized in T3 mode and configured from an ini file. If needed,
# input channel offsets can be adjusted so that the correlation maximum is
# centered at tau = 0. The FCS parameters define the detector channels, the
# correlation window, and the start time used for the analysis.
#
# During acquisition, the script repeatedly reads the FCS data and plots the
# resulting AA, AB, and BB correlation curves on a logarithmic time axis.
#
# This is useful for FCS applications such as studying molecular diffusion,
# concentration fluctuations, and dynamics in fluorescence signals, as well as
# for checking detector alignment and timing in two-channel correlation
# measurements.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDeviceIDs()
    #sn.getFileDevice(r"\mnt\d\Data\PicoQuant\OpenCLTest\Atto655+Cy5_diff_FCS+FLCS_Conv.ptu")
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    
    # set the configuration for your device type
    sn.loadIniConfig(r"config\MH.ini")
    
    # 1. shift the signals to max correlation max at tau = 0
    #sn.device.setInputChannelOffset(1, 1564)
    
    # 2. set windowSize and startTime
    sn.correlation.setFFCSParameters(1, 2, 1e6, 1e12, 100)
    sn.correlation.measure(2000,savePTU=False, waitFinished=True)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getFCSData()
        time.sleep(.1)
        
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='AA')
        plt.plot(bins, data[1], linewidth=2.0, label='AB')
        plt.plot(bins, data[2], linewidth=2.0, label='BB')
        plt.xlabel('Time [s]')
        plt.xscale('log')
        plt.ylabel('FCS')
        #plt.yscale('log')
        plt.legend()
        plt.title("FCS")
        plt.pause(0.1)
        
        if finished:
            break

    plt.show(block=True)    
