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