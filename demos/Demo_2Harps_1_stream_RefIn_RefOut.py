from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Two synchronized TCSPC devices — combined histogram stream
# ==========================================================
# This demo demonstrates how photon events from two synchronized PicoQuant
# time tagging devices can be combined into a single histogram stream.
#
# Setup:
# The master device provides the timing reference and controls the measurement
# start. Its 10 MHz reference output is connected to the external reference
# input of the slave device. The master's measurement-active signal is
# additionally connected to the slave control input C1.
#
# The slave is configured to use the external 10 MHz reference and waits for the
# measurement-active gate from the master before acquiring data. Selected slave
# input channels are then imported into the master's data stream using a snAPI
# stream manipulator.
#
# The resulting histogram contains both the master's own channels and the
# imported slave channels on a common time axis. This is useful for multi-device
# measurements that require synchronized acquisition across two TCSPC units while
# processing the combined photon stream as one measurement.

if(__name__ == "__main__"):
    
    master = "1000509"
    slave = "1050002"
    
    # init snAPI
    sn = snAPI()
    sn.setLogLevel(LogLevel.Api, True)
        
    # get master device
    sn.getDevice(master) 
    sn.initDevice(MeasMode.T2)
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
    sn.initDevice(MeasMode.T2, RefSource.External_10MHZ)
    sn.loadIniConfig("config\MH.ini")
    # set the slave to wait on measurement active (master MACT is connected to slave C1)
    # https://picoquant.github.io/snAPI/hardware.controlConnector.html
    sn.device.setMeasControl(MeasControl.C1Gated, 1, 0)
    
    # start measurement on both devices (from master)
    sn.getDevice(master)
    sn.histogram.measure(acqTime=10000, waitFinished=False, savePTU=False)
    
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
