from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# This demo starts the data acquisition at the slave and should be executed first.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice("1045483")
    
    # init Slave and init Master must not happen at the same time
    sn.initDevice(MeasMode.T2, RefSource.Wr_Slave_Harp)
    sn.device.setMeasControl(MeasControl.WrMaster2Slave)
    sn.loadIniConfig("config\MH.ini")
    
    # configure timetrace
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)

    # This enables the measurement on the slave.
    sn.setPTUFilePath("C:\Data\PicoQuant\slave.ptu")
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=True)
    
    # Now the slave waits for the start of the measurement of the master.
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
        plt.title(f'TimeTrace Slave {sn.deviceConfig["ID"]}')
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
