from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

# Higher-order correlation — conditioned g(2) as a slice of g(3)
# ==============================================================
# This demo demonstrates how snAPI can be used to measure a higher-order
# correlation by conditioning a g(2) measurement on a two-photon coincidence.
#
# The script creates a virtual coincidence channel from detector channels Ch1
# and Ch2. This channel fires when photons are detected on both channels within
# the selected coincidence window. The virtual coincidence channel is then
# correlated with a third detector channel, Ch3, using the built-in g(2)
# correlator.
#
# Setup:
# A light source is split onto three single-photon detectors connected to
# Ch1..Ch3. For pulsed sources, the sync channel Ch0 can be used as a herald
# signal to gate the detector channels to the expected photon-arrival window. For
# continuous-wave sources, the detector channels can be used directly.
#
# The resulting correlation corresponds to a one-dimensional slice of the
# third-order correlation function, g(3)(0, tau). It gives the probability of
# detecting a photon on Ch3 at delay tau, conditioned on a coincidence between
# Ch1 and Ch2 at tau1 approximately equal to zero.
#
# During acquisition, the script repeatedly reads and plots this conditioned
# g(2) curve. This is useful for studying multi-photon emission, photon-number
# statistics, and higher-order correlations without calculating the full
# two-dimensional g(3)(tau1, tau2) map.

if(__name__ == "__main__"):
    sn = snAPI()
    sn.getDevice()
    ptuFile = r"D:\Data\PicoQuant\g2t.ptu"
    sn.getFileDevice(ptuFile)
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\MH.ini")
    windowSize = 1000  # 1 ns coincidence window [ps]
    
    # --- Optional: Herald filter for pulsed sources ---
    # Uncomment the following lines if using a pulsed source with sync on Ch0:
    # heraldChans = sn.manipulators.herald(0, [1, 2, 3], delayTime=50000, gateTime=windowSize, keepChannels=True)
    # ch1, ch2, ch3 = heraldChans[0], heraldChans[1], heraldChans[2]
    # For CW sources, use the detector channels directly:
    ch1, ch2, ch3 = 1, 2, 3
    
    # --- Coincidence of Ch1 and Ch2 ---
    # This creates a virtual channel that fires when Ch1 and Ch2 coincide.
    # The timestamp is set to Average to center the correlation peak.
    ci_12 = sn.manipulators.coincidence([ch1, ch2], windowSize, time=CoincidenceTime.Average, keepChannels=True)
    
    # --- Conditioned g(2): coincidence(1,2) vs Ch3 ---
    # This yields the 1D slice g(3)(0, tau)
    sn.correlation.setG2Parameters(ci_12, ch3, 20000, 5, True)
    sn.correlation.measure(0, savePTU=False)
    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getG2Data()
        time.sleep(.3)
        plt.clf()
        plt.plot(bins, data, linewidth=2.0, label='g(3)(0, tau): coinc{1,2} vs Ch3')
        plt.xlabel('tau [ps]')
        plt.ylabel('g(3)(0, tau)')
        plt.legend()
        plt.title("Conditioned g(2) — slice of g(3)")
        plt.pause(0.1)
        if finished:
            break
    plt.show(block=True)
