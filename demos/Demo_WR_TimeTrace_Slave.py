from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# White Rabbit time trace — slave unit
# ====================================
# This demo demonstrates how to prepare and monitor a time trace on the slave
# unit of a White Rabbit synchronized pair of PicoQuant time tagging devices.
#
# The slave is initialized in T2 mode with `RefSource.Wr_Slave_Harp` and uses
# `MeasControl.WrMaster2Slave`. After the measurement is armed, the slave waits
# for the synchronized start command from the master unit.
#
# Setup:
# The White Rabbit master and slave must already be configured and connected.
# This slave time trace demo should be started before the corresponding master
# time trace demo. The slave is initialized, configured from an ini file, and
# prepared for time trace acquisition.
#
# Once the master starts the measurement, the slave begins acquiring data
# synchronously over the White Rabbit link. The photon stream from the slave can
# optionally be saved to a PTU file while the time trace is displayed.
#
# During acquisition, the script repeatedly reads and plots the count rates of
# the sync input and all enabled detector channels of the slave unit. This is
# useful for monitoring the slave-side signals in a synchronized White Rabbit
# measurement and confirming that the slave follows the master-controlled
# acquisition.

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
    sn.setPTUFilePath(r"C:\Data\PicoQuant\slave.ptu")
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
