from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
from threading import Timer
import time

# Live-refresh PNR 2D histogram
# ==============================
# This demo shows how to combine the PNR (Photon Number Resolving) manipulator
# with a 2D histogram for real-time monitoring of single-photon detector timing
# characteristics. It works with a PicoQuant time-tagging device or a PTU file.
#
# Processing pipeline:
# 1. The pnr manipulator receives raw photon events from a reference channel
#    and two detector channels (rising and falling edge of the same detector).
#    It applies time-over-threshold (ToT) mode to reconstruct photon pulse widths,
#    corrects for time-walk using a configurable factor, and suppresses events
#    that arrive while the detector is still in its recovery window (diffMin/diffMax
#    define the valid SYNC-to-last-SYNC gap in ps — events outside this range are
#    discarded). The manipulator outputs two corrected virtual channels.
#
# 2. The histogram2D accumulates the arrival-time differences from the reference
#    channel to each of the two pnr output channels into a 2D matrix. Axis offsets,
#    bin widths and bin counts are configured via setHisto2dParams. The wideField
#    flag switches between a coarse overview window and a fine-resolution window
#    around the signal peak.
#
# During acquisition the script repeatedly reads the current 2D histogram, updates
# both linear and logarithmic color-scaled plots, then clears the accumulated data
# so each refresh interval shows only freshly acquired events.
#
# This is useful for optimizing detector bias, threshold, and timing alignment in
# PNR detector characterization setups.

if(__name__ == "__main__"):

    sn = snAPI()
    #sn.getDevice("1050002")
    #sn.initDevice(measMode=MeasMode.T2)
    #sn.device.setInputEdgeTrig(5,-20,0)
    #sn.device.setInputEdgeTrig(7,-35,1)
    sn.getFileDevice(r"D:\Data\QuantumOpus_PNR\Ch1Rising70mV_Ch2Falling70mV_HighestRate18Mcps.ptu")
    #sn.getFileDevice(r"D:\Data\QuantumOpus_PNR\Ch1Rising70mV_Ch2Falling70mV_HigherRate13Mcps.ptu")
    #sn.getFileDevice(r"D:\Data\QuantumOpus_PNR\Ch1Rising70mV_Ch2Falling70mV_HighRate.ptu")
    
    #sn.loadIniConfig(r"config\TH260N.ini")
    sn.setLogLevel(LogLevel.Config, False)
    sn.setLogLevel(LogLevel.Api, True)
    sn.setLogLevel(LogLevel.Device, True)
    
    cPNR = sn.manipulators.pnr(channelRef=0, channelX=1, channelY=2, diffMin = 0, diffMax = 50000, xCorr=-3, yCorr=255, timewalkFactor=0.13, toT=True)
    wideField = False
    if wideField:
        sn.histogram2d.setHisto2dParams(refChannel=0, channelX=cPNR, channelY=cPNR+1, offsetX=0, offsetY=0, 
                                    binWidthX=10, binWidthY=10, numBinsX=1000, numBinsY=1000)
    else:
        sn.histogram2d.setHisto2dParams(refChannel=0, channelX=cPNR, channelY=cPNR+1, offsetX=4000, offsetY=1500, 
                                    binWidthX=1, binWidthY=1, numBinsX=1000, numBinsY=1000)

    sn.histogram2d.measure(acqTime=0, waitFinished=True, savePTU=False)
    data = sn.histogram2d.getData()

    # prepare plot
    extent = [
        sn.histogram2d.offsetX, sn.histogram2d.offsetX + sn.histogram2d.binWidthX * sn.histogram2d.numBinsX,
        sn.histogram2d.offsetY, sn.histogram2d.offsetY + sn.histogram2d.binWidthY * sn.histogram2d.numBinsY
    ]
    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(10, 4))
    fig.canvas.manager.set_window_title(sn.deviceConfig['ID'])
    im_lin = ax_lin.imshow(data, origin="lower", aspect="auto", cmap=plt.cm.turbo, extent=extent)
    fig.colorbar(im_lin, ax=ax_lin, label="counts")
    ax_lin.set_title("Linear")
    log_norm = matplotlib.colors.LogNorm(vmin=1, vmax=max(1.0, float(np.max(data))))
    im_log = ax_log.imshow(np.maximum(data, 1), origin="lower", aspect="auto", cmap=plt.cm.turbo, norm=log_norm, extent=extent)
    fig.colorbar(im_log, ax=ax_log, label="counts (log)")
    ax_log.set_title("Log")
    for ax in (ax_lin, ax_log):
        ax.set_xlabel(f"dX [ps]")
        ax.set_ylabel(f"dY [ps]")
    fig.tight_layout()

    # plotting loop
    while True:
        finished = sn.histogram2d.isFinished()
        data = sn.histogram2d.getData()
        
        # plot
        vmax = float(np.max(data))
        vmax = 1.0 if (not np.isfinite(vmax) or vmax <= 0) else vmax
        im_lin.set_data(data)
        im_lin.set_clim(0.0, vmax)
        im_log.set_data(np.maximum(data, 1))
        im_log.norm.vmax = max(1.0, vmax)
        fig.canvas.draw_idle()

        # clear measure data (refresh chart)
        sn.histogram2d.clearMeasure()
        plt.pause(1)
            
        if finished:
            break
    
    plt.ioff()
    plt.show(block=True)
