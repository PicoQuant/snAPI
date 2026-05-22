from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time

# Conditioned g(2) — a 1D slice of g(3)
# ========================================
# This demo measures a conditioned g(2): the probability of detecting a photon
# on Ch3 at delay tau, given that Ch1 and Ch2 fired simultaneously (tau1 ~ 0).
#
# This is NOT the full g(3)(tau1, tau2), which is a 2D correlation function.
# It is the 1D slice g(3)(0, tau) — useful for verifying photon number
# statistics and multi-photon emission properties.
#
# Setup:
#   A light source is split onto 3 SNSPDs via beam splitters:
#     SNSPD 1 (Ch1)
#     SNSPD 2 (Ch2)
#     SNSPD 3 (Ch3)
#
# Approach:
#   1. Build a coincidence of Ch1 and Ch2 -> virtual channel ci_12
#   2. Correlate ci_12 with Ch3 using the built-in g(2) correlator
#   This yields g(3)(0, tau) — conditioned on a 2-fold coincidence at tau1 ~ 0.
#
# The herald filter is used if the source is pulsed (sync on Ch0).
# For CW sources, the herald can be omitted.

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