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
    #sn.getFileDevice(r"e:\Data\PicoQuant\cell01_55pct_1.ptu")
    #sn.getFileDevice(r"e:\Data\PicoQuant\Correaltion_T3.ptu")
    #sn.getFileDevice(r"e:\Data\PicoQuant\OpenCLTest\Atto655+Cy5_diff_FCS+FLCS_Conv.ptu")
    sn.initDevice(MeasMode.T3)
    #sn.device.setInputDeadTime(-1,1000)
    sn.correlation.setFCSparameters(1, 2, 1e4, 5)
    sn.correlation.measure(10000,savePTU=True)

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
            
        #sn.correlation.clearMeasure()
            
        if finished:
            break

    plt.show(block=True)    
