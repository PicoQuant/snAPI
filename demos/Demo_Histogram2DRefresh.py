from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
from threading import Timer
import time

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
    
    wideField = True
    if wideField:
        sn.histogram2d.setHisto2dParams(refChannel=0, channelX=1, channelY=2, offsetX=4000, offsetY=5500, 
                                    binWidthX=1, binWidthY=1, numBinsX=1000, numBinsY=1000)
    else:
        sn.histogram2d.setHisto2dParams(refChannel=0, channelX=1, channelY=2, offsetX=0, offsetY=0, 
                                    binWidthX=10, binWidthY=10, numBinsX=1000, numBinsY=1000)
    # activate ToT mode and     
    sn.histogram2d.setHisto2dTotMode(totMode=True, timewalkFactor=0.7)
    sn.histogram2d.setHisto2dRecoveryTimingCorrection(diffTimeMin=50000, correctionX=-33, correctionY=250, timewalkCorrectionFactor=-0.2)
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
