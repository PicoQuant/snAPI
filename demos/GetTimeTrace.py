from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\HH400-PMT-cw-1MHz.ptu")
    #sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    #sn.getFileDevice(r"E:\Data\PicoQuant\11_1.ptu")
    sn.initDevice(MeasMode.T3)
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(66)
    sn.timeTrace.measure(100000, False, True)

    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData() 
        plt.clf()
        plt.plot(times, counts[0], linewidth=2.0, label='sync')
        plt.plot(times, counts[1], linewidth=2.0, label='chan1')
        plt.plot(times, counts[2], linewidth=2.0, label='chan2')
        #plt.plot(times, data[3], linewidth=2.0, label='chan3')
        #plt.plot(times, data[4], linewidth=2.0, label='chan4')
        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)
        
        if finished:
            break
            
    plt.show(block=True)