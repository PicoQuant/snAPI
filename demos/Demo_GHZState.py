from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time
 
# GHZ State Generation and Verification
# =======================================
# This demo demonstrates multi-photon coincidence detection for heralding
# and verifying Greenberger-Horne-Zeilinger (GHZ) entangled states.
#
# Setup:
#   A pulsed pump laser generates photon pairs via SPDC.
#   The sync channel (Ch0) provides the pump trigger (herald).
#   3 detectors measure the output photons:
#     SNSPD 1 (Ch1) - Photon A
#     SNSPD 2 (Ch2) - Photon B
#     SNSPD 3 (Ch3) - Photon C
#
# A 3-fold coincidence {Ch1, Ch2, Ch3} after the herald gate signals
# a successful GHZ state generation event.
#
# Additional pairwise coincidences are monitored to verify that the 3-fold
# rate is consistent with the pairwise rates (accidental coincidence estimation).
 
if(__name__ == "__main__"):
 
    sn = snAPI()
    sn.getDevice()
    # sn.getFileDevice(r"C:\Data\PicoQuant\ghz_state.ptu")
 
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\MH.ini")
 
    windowSize = 1000  # 1 ns coincidence window [ps]
 
    # --- Herald filter ---
    # Gate all detectors using the pump trigger (Ch0)
    heraldChans = sn.manipulators.herald(0, [1, 2, 3], delayTime=50000, gateTime=windowSize, keepChannels=True)
    h = heraldChans
 
    crInIdx = sn.manipulators.countrate()
 
    # --- Pairwise coincidences (for accidental rate estimation) ---
    ci2 = sn.manipulators.coincidences([
        [h[0], h[1]],  # {A,B}
        [h[0], h[2]],  # {A,C}
        [h[1], h[2]],  # {B,C}
    ], windowSize)
 
    # --- 3-fold coincidence (GHZ state herald) ---
    ci3 = sn.manipulators.coincidences([
        [h[0], h[1], h[2]],  # {A,B,C}
    ], windowSize)
 
    crOutIdx = sn.manipulators.countrate()
 
    # --- Measurement ---
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)
 
    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData()
 
        CRin = sn.manipulators.getCountrates(crInIdx)
        CRout = sn.manipulators.getCountrates(crOutIdx)
 
        sn.logPrint(f"Heralded rates - A: {CRout[h[0]]}, B: {CRout[h[1]]}, C: {CRout[h[2]]}")
 
        plt.clf()
 
        # plot pairwise coincidences
        plt.subplot(2, 1, 1)
        plt.plot(times, counts[ci2[0]], linewidth=2.0, label='{A,B}')
        plt.plot(times, counts[ci2[1]], linewidth=2.0, label='{A,C}')
        plt.plot(times, counts[ci2[2]], linewidth=2.0, label='{B,C}')
        plt.ylabel('Counts [Cts/s]')
        plt.legend()
        plt.title("GHZ State - Pairwise Coincidences")
 
        # plot 3-fold coincidence
        plt.subplot(2, 1, 2)
        plt.plot(times, counts[ci3[0]], linewidth=2.0, label='{A,B,C} (GHZ herald)', color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('Counts [Cts/s]')
        plt.legend()
        plt.title("GHZ State - 3-Fold Coincidence")
 
        plt.tight_layout()
        plt.pause(0.1)
 
        if finished:
            break
 
    plt.show(block=True)