from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

if(__name__ == "__main__"):

    sn = snAPI(libType=LibType.HH)
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\MH160_Sun.ptu")
    #sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    #sn.getFileDevice(r"C:\Data\PicoQuant\default_1.ptu")
    sn.initDevice(MeasMode.T2)
    sn.device.setSyncDiv(1)
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    #sn.setPTUFilePath(r"test_the_best")
    
    keepChannels = True
    
    # hChans = sn.manipulators.herald(0, [1,2], 66000, 100000, keepChannels)
    #ci = sn.manipulators.coincidence([1, 2], 10000, keepChannels)
    # cd = sn.manipulators.delay(1, 1000000000, keepChannels)
    # cm = sn.manipulators.merge([hChans[0], hChans[1]], keepChannels)    
    
    sn.timeTrace.measure(100000, False, False)
    
    while True: 
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData() 
        plt.clf()
        plt.plot(times, counts[0], linewidth=2.0, label='sync')
        plt.plot(times, counts[1], linewidth=2.0, label='chan1')
        plt.plot(times, counts[2], linewidth=2.0, label='chan2')
        # plt.plot(times, counts[hChans[0]], linewidth=2.0, label='hChan1')
        # plt.plot(times, counts[hChans[1]], linewidth=2.0, label='hChan2')
        #plt.plot(times, counts[ci], linewidth=2.0, label='coincidence 1&2-1ns')
        # plt.plot(times, counts[cd], linewidth=2.0, label='delay 1ms')
        # plt.plot(times, counts[cm], linewidth=2.0, label='merged h1&h2')

        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
