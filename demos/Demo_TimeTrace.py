from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

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
