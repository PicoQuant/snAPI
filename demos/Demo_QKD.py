from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Quantum Key Distribution (BB84)
# ================================
# This demo demonstrates a BB84-style QKD receiver using herald-gated detectors.
#
# Setup:
#   Alice sends heralded single photons. The herald signal arrives on Ch0 (sync).
#   A passive basis choice (50/50 beam splitter) routes photons to one of two
#   polarizing beam splitters (PBS):
#
#   Basis X (rectilinear):
#     PBS1 -> SNSPD 1 (Ch1, H polarization) = Bit 0
#     PBS1 -> SNSPD 2 (Ch2, V polarization) = Bit 1
#
#   Basis Z (diagonal):
#     PBS2 -> SNSPD 3 (Ch3, D polarization) = Bit 0
#     PBS2 -> SNSPD 4 (Ch4, A polarization) = Bit 1
#
# The herald filter gates all detectors to the time window after Alice's pulse.
# A heralded click on any detector already represents a coincidence between
# Alice's source and Bob's measurement -- no additional coincidence is needed
# for key generation.
#
# Multi-detector coincidences are monitored as error indicators:
#   - Same-basis double clicks (H+V or D+A): multi-photon events
#   - Cross-basis clicks (e.g. H+D): optical crosstalk or alignment issues

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