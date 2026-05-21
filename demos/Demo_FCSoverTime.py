from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    #sn.getDevice()
    sn.getFileDevice(r"D:\Data\PicoQuant\OpenCLTest\Atto655+Cy5_diff_FCS+FLCS_Conv.ptu")
    sn.initDevice()
    channelA = 1
    channelB = 2
    fcsData = None
    fcsBins = None
    windowSize = 10 # seconds
    fileSize = 210 # seconds
    
    windows = np.arange(0, fileSize, windowSize)
    sn.correlation.setFFCSParameters(1, 2, 1e6, 1e12, 100)
    sn.correlation.setSequenceMode(sequenceMode=SequenceMode.Timer, wait4newData=True, param = windowSize)
    sn.correlation.measure(acqTime = fileSize*1000)
    i = 0
    
    while True:
        finished = sn.correlation.isFinished()
        if finished:
            break
        data, bins = sn.correlation.getFCSData()

        if len(data) == 0:
            continue

        if fcsData is None:
            fcsData = np.zeros((len(windows), len(data[0])))
            fcsBins  = np.copy(bins)

        if i < len(windows):
            fcsData[i, :] = data[0]
            i += 1
        else:
            break

    plt.clf()
    plt.pcolormesh(fcsBins * 1e12, windows[:i], fcsData[:i, :],
                    shading='auto', cmap='hot')
    plt.xscale('log')
    plt.colorbar(label='Counts')
    plt.xlabel('tau [ps]')
    plt.ylabel('t [s]')
    plt.title(f"FCS — Step {i+1}/{len(windows)}")
    plt.tight_layout()
    plt.pause(0.1)
    plt.title("FCS over time")
    plt.show(block=True)

