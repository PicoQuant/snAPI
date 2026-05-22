from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Quantum key distribution — BB84 receiver monitoring
# ===================================================
# This demo demonstrates how snAPI can be used to monitor heralded detector
# events in a BB84-style quantum key distribution receiver.
#
# Setup:
# Alice sends heralded single photons to Bob's receiver. The sync channel, Ch0,
# is used as Alice's herald signal. A passive basis choice, for example a 50/50
# beam splitter, routes each photon to one of two measurement bases.
#
# In the X basis, the photon is analyzed by a polarizing beam splitter with
# detectors for horizontal and vertical polarization:
#   Ch1: H polarization -> Bit 0
#   Ch2: V polarization -> Bit 1
#
# In the Z basis, the photon is analyzed by a second polarizing beam splitter
# with detectors for diagonal and anti-diagonal polarization:
#   Ch3: D polarization -> Bit 0
#   Ch4: A polarization -> Bit 1
#
# The herald filter gates all four detector channels to the expected
# photon-arrival window after Alice's herald pulse. Each heralded detector event
# represents a valid raw key event for the corresponding basis and bit value, so
# no additional coincidence calculation is required for key generation.
#
# The script also forms selected multi-detector coincidences as error monitors.
# Same-basis double clicks, such as H+V or D+A, indicate multi-photon events or
# dark-count overlap. Cross-basis coincidences, such as H+D or V+A, can indicate
# optical crosstalk, imperfect alignment, or other unwanted correlations.
#
# During acquisition, the raw key rates for H, V, D, and A are displayed together
# with the monitored error-coincidence rates. This is useful for checking the
# stability of a BB84 receiver, balancing the detector channels, and identifying
# error contributions during QKD experiments.

if(__name__ == "__main__"):
    sn = snAPI()
    sn.getDevice()
    # sn.getFileDevice(r"C:\Data\PicoQuant\qkd_bb84.ptu")
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\MH.ini")
    windowSize = 1000  # 1 ns gate window [ps]
    
    # --- Countrate before herald ---
    crInIdx = sn.manipulators.countrate()
    
    # --- Herald filter ---
    # Gate Bob's detectors Ch1-Ch4 using Alice's herald (Ch0).
    # Each heralded channel represents a valid key event:
    #   heraldChans[0] = H detection (Basis X, Bit 0)
    #   heraldChans[1] = V detection (Basis X, Bit 1)
    #   heraldChans[2] = D detection (Basis Z, Bit 0)
    #   heraldChans[3] = A detection (Basis Z, Bit 1)
    heraldChans = sn.manipulators.herald(0, [1, 2, 3, 4], delayTime=50000, gateTime=windowSize, keepChannels=True)
    h = heraldChans
    
    # --- Error monitoring: multi-detector coincidences ---
    # Same-basis double clicks indicate multi-photon events or dark count overlap
    # Cross-basis coincidences indicate optical crosstalk or misalignment
    ciErrors = sn.manipulators.coincidences([
        [h[0], h[1]],  # Double X: H + V
        [h[2], h[3]],  # Double Z: D + A
        [h[0], h[2]],  # Cross: H + D
        [h[0], h[3]],  # Cross: H + A
        [h[1], h[2]],  # Cross: V + D
        [h[1], h[3]],  # Cross: V + A
    ], windowSize)
    
    # --- Countrate after herald ---
    crOutIdx = sn.manipulators.countrate()
    
    # --- Measurement ---
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)
    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData()
        CRout = sn.manipulators.getCountrates(crOutIdx)
        # Raw key rates per detector
        rateH = CRout[h[0]]
        rateV = CRout[h[1]]
        rateD = CRout[h[2]]
        rateA = CRout[h[3]]
        totalRate = rateH + rateV + rateD + rateA
        sn.logPrint(f"Key rates - H:{rateH} V:{rateV} D:{rateD} A:{rateA} | Total:{totalRate}")
        plt.clf()
        # plot heralded detector rates = raw key events
        plt.subplot(2, 1, 1)
        plt.plot(times, counts[h[0]], linewidth=2.0, label='H (X, Bit 0)')
        plt.plot(times, counts[h[1]], linewidth=2.0, label='V (X, Bit 1)')
        plt.plot(times, counts[h[2]], linewidth=2.0, label='D (Z, Bit 0)')
        plt.plot(times, counts[h[3]], linewidth=2.0, label='A (Z, Bit 1)')
        plt.ylabel('Counts [Cts/s]')
        plt.legend(fontsize='small', ncol=2)
        plt.title("QKD BB84 - Heralded Key Events")
        # plot error coincidences
        plt.subplot(2, 1, 2)
        plt.plot(times, counts[ciErrors[0]], linewidth=2.0, label='Double X (H+V)')
        plt.plot(times, counts[ciErrors[1]], linewidth=2.0, label='Double Z (D+A)')
        plt.plot(times, counts[ciErrors[2]], linewidth=2.0, label='Cross H+D', linestyle='--')
        plt.plot(times, counts[ciErrors[3]], linewidth=2.0, label='Cross H+A', linestyle='--')
        plt.plot(times, counts[ciErrors[4]], linewidth=2.0, label='Cross V+D', linestyle='--')
        plt.plot(times, counts[ciErrors[5]], linewidth=2.0, label='Cross V+A', linestyle='--')
        plt.xlabel('Time [s]')
        plt.ylabel('Counts [Cts/s]')
        plt.legend(fontsize='small', ncol=2)
        plt.title("QKD BB84 - Error Monitoring")
        plt.tight_layout()
        plt.pause(0.1)
        if finished:
            break
    plt.show(block=True)
