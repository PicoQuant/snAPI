from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.getFileDevice(r"D:\Data\PicoQuant\Chattanooga_MH150_3channel_FiberSpool.ptu")
    #sn.initDevice()
    signal = 1
    idler = 2
    g2Data = None
    g2Bins = None
    startTime = 59.5 # seconds
    stopTime = 60 # seconds
    windowSize = 0.001 # seconds
    delay = 49405000 # ps
    
    windows = np.arange(startTime, stopTime, windowSize)
    sn.manipulators.subStream(startTime, stopTime)
    delayedCh1 = sn.manipulators.delay(signal, delay)
    sn.correlation.setG2Parameters(delayedCh1, idler, 1000, 50, False)
    sn.correlation.setSequenceMode(sequenceMode=SequenceMode.Timer, wait4newData=True, param = windowSize)
    sn.correlation.measure(acqTime = stopTime * 1000)
    i = 0
    
    while True:        
        finished = sn.correlation.isFinished()
        if finished:
            break
        data, bins = sn.correlation.getG2Data()

        if g2Data is None:
            g2Data = np.zeros((len(windows), len(data)))
            g2Bins  = np.copy( bins + delay * 1e-12 )

        if i < len(windows) and len(data) > 0:
            if windows[i] > startTime:
                g2Data[i, :] = data
            i += 1
        else:
            break

    plt.clf()
    plt.pcolormesh(g2Bins * 1e12, windows[:i+1], g2Data[:i+1, :],
                    shading='auto', cmap='hot')
    plt.colorbar(label='Counts')
    plt.xlabel('tau [ps]')
    plt.ylabel('t [s]')
    plt.title(f"g(2)(tau1, tau2) — Step {i+1}/{len(windows)}")
    plt.tight_layout()
    plt.pause(0.1)
    plt.title("g(2)(C1, C2) over time")
    plt.show(block=True)

