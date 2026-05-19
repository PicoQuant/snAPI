import sys
import os
import time 

from snAPI.Main import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg',force=True)
print("Switched to:",matplotlib.get_backend())

# Count rate scan by trigger level
# ======================================
# This tool helps determine suitable trigger or discriminator levels for a
# PicoQuant time tagging device by measuring the count rate while sweeping the
# trigger level.
#
# The script initializes the device, loads an ini configuration file, and then
# scans the trigger level over a defined voltage range. For each trigger level,
# the same setting is applied to the sync input and all detector channels, using
# either edge triggering or CFD triggering depending on the loaded device
# configuration.
#
# Setup:
# The device configuration is loaded from an ini file. The trigger-level scan
# range is defined directly in the script by the start, stop, and step values of
# the loop. These values should be adapted to the signal levels and trigger mode
# used in the measurement setup.
#
# During the scan, the script reads the count rates for the sync input and all
# detector channels with `getCountRates`, prints the values, and plots the count
# rate as a function of the trigger level.
#
# This is useful for finding a trigger level that separates the signal from
# noise, checking signal amplitudes, optimizing detector channel settings, and
# preparing a stable configuration before running a measurement.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    sn.loadIniConfig("config\PH330_Edge.ini")
    
    numChans = sn.deviceConfig["NumChans"]
    x, sync =  [],[]
    chan = [[] for _ in range(numChans)] 

    plt.show(block=False)
    init = True
    # set start, stop, step for the trigger level scan
    for trigLvl in range(-500, 0, 1):
        if sn.deviceConfig["SyncTrigMode"] == "Edge":
            sn.device.setInputEdgeTrig(-1, trigLvl, 0)
            sn.device.setSyncEdgeTrig(trigLvl, 0)
        elif sn.deviceConfig["SyncTrigMode"] == "CFD":
            sn.device.setInputCFD(-1, trigLvl, 0)
            sn.device.setSyncCFD(trigLvl, 0)
        
        if init:
            init = False
            time.sleep(0.1)
            
        cntRs = sn.getCountRates()
        
        sn.logPrint(trigLvl, cntRs)
        x.append(trigLvl)
        sync.append(cntRs[0])
        for i in range(numChans):
            chan[i].append(cntRs[i+1])
        
        plt.clf()
        plt.plot(x, chan[0], linewidth=2.0, label='sync')
        for i in range(numChans):
            plt.plot(x, chan[i], linewidth=2.0, label=f"chan{str(i)}")

        plt.xlabel('Trigger Level [mV]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Counts / Trigger Level")
        plt.pause(0.2)
        
    plt.show(block=True)
