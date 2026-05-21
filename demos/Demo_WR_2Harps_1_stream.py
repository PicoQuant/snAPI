from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# White Rabbit synchronized devices — combined histogram stream
# =============================================================
# This demo demonstrates how photon events from two White Rabbit synchronized
# PicoQuant time tagging devices can be combined into a single histogram stream.
#
# The master and slave units are initialized in T2 mode with their corresponding
# White Rabbit reference sources. The master controls the synchronized
# measurement start and stop, while selected channels from the slave are imported
# into the master's data stream.
#
# Setup:
# The two units must be configured for White Rabbit operation beforehand and
# connected via a White Rabbit fiber link. The device IDs for the master and
# slave are selected in the script. The master is initialized with
# `RefSource.Wr_Master_Harp`, the slave with `RefSource.Wr_Slave_Harp`, and both
# devices use `MeasControl.WrMaster2Slave`.
#
# The slave channels are imported into the master stream with
# `sn.manipulators.importStream(..., remoteStartStop=True)`. This enables the
# master to start and stop the synchronized acquisition on both units.
#
# During acquisition, the script reads the histogram from the master device and
# plots both the master's own channels and the imported slave channels on a
# common time axis. This is useful for measurements that require channel
# expansion across two White Rabbit synchronized time tagging units while
# processing the combined photon stream as one measurement.

if(__name__ == "__main__"):
    
    master = "1000509"
    slave = "1050002"
    
    # init snAPI
    sn = snAPI()
    sn.setLogLevel(LogLevel.Api, True)
        
    # get master device
    sn.getDevice(master) 
    sn.initDevice(MeasMode.T2, RefSource.Wr_Master_Harp)
    sn.device.setMeasControl(MeasControl.WrMaster2Slave)
    sn.loadIniConfig("config\HH500.ini")
    
    # create a own instance of the histogram class for the master device
    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(1)
    sn.histogram.setNumBins(20000)
    # import channels from slave into master manipulator
    # and enable the starting and stopping of the measurement via the master device (remoteStartStop=True)
    importChans = sn.manipulators.importStream(slave, [0,1,2], remoteStartStop=True)
    
    # get slave device
    sn.getDevice(slave) 
    #initialize slave with external 10MHz reference in (from master reference out)
    sn.initDevice(MeasMode.T2, RefSource.Wr_Slave_Harp)
    sn.loadIniConfig("config\MH.ini")
    sn.device.setMeasControl(MeasControl.WrMaster2Slave)
    
    # start measurement on both devices (from master)
    sn.getDevice(master)
    sn.histogram.measure(acqTime=0, waitFinished=False, savePTU=False)
    
    while not sn.histogram.isFinished():
        # get the data
        dataMaster, binsMaster = sn.histogram.getData()
        numChansMaster = len(dataMaster)
        
        # plot the histogram
        plt.clf()
        if len(dataMaster):
            plt.plot(binsMaster, dataMaster[0], linewidth=2.0, label='Sync Master')
            plt.plot(binsMaster, dataMaster[1], linewidth=2.0, label='Chan1 Master')
            for c in importChans:
                plt.plot(binsMaster, dataMaster[c], linewidth=2.0, label=f'Channel {c} Slave')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts', )
        plt.yscale('log', base=10, nonpositive='clip')
        plt.legend()
        plt.title("Counts / Time")
        plt.pause(0.1)

    plt.show(block=True)
