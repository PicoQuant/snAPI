from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg', force=True)
from matplotlib import pyplot as plt
import numpy as np
import time

# Full g(3)(tau1, tau2) — 2D Third-Order Correlation
# =====================================================
# tau1Values directly represents the physical τ1 = t_Ch2 − t_Ch1.
# Shear correction is applied per step.
#
#   tau1 < 0 (Ch2 before Ch1): delay Ch2 by |tau1|  →  ci_12 fires at t_Ch1
#   tau1 > 0 (Ch2 after Ch1):  delay Ch1 by tau1    →  ci_12 fires at t_Ch2
#   tau1 = 0: no delay, CoincidenceTime.First
#   Shear correction for tau1 != 0:
#     tau2_corrected = tau2_measured + tau1  →  np.roll(data, tau1/bin_width)

if __name__ == "__main__":

    sn = snAPI()
    ptuFile = r"\mnt\d\Data\PicoQuant\g2t.ptu"

    ch1 = 1
    ch2 = 2
    ch3 = 3

    # --- g(2) parameters ---
    g2WindowSize = 20000      # [ps]
    g2BinWidth   = 50         # [ps]
    g2normalization = False
    
    # --- coincidence parameters ---
    windowSize   = 1000       # [ps]
    tau1Stop = 10000          # [ps]
    tau1Step = 250            # [ps]
    coincidenceTime = CoincidenceTime.Average

    bin_width_s = g2BinWidth * 1e-12   # bin width in seconds (for shear shift)

    tau1Positive = np.arange(tau1Step, tau1Stop + tau1Step, tau1Step)
    tau1Values   = np.concatenate([-tau1Positive[::-1], [0], tau1Positive])

    g3Data = None
    g2Bins = None

    plt.figure(figsize=(10, 8))
    sn.getFileDevice(ptuFile)
    sn.initDevice(MeasMode.T2)

    for i, tau1 in enumerate(tau1Values):
        sn.logPrint(f"Step {i+1}/{len(tau1Values)}: tau1 = {tau1} ps")

        if tau1 < 0:
            # Ch2 before Ch1 → delay Ch2, Ch1 is reference (First = Ch1)
            ch2_used = sn.manipulators.delay(ch2, float(-tau1), keepSourceChannel=True)
            ci_12 = sn.manipulators.coincidence(
                [ch1, ch2_used],
                windowSize,
                mode=CoincidenceMode.CountOnce,
                time=coincidenceTime,
                keepChannels=True
            )
        elif tau1 > 0:
            # Ch2 after Ch1 → delay Ch1, Ch2 is reference (First = Ch2)
            ch1_used = sn.manipulators.delay(ch1, float(tau1), keepSourceChannel=True)
            ci_12 = sn.manipulators.coincidence([ch2, ch1_used], windowSize, mode=CoincidenceMode.CountOnce, time=coincidenceTime )
        else:
            # tau1 = 0: no delay
            ci_12 = sn.manipulators.coincidence(
                [ch1, ch2], windowSize, mode=CoincidenceMode.CountOnce, time=coincidenceTime)

        sn.correlation.setG2Parameters(ci_12, ch3, g2WindowSize, g2BinWidth, normalization=g2normalization)
        sn.correlation.measure(0, waitFinished=True, savePTU=False)

        data, bins = sn.correlation.getG2Data()
        data = np.copy(data)

        if g3Data is None:
            g3Data = np.zeros((len(tau1Values), len(data)))
            g2Bins  = np.copy(bins)

        if tau1 < 0:
            shift = int(round(tau1 * 1e-12 / bin_width_s))
            data = np.roll(data, shift)

        g3Data[i, :] = data

        plt.clf()
        plt.pcolormesh(g2Bins * 1e12, tau1Values[:i+1], g3Data[:i+1, :],
                       shading='auto', cmap='hot')
        plt.colorbar(label='Counts')
        plt.xlabel('tau2 [ps]')
        plt.ylabel('tau1 [ps]')
        plt.title(f"g(2)(tau1, tau2) — Step {i+1}/{len(tau1Values)}")
        plt.tight_layout()
        plt.pause(0.1)

        sn.correlation.stopMeasure()
        sn.manipulators.clearAll()

    plt.title("g(2)(ci12, ch3; tau1, tau2) — coincidence-conditioned g(2)")
    plt.show(block=True)