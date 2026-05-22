from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

# Bell State Measurement
# ======================
# This demo demonstrates a Bell state measurement using two entangled photon pairs.
#
# Setup:
#   Photon pair A -> Beam Splitter -> SNSPD 1 (Ch1), SNSPD 2 (Ch2)
#   Photon pair B -> Beam Splitter -> SNSPD 3 (Ch3), SNSPD 4 (Ch4)
#
# The sync channel (Ch0) acts as the pump laser trigger (herald).
# A herald filter gates the detector channels to the relevant time window
# after the pump pulse.
#
# Coincidence patterns identify Bell states:
#   {1,3} or {2,4} -> |Psi+>
#   {1,4} or {2,3} -> |Psi->
#
# The ratio of these coincidence rates reveals the quality of the entanglement source.

if(__name__ == "__main__"):
    sn = snAPI()
    sn.getDevice()
    # sn.getFileDevice(r"C:\Data\PicoQuant\bell_state.ptu")
    sn.initDevice(MeasMode.T2)
    sn.loadIniConfig("config\MH.ini")
    windowSize = 1000  # 1 ns coincidence window [ps]
    
    # --- Herald filter ---
    # Gate detectors Ch1-Ch4 using the sync pulse (Ch0) as herald.
    # Only events within the gate window after the pump pulse are relevant.
    heraldChans = sn.manipulators.herald(0, [1, 2, 3, 4], delayTime=50000, gateTime=windowSize, keepChannels=True)
    # heraldChans[0..3] correspond to the heralded versions of Ch1..Ch4
    
    # --- Coincidences for Bell state identification ---
    # |Psi+>: {1,3} or {2,4}
    # |Psi->: {1,4} or {2,3}
    ciChans = sn.manipulators.coincidences([
        [heraldChans[0], heraldChans[2]],  # {1,3} -> |Psi+>
        [heraldChans[1], heraldChans[3]],  # {2,4} -> |Psi+>
        [heraldChans[0], heraldChans[3]],  # {1,4} -> |Psi->
        [heraldChans[1], heraldChans[2]],  # {2,3} -> |Psi->
    ], windowSize)
    
    # --- Measurement ---
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    sn.timeTrace.measure(10000, waitFinished=False, savePTU=False)
    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData()
        plt.clf()
        plt.plot(times, counts[ciChans[0]], linewidth=2.0, label='|Psi+> {1,3}')
        plt.plot(times, counts[ciChans[1]], linewidth=2.0, label='|Psi+> {2,4}')
        plt.plot(times, counts[ciChans[2]], linewidth=2.0, label='|Psi-> {1,4}')
        plt.plot(times, counts[ciChans[3]], linewidth=2.0, label='|Psi-> {2,3}')
        plt.xlabel('Time [s]')
        plt.ylabel('Counts [Cts/s]')
        plt.legend()
        plt.title("Bell State Coincidences")
        plt.pause(0.1)
        if finished:
            break
    plt.show(block=True)