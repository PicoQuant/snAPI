from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    #sn.getFileDevice(r"E:\Data\PicoQuant\PMT-cw-1MHz.ptu")
    #sn.getFileDevice(r"E:\Data\PicoQuant\HH400-PMT-cw-1MHz.ptu")
    sn.initDevice(MeasMode.T3)
    #sn.device.setInputDeadTime(-1,1000)
    
    # set filter window to 1ns
    sn.filter.setRowParams(0, 1000, 1, False, [0,1], [])
    sn.filter.enableRow(0,True)
    
    sn.correlation.setG2parameters(1, 2, 1000, 5)
    sn.correlation.measure(100000)
    
    plt.ion()
    while True:
        data, bins = sn.correlation.getG2data()
        #time.sleep(1.0)
        
        plt.clf()
        
        plt.plot(bins, data, linewidth=2.0, label='g(2)')
        plt.xlabel('Time [s]')
        plt.ylabel('g(2)')
        #plt.ylim(0,1)
        plt.legend()
        plt.title("g(2)")
        plt.pause(0.1)
        sn.correlation.clearMeasure()
        
        if sn.correlation.isFinished():
            break
    
    plt.show(block=True)