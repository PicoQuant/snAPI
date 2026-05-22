from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

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