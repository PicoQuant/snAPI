from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
from tqdm import tqdm
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    hData = None
    hBins = None
    channel = 2
    windowSize = .1  # seconds per sequence step
    acqTime = 10000   # ms

    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(5)
    sn.histogram.setNumBins(20000)
    sn.histogram.setSequenceMode(sequenceMode=SequenceMode.Timer, wait4newData=True, param=windowSize)
    sn.histogram.measure(acqTime=acqTime, waitFinished=False)
    i = 0
    maxSteps = int(acqTime / (windowSize * 1000))

    with tqdm(total=maxSteps, desc="Acquiring histograms", unit="step") as pbar:
        while True:
            finished = sn.histogram.isFinished()
            if finished:
                break
            data, bins = sn.histogram.getData()
            if len(data) == 0:
                continue

            if hData is None:
                hData = np.zeros((110, len(data[channel])))
                hBins = bins

            if i < len(hData):
                hData[i, :] = data[channel]
                i += 1
                pbar.update(1)
            else:
                break

    plt.clf()
    step = hBins[1] - hBins[0]
    xEdges = np.append(hBins, hBins[-1] + step) * 1e12
    yEdges = np.arange(i + 1) * windowSize
    plt.pcolormesh(xEdges, yEdges, hData[:i, :], shading='flat', cmap='hot', norm=LogNorm(vmin=1))
    plt.colorbar(label='Counts')
    plt.xlabel('Time delay [ps]')
    plt.ylabel('Elapsed time [s]')
    plt.title(f"Histograms — channel {channel}, {i} steps × {windowSize} s")
    plt.tight_layout()
    plt.show(block=True)

