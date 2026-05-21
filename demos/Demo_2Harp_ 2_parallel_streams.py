from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Two synchronized time tagging devices — parallel histogram streams
# =============================================================
# This demo demonstrates parallel histogram acquisition with two synchronized
# PicoQuant time tagging devices in a master-slave configuration.
#
# Setup:
# The master device provides the timing reference and controls the measurement
# start. Its 10 MHz reference output is connected to the external reference
# input of the slave device. The master's measurement-active signal is
# additionally connected to the slave control input C1.
#
# The slave is configured to use the external 10 MHz reference and waits for the
# measurement-active gate from the master before acquiring data. This allows both
# devices to run synchronized measurements while keeping their data streams
# separate.
#
# During acquisition, histograms from the master and slave are read independently
# and plotted together. This is useful for multi-device measurements that require
# synchronized acquisition across two time tagging units while preserving separate
# histogram streams for each device.

if(__name__ == "__main__"):
    
    master = "1000509"
    slave = "1050002"
    
    # init snAPI
    sn = snAPI()
        
    # get master
    sn.getDevice(master) 
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\HH500.ini")
    histoMaster = Histogram(sn)
    histoMaster.setRefChannel(0)
    histoMaster.setBinWidth(1)
    histoMaster.setNumBins(20000)
    
    # get slave
    sn.getDevice(slave) 
    #initialize slave wit external trigger in (from master trigger out)
    sn.initDevice(MeasMode.T2, RefSource.External_10MHZ)
    sn.loadIniConfig("config\MH.ini")
    # set the slave to wait on measurement active (master MACT is connected to slave C1)
    # https://picoquant.github.io/snAPI/hardware.controlConnector.html
    sn.device.setMeasControl(MeasControl.C1Gated, 1, 0)
    histoSlave = Histogram(sn)
    histoSlave.setRefChannel(0)
    histoSlave.setBinWidth(5)
    histoSlave.setNumBins(4000)
    
    # start histogram measurement
    # ..on slave first
    histoSlave.measure(waitFinished=False, savePTU=False)
    # wait for measurement is running:
    # the slave measurement is started in a separate thread and unfortunately 
    # an "histoMaster.measure" could be faster then the slave
    # then the slave misses the measurement active (low-high-slope)
    # and never get started
    time.sleep(0.01)
    
    sn.getDevice(master)
    histoMaster.measure(acqTime=10000, waitFinished=False, savePTU=False)
    
    
    while not histoSlave.isFinished():
        # get the data
        #sn.getDevice(master)
        dataMaster, binsMaster = histoMaster.getData()
        #sn.getDevice(slave)
        dataSlave, binsSlave = histoSlave.getData()
        numChansMaster = len(dataMaster)
        numChansSlave = len(dataSlave)
        
        # plot the histogram
        plt.clf()
        if len(dataMaster):
            plt.plot(binsMaster, dataMaster[0], linewidth=2.0, label='SyncM')
            for c in range(1, numChansMaster):
                plt.plot(binsMaster, dataMaster[c], linewidth=2.0, label=f'ChanM{c}')
        if len(dataSlave):
            plt.plot(binsSlave, dataSlave[0], linewidth=2.0, label='SyncS')
            for c in range(1, numChansSlave):
                plt.plot(binsSlave, dataSlave[c], linewidth=2.0, label=f'ChanS{c}')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts', )
        plt.yscale('log', base=10, nonpositive='clip')
        plt.legend()
        plt.title("Counts / Time")
        plt.pause(0.1)

    plt.show(block=True)
