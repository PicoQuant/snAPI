from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

# Sequence-mode g(2) correlation over measurement time
# ====================================================
# This demo demonstrates how sequence mode can be used to acquire a gapless
# series of second-order correlation measurements, g(2), from photon events
# recorded with a PicoQuant time tagging device or from a PTU file.
#
# The script configures a g(2) correlation between a signal channel and an idler
# channel. A fixed delay is applied to the signal channel with a snAPI
# manipulator so that the correlation feature is shifted into the selected
# correlation window.
#
# Setup:
# The signal and idler detector channels, correlation window, bin width,
# acquisition time, and sequence duration are defined in the script. The sequence
# duration determines the length of each consecutive correlation measurement in
# the gapless measurement sequence.
#
# The correlation module is run in sequence mode. Instead of repeatedly starting
# and stopping separate measurements, snAPI divides the acquisition into
# consecutive time slices and returns one g(2) curve for each slice.
#
# During acquisition, the script displays the sequence as a 2D plot with
# correlation delay tau on one axis and measurement time on the other. This is
# useful for observing changes in photon correlations over time without gaps
# between the individual correlation measurements, for example when monitoring
# source stability, alignment drift, blinking, or other time-dependent changes in
# a photon-pair or single-photon experiment.

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"D:\Data\PicoQuant\Chattanooga_MH150_3channel_FiberSpool.ptu")
    sn.initDevice()
    signal = 1
    idler = 2
    g2Data = None
    g2Bins = None
    windowSize = 0.5 # seconds
    fileSize = 60 # seconds
    delay = 49405000 # ps
    
    windows = np.arange(0, fileSize, windowSize)
    delayedCh1 = sn.manipulators.delay(signal, delay)
    sn.correlation.setG2Parameters(delayedCh1, idler, 10000, 5, False)
    sn.correlation.setSequenceMode(sequenceMode=SequenceMode.Timer, wait4newData=True, param = windowSize)
    sn.correlation.measure(acqTime = fileSize*1000)
    i = 0
    
    while True:        
        finished = sn.correlation.isFinished()
        if finished:
            break
        data, bins = sn.correlation.getG2Data()

        if g2Data is None:
            g2Data = np.zeros((len(windows), len(data)))
            g2Bins  = np.copy( bins + delay * 1e-12 )

        if i < len(windows):
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

