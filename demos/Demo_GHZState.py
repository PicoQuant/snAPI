from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import time
 
# GHZ state verification with heralded multi-photon coincidences
# ==============================================================
# This demo demonstrates how snAPI can be used to monitor multi-photon
# coincidence patterns for experiments involving Greenberger-Horne-Zeilinger
# (GHZ) entangled states.
#
# Setup:
# A pulsed photon source generates the photons used for the GHZ-state experiment.
# The sync channel, Ch0, is used as the pump laser trigger and acts as the herald
# signal. Three single-photon detectors are connected to Ch1..Ch3 and record the
# photons associated with the three GHZ modes A, B, and C.
#
# The herald filter gates the detector channels to the relevant time window after
# each pump pulse. This suppresses events outside the expected photon-arrival
# window and creates heralded detector channels for the three output modes.
#
# The script then forms the pairwise coincidences {A,B}, {A,C}, and {B,C}, as
# well as the three-fold coincidence {A,B,C}. The pairwise coincidences are used
# to monitor the two-photon contributions and estimate accidental coincidences,
# while the three-fold coincidence indicates events in which all three photons
# are detected within the selected coincidence window.
#
# During acquisition, the pairwise and three-fold coincidence rates are displayed
# as time traces. This is useful for GHZ-state generation and verification
# experiments, where the stability and relative rates of multi-photon
# coincidence events are used to evaluate the measurement.
 
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
