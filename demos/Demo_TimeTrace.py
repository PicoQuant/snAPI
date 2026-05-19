from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Time trace measurement from a time tagging device
# =================================================
# This demo demonstrates how to acquire and display a time trace from photon
# events recorded with a PicoQuant time tagging device.
#
# The script initializes the device in T3 mode and configures the time trace
# module with a selected number of time bins and history size. The time trace
# accumulates the count rates of the sync input and all enabled detector channels
# as a function of measurement time.
#
# Setup:
# The device can be configured from an ini file or by setting trigger parameters
# directly in the script. The time trace parameters define how many time bins are
# displayed and how much history is kept during acquisition.
#
# During acquisition, the script repeatedly reads the current time trace data and
# plots the count rates on a logarithmic scale. The photon stream can optionally
# be saved as a PTU file while the time trace is being displayed.
#
# This is useful for monitoring detector signals in real time, checking count
# rates before or during a measurement, optimizing optical alignment, and
# verifying that all channels receive the expected signal levels.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.setLogLevel(LogLevel.Config, True)
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    
    # alternatively read data from file
    sn.setLogLevel(LogLevel.DataFile, True)
    #sn.getFileDevice(r"\mnt\d\Data\PicoQuant\CW_Shelved.ptu") # T2 File
    #sn.getFileDevice(r"D:\Data\PicoQuant\CW_Shelved.ptu") # T2 File
    
    # enable this to get info about loading config
    sn.setLogLevel(logLevel=LogLevel.Config, onOff=True)
    #sn.loadIniConfig(r"config\MH.ini")
    
    numChans = sn.deviceConfig["NumChans"]
    triggerMode = TrigMode.Edge if sn.deviceConfig["SyncTrigMode"] == "Edge" else TrigMode.CFD
    
    if dontUseSettingsFromConfigIni := False:
        #set input CFD trigger
        if triggerMode == TrigMode.CFD: 
            #sn.device.setSyncTrigMode(TrigMode.CFD)
            sn.device.setInputTrigMode(-1, TrigMode.CFD)
            sn.device.setSyncCFD(100, 0)
            sn.device.setInputCFD(-1, 100, 0)
        
        #set input edge trigger
        if triggerMode == TrigMode.Edge: 
            #sn.device.setSyncTrigMode(TrigMode.Edge)
            sn.device.setInputTrigMode(-1, TrigMode.Edge)
            sn.device.setSyncEdgeTrig(-100, 0)
            sn.device.setInputEdgeTrig(-1, -50, 0)
        
    # configure timetrace
    sn.timeTrace.setNumBins(1000)
    sn.timeTrace.setHistorySize(1)
    
    # you can set a custom file name or path
    sn.setPTUFilePath("MyFileName.ptu")
    
    # measure 10s
    sn.timeTrace.measure(1000, waitFinished=False, savePTU=True)
    
    while True: 
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData(normalized=True) 
        plt.clf()
        plt.plot(times, counts[0], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(times, counts[c], linewidth=2.0, label=f'chan{c}')

        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.yscale('log', base=10, nonpositive='clip')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
