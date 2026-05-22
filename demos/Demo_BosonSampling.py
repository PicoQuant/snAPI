from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
 
# Boson sampling with heralded coincidence detection
# ==================================================
# This demo demonstrates how snAPI can be used to monitor coincidence events in
# a boson sampling experiment.
#
# Setup:
# A pulsed photon source injects single photons into a linear optical network.
# The sync channel, Ch0, is used as the pump laser trigger and acts as the herald
# signal. Four output ports of the optical network are monitored by single-photon
# detectors connected to Ch1..Ch4.
#
# The herald filter gates the detector channels to the relevant time window after
# each pump pulse. This suppresses events outside the expected photon-arrival
# window and creates heralded detector channels for the four output ports.
#
# The script then forms all pairwise, three-fold, and four-fold coincidences
# between the heralded output channels. During acquisition, these coincidence
# rates are displayed as time traces, allowing the occupied output-port
# combinations of the optical network to be monitored in real time.
#
# This is useful for boson sampling and related linear-optics experiments where
# the photon-number distribution across several output modes is inferred from
# multi-channel coincidence patterns.
 
if(__name__ == "__main__"):
 
    sn = snAPI()
    sn.getDevice()
    # sn.getFileDevice(r"C:\Data\PicoQuant\boson_sampling.ptu")
 
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\MH.ini")
 
    windowSize = 1000  # 1 ns coincidence window [ps]
    h = [0, 0, 0, 0]  # shorthand for heralded channels
 
    # --- Herald filter ---
    # Gate output detectors Ch1-Ch4 using the pump trigger (Ch0) as herald
    heraldChans = sn.manipulators.herald(0, [1, 2, 3, 4], delayTime=50000, gateTime=windowSize, keepChannels=True)
    h = heraldChans
 
    crInIdx = sn.manipulators.countrate()
 
    # --- Pairwise coincidences (2-fold) ---
    ci2 = sn.manipulators.coincidences([
        [h[0], h[1]],  # {1,2}
        [h[0], h[2]],  # {1,3}
        [h[0], h[3]],  # {1,4}
        [h[1], h[2]],  # {2,3}
        [h[1], h[3]],  # {2,4}
        [h[2], h[3]],  # {3,4}
    ], windowSize)
 
    # --- 3-fold coincidences ---
    ci3 = sn.manipulators.coincidences([
        [h[0], h[1], h[2]],  # {1,2,3}
        [h[0], h[1], h[3]],  # {1,2,4}
        [h[0], h[2], h[3]],  # {1,3,4}
        [h[1], h[2], h[3]],  # {2,3,4}
    ], windowSize)
 
    # --- 4-fold coincidence ---
    ci4 = sn.manipulators.coincidences([
        [h[0], h[1], h[2], h[3]],  # {1,2,3,4}
    ], windowSize)
 
    crOutIdx = sn.manipulators.countrate()
 
    # --- Measurement ---
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)
 
    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData()
 
        CRout = sn.manipulators.getCountrates(crOutIdx)
        sn.logPrint(f"Heralded rates - Ch1: {CRout[h[0]]}, Ch2: {CRout[h[1]]}, "
                    f"Ch3: {CRout[h[2]]}, Ch4: {CRout[h[3]]}")
 
        plt.clf()
 
        # plot 2-fold coincidences
        plt.subplot(2, 1, 1)
        plt.plot(times, counts[ci2[0]], linewidth=2.0, label='{1,2}')
        plt.plot(times, counts[ci2[1]], linewidth=2.0, label='{1,3}')
        plt.plot(times, counts[ci2[2]], linewidth=2.0, label='{1,4}')
        plt.plot(times, counts[ci2[3]], linewidth=2.0, label='{2,3}')
        plt.plot(times, counts[ci2[4]], linewidth=2.0, label='{2,4}')
        plt.plot(times, counts[ci2[5]], linewidth=2.0, label='{3,4}')
        plt.ylabel('Counts [Cts/s]')
        plt.legend(fontsize='small', ncol=3)
        plt.title("Boson Sampling - 2-fold Coincidences")
 
        # plot 3-fold and 4-fold coincidences
        plt.subplot(2, 1, 2)
        plt.plot(times, counts[ci3[0]], linewidth=2.0, label='{1,2,3}')
        plt.plot(times, counts[ci3[1]], linewidth=2.0, label='{1,2,4}')
        plt.plot(times, counts[ci3[2]], linewidth=2.0, label='{1,3,4}')
        plt.plot(times, counts[ci3[3]], linewidth=2.0, label='{2,3,4}')
        plt.plot(times, counts[ci4[0]], linewidth=2.0, label='{1,2,3,4}')
        plt.xlabel('Time [s]')
        plt.ylabel('Counts [Cts/s]')
        plt.legend(fontsize='small', ncol=3)
        plt.title("Boson Sampling - Higher-Order Coincidences")
 
        plt.tight_layout()
        plt.pause(0.1)
 
        if finished:
            break
 
    plt.show(block=True)
 
