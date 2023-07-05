from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    #sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    #sn.getFileDevice(r"e:\Data\PicoQuant\cell01_55pct_1.ptu")
    #sn.getFileDevice(r"e:\Data\PicoQuant\Correaltion_T3.ptu")
    #sn.getFileDevice(r"e:\Data\PicoQuant\Datasets Metrologia 56 025004\Metrologia_g2_SPS1550_INRIM-PTB-NPL\20171023_INRIM-NPL\acq_NPL\g2_1550nm_NPL\acq002_001.ptu")
    sn.initDevice(MeasMode.T2)
    #sn.device.setInputDeadTime(-1,1000)
    
    # set filter window to 1ns
    #sn.filter.setRowParams(0, 1000, 1, False, [0,1], [])
    #sn.filter.enableRow(0,True)
    #sn.manipulators.coincidence([1,2], 200000)
    
    #sn.setPTUFilePath("test.ptu")
    sn.correlation.setG2parameters(1, 2, 200000, 200)
    sn.correlation.measure(10000,savePTU=True)
    
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
        #sn.correlation.clearMeasure()
        
        if sn.correlation.isFinished():
            break
    
    plt.show(block=True)