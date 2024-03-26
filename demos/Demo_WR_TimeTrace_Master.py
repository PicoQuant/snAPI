from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# This demo starts the data acquisition at the master and should be executed after the slave is
# initialized and the measurement is started on the slave.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice("1000002")
    
    # Init Slave and init Master must not happen at the same time!
    sn.initDevice(MeasMode.T2, RefSource.Wr_Master_Harp)
    sn.device.setMeasControl(MeasControl.WrMaster2Slave)
    sn.loadIniConfig("config\MH.ini")
    
    # configure timetrace
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)

    # Now the master starts the measurement of itself and the slave synchronously
    # over White Rabbit.
    sn.setPTUFilePath("C:\Data\PicoQuant\master.ptu")
    # The line `sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)` is initiating a
    # measurement using the time trace feature of the device.
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=True)
    
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
