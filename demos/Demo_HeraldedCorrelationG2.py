from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI(libType=LibType.MH)
    sn.getDeviceIDs()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)

    # define the path for the T2 file
    sn.getFileDevice("E:\Data\PicoQuant\CW_Shelved.ptu")

    # define a gate window after the herald channel (1) for the detector channels (2 and 3), 
    # starting at 100000 ps after the herald signal, with a gate length of 200000 ps
    heraldChans = sn.manipulators.herald(1, [2, 3], 100000, 200000)

    # initiate the g2 correlation with the time-gated channels
    sn.correlation.setG2Parameters(heraldChans[0],heraldChans[1], 500000, 100)
    sn.correlation.measure(100000,savePTU=False)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getG2Data()
        time.sleep(.3)
        
        plt.clf()
        plt.plot(bins, data, linewidth=2.0, label='g(2)')
        plt.xlabel('Time [s]')
        plt.ylabel('g(2)')
        plt.legend()
        plt.title("g(2)")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
