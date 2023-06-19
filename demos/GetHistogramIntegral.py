from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
from threading import Timer
import time

if(__name__ == "__main__"):

    class RepeatTimer(Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)
                
    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    sn.getFileDevice(r"C:\Data\PicoQuant\default.ptu")
    sn.initDevice(MeasMode.T2)
    #sn.device.setInputDeadTime(-1,1000)
    waitFinished = False
    sn.device.setStopOverflow(1000000)
    
    #sn.filter.setRowParams(0, 1000, 1, False, [0,1], [])
    #sn.filter.enableRow(0,True)
    hChans = sn.manipulators.herald(0, [1,2], 66000, 10000, True)
    #cm = sn.manipulators.merge([1,2],True)
    #hChans = [1,2]
    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(5)
    sn.histogram.measure(10000, False)
    #refreshTimer = RepeatTimer(1, sn.histogram.clearMeasure).start()
    
    while True:
        finished = sn.histogram.isFinished()
        data, bins = sn.histogram.getData()
        #if not waitFinished and not finished:
            #sn.histogram.clearMeasure()
            
        plt.pause(0.5)
        plt.clf()
        #plt.plot(bins, data[0], linewidth=2.0, label='sync')
        plt.plot(bins, data[1], linewidth=2.0, label='chan1')
        plt.plot(bins, data[2], linewidth=2.0, label='chan2')
        plt.plot(bins, data[hChans[0]], linewidth=2.0, label='h1')
        plt.plot(bins, data[hChans[1]], linewidth=2.0, label='h2')
        #plt.plot(bins, data[cm], linewidth=2.0, label='merge 1&2')
        plt.xlabel('Time [ps]')
        #plt.xlim(0, 27000) #set the scale range of the time scale to the region of interest
        #plt.yscale('log')
        plt.ylabel('Counts')
        #plt.ylim(50, 1e6)
        plt.legend()
        plt.title("Histogram")
        
        if waitFinished or finished:
            break
                
    #refreshTimer.clear()
    
    plt.show(block=True)
