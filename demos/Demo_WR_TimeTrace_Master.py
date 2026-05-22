from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# White Rabbit time trace — master unit
# =====================================
# This demo demonstrates how to acquire a time trace on the master unit of a
# White Rabbit synchronized pair of PicoQuant time tagging devices.
#
# The master is initialized in T2 mode with `RefSource.Wr_Master_Harp` and uses
# `MeasControl.WrMaster2Slave`. It is responsible for starting the synchronized
# measurement on both the master and the already prepared slave unit.
#
# Setup:
# The White Rabbit master and slave must already be configured and connected.
# The slave time trace demo should be started first so that the slave is
# initialized and waiting for the master's start command. The master is then
# initialized, configured from an ini file, and prepared for time trace
# acquisition.
#
# When the master starts the measurement, the acquisition on both units begins
# synchronously over the White Rabbit link. The photon stream from the master can
# optionally be saved to a PTU file while the time trace is displayed.
#
# During acquisition, the script repeatedly reads and plots the count rates of
# the sync input and all enabled detector channels of the master unit. This is
# useful for monitoring the master-side signals in a synchronized White Rabbit
# measurement.

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
    sn.setPTUFilePath(r"C:\Data\PicoQuant\master.ptu")
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
