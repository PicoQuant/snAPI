from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDeviceIDs()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    sn.initDevice(MeasMode.T2)
    #sn.device.setInputDeadTime(-1,1000)
    sn.correlation.setFCSparameters(1, 2, 20, 8)
    sn.correlation.measure(100000)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getFCSdata()
        time.sleep(.3)
        
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='AB')
        plt.plot(bins, data[1], linewidth=2.0, label='BA')
        plt.xlabel('Time [s]')
        plt.xscale('log')
        plt.ylabel('FCS')
        #plt.yscale('log')
        plt.legend()
        plt.title("FCS")
        plt.pause(0.1)
            
        sn.correlation.clearMeasure()
            
        if finished:
            break

    plt.show(block=True)    
