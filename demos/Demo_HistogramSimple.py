from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Simple histogram measurement from photon arrival times
# ======================================================
# This demo demonstrates how to acquire a basic histogram measurement from
# photon events recorded with a PicoQuant time tagging device.
#
# The script initializes the device, loads an ini configuration file, and
# configures a histogram measurement with a selected reference channel, bin
# width, and number of bins. Photon arrival times are accumulated relative to
# the reference channel and returned as time-resolved histograms for the sync
# input and all enabled detector channels.
#
# Setup:
# The device configuration is loaded from an ini file. The histogram parameters
# define the reference channel, the temporal resolution of the histogram bins,
# and the total histogram range.
#
# The measurement is started for a fixed acquisition time and runs until it has
# finished. The acquired photon stream can optionally be saved as a PTU file.
#
# After the measurement, the script reads the histogram data and plots the result
# on a logarithmic count scale. This is useful as a compact starting point for
# time-resolved measurements, checking photon arrival-time distributions, and
# verifying the timing alignment between channels.

if(__name__ == "__main__"):
    
    # select the device library
    sn = snAPI()
    # get first available device
    sn.getDevice()
    sn.setLogLevel(logLevel=LogLevel.DataFile, onOff=True)
    
    #initialize the device
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig("config\MH.ini")
    
    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(100)
    sn.histogram.setNumBins(1000)
    # start histogram measurement
    sn.histogram.measure(acqTime=1000, waitFinished=True, savePTU=True)
    
    # get the data
    data, bins = sn.histogram.getData()
    
    # plot the histogram
    if len(data):
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(bins, data[c], linewidth=2.0, label=f'chan{c}')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts', )
        plt.yscale('log', base=10, nonpositive='clip')
        plt.legend()
        plt.title("Counts / Time")
        plt.pause(0.01)

    plt.show(block=True)
