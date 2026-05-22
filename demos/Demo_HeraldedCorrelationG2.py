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
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\MH.ini")
    
    windowSize = 2000 #ps
    # move the histograms of the both channels to the same time after the sync to filter both at once
    sn.device.setInputChannelOffset(0,-4000)

    # measure the count rate before the herald filter
    CrInIdx = sn.manipulators.countrate()
    
    # define a gate window after the herald channel 0 (sync) for the detector channels 1 and 2, 
    # starting at 52000 ps after the herald signal , with a gate length of windowSize (300 ps)
    heraldChans = sn.manipulators.herald(0, [1,2], 46000, windowSize, inverted=False, keepChannels=True )
    
    # measure the count rate after the herald filter
    CrOutIdx = sn.manipulators.countrate()

    # initiate the g2 correlation with the time-gated channels
    sn.correlation.setG2Parameters(heraldChans[0], heraldChans[1], windowSize, 1)
    sn.correlation.measure(10000,savePTU=False)

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getG2Data()
        
        CRin = sn.manipulators.getCountrates(CrInIdx)
        CRout = sn.manipulators.getCountrates(CrOutIdx)
        
        # print the count rates
        sn.logPrint(f"CR in: {CRin[1]}, {CRin[2]} - out: {CRout[heraldChans[0]]}, {CRout[heraldChans[1]]}")
        
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
