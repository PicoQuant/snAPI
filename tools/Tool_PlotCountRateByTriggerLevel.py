import sys
import os
import time 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snAPI.Main import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg',force=True)
print("Switched to:",matplotlib.get_backend())

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