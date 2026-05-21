import sys      
import os      
import time      
import numpy as np      
from scipy import signal      
from snAPI.Main import *      
import matplotlib     
import matplotlib.colors as colors     
import matplotlib.pyplot as plt      
from matplotlib.gridspec import GridSpec      
from matplotlib.widgets import Button      
matplotlib.use('TkAgg', force=True)      
print("Switched to:", matplotlib.get_backend())

# Threshold scan with count rate and timing-quality metrics
# =========================================================
# This tool helps determine suitable trigger or discriminator levels for a
# PicoQuant time tagging device by measuring both the count rate and timing
# response while sweeping the trigger threshold.
#
# The script initializes the device, loads an ini configuration file, and scans
# the trigger level over a defined voltage range. For each trigger level, the
# same setting is applied to all detector channels, using either level triggering
# or CFD triggering depending on the loaded device configuration.
#
# Setup:
# The device configuration is loaded from an ini file. The trigger-level scan
# range is defined directly in the script by the start, stop, and step values.
# The channel to analyze, histogram bin width, number of bins, and RMS evaluation
# window can also be adjusted in the script.
#
# At each trigger level, the tool acquires a histogram relative to the sync
# input. From the selected detector channel, it calculates the count rate, the
# full width at half maximum (FWHM), the center of gravity of the histogram peak,
# and the RMS deviation around the peak.
#
# During the scan, the script displays a 2D histogram heatmap showing how the
# timing distribution changes with trigger threshold. In parallel, it plots the
# count rate, FWHM, center of gravity, and RMS deviation as functions of the
# trigger level.
#
# This is useful for finding a trigger threshold that provides a good compromise
# between signal rate and timing performance, checking threshold-dependent timing
# shifts, optimizing detector channel settings, and preparing a stable
# configuration before running a measurement.

Channel = 2  # Channel to analyze (0: Sync, 1: Chan1, 2: Chan2, etc.)
Start = -80  # mV, start of trigger threshold range
Stop = 0     # mV, end of trigger threshold range
Step = 2      # mV, step size for trigger threshold range
BinWidth = 5  # ps, histogram bin width
NumBins = 20000  # Number of bins in histogram (adjust based on expected peak width and range)

# Configuration for RMS window size (adjust based on your expected peak width)  
RMS_WINDOW_BINS = 2000  # Number of bins on each side of peak for RMS calculation  

def calculate_fwhm(data, bins):      
    """Calculate Full Width at Half Maximum of histogram peak"""      
    if len(data) == 0 or np.max(data) == 0:      
        return 0      

    # Find peak      
    peak_idx = np.argmax(data)      
    peak_value = data[peak_idx]      
    half_max = peak_value / 2      

    # Find points where histogram crosses half maximum      
    left_idx = peak_idx      
    while left_idx > 0 and data[left_idx] > half_max:      
        left_idx -= 1      

    right_idx = peak_idx      
    while right_idx < len(data) - 1 and data[right_idx] > half_max:      
        right_idx += 1      

    # Calculate FWHM in picoseconds      
    if left_idx < right_idx:      
        fwhm_bins = right_idx - left_idx      
        fwhm_time = fwhm_bins * (bins[1] - bins[0]) if len(bins) > 1 else 0      
        return fwhm_time      
    return 0      
    
def calculate_center_of_gravity(data, bins):    
    """Calculate center of gravity (mean time) of histogram peak"""    
    if len(data) == 0 or np.sum(data) == 0:    
        return 0  

    # Find peak and define a window around it using FWHM  
    peak_idx = np.argmax(data)  
    peak_value = data[peak_idx]  
    half_max = peak_value / 2  

    # Find FWHM boundaries  
    left_idx = peak_idx  
    while left_idx > 0 and data[left_idx] > half_max:  
        left_idx -= 1  

    right_idx = peak_idx  
    while right_idx < len(data) - 1 and data[right_idx] > half_max:  
        right_idx += 1  

    # Use only the peak region for CoG calculation  
    peak_data = data[left_idx:right_idx+1]  
    peak_bins = bins[left_idx:right_idx+1]  

    if len(peak_data) == 0 or np.sum(peak_data) == 0:  
        return 0  
        
    total_counts = np.sum(peak_data)    
    mean_time = np.sum(peak_data * peak_bins) / total_counts    
    return mean_time  
    
def calculate_rms_deviation(data, bins, center_of_gravity, window_bins=RMS_WINDOW_BINS):    
    """Calculate RMS deviation (standard deviation) from center of gravity  

    Uses a fixed window around the peak for robustness, independent of FWHM.  
    """  
    if len(data) == 0 or np.sum(data) == 0:  
        return 0  

    # Find peak  
    peak_idx = np.argmax(data)  

    # Use fixed window around peak (independent of FWHM)  
    left_idx = max(0, peak_idx - window_bins)  
    right_idx = min(len(data) - 1, peak_idx + window_bins)  

    # Use the peak region for RMS calculation  
    peak_data = data[left_idx:right_idx+1]  
    peak_bins = bins[left_idx:right_idx+1]  

    if len(peak_data) == 0 or np.sum(peak_data) == 0:  
        return 0  
        
    total_counts = np.sum(peak_data)  
    variance = np.sum(peak_data * (peak_bins - center_of_gravity)**2) / total_counts  
    rms = np.sqrt(variance)  
    return rms  

class ZoomHeatmap:      
    def __init__(self, fig, ax_heatmap, heatmap_data, trigger_levels):      
        self.fig = fig      
        self.ax_heatmap = ax_heatmap      
        self.heatmap_data = heatmap_data      
        self.trigger_levels = trigger_levels      
        self.original_extent = None      
        self.current_extent = None      

        # Store original limits      
        self.original_xlim = None      
        self.original_ylim = None      

        # Connect keyboard events      
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)      

    def on_key_press(self, event):      
        """Handle keyboard shortcuts for zoom control"""      
        if event.key == 'r':  # Reset zoom      
            self.reset_zoom()      
        elif event.key == 'x':  # Zoom to x-axis only      
            self.zoom_x_axis()      
        elif event.key == 'y':  # Zoom to y-axis only      
            self.zoom_y_axis()      
        elif event.key == 'home':  # Home view      
            self.home_view()      

    def reset_zoom(self):      
        """Reset zoom to original view"""      
        if self.original_xlim and self.original_ylim:      
            self.ax_heatmap.set_xlim(self.original_xlim)      
            self.ax_heatmap.set_ylim(self.original_ylim)      
            self.fig.canvas.draw_idle()      

    def zoom_x_axis(self):      
        """Zoom to fit x-axis"""      
        self.ax_heatmap.autoscale(axis='x', tight=True)      
        self.fig.canvas.draw_idle()      

    def zoom_y_axis(self):      
        """Zoom to fit y-axis"""      
        self.ax_heatmap.autoscale(axis='y', tight=True)      
        self.fig.canvas.draw_idle()      

    def home_view(self):      
        """Reset to home view"""      
        self.ax_heatmap.set_xlim(self.original_xlim)      
        self.ax_heatmap.set_ylim(self.original_ylim)      
        self.fig.canvas.draw_idle()      

    def store_original_limits(self):      
        """Store the original plot limits"""      
        self.original_xlim = self.ax_heatmap.get_xlim()      
        self.original_ylim = self.ax_heatmap.get_ylim()      

if __name__ == "__main__":      
    # Initialize snAPI      
    sn = snAPI()      
    sn.getDevice()      
    sn.initDevice(MeasMode.T2)      
    sn.loadIniConfig(r"config\MH.ini")      

    # Configuration      
    numChans = sn.deviceConfig["NumChans"]      
    trigger_levels = np.arange(Start, Stop, Step)  # Trigger threshold range      
    acq_time_per_level = 500  # ms per trigger level      

    # Initialize data storage      
    heatmap_data = np.zeros((len(trigger_levels), NumBins))      
    count_rates = []      
    fwhm_values = []      
    cog_values = []  # Center of gravity values    
    rms_values = []  # RMS deviation values    

    # Set up figure with subplots and navigation toolbar      
    fig = plt.figure(figsize=(20, 10))      
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)      

    # 2D Heatmap subplot (left column, spanning both rows)    
    ax_heatmap = fig.add_subplot(gs[:, 0])      
    ax_count_rate = fig.add_subplot(gs[0, 1])      
    ax_fwhm = fig.add_subplot(gs[1, 1])      
    ax_cog = fig.add_subplot(gs[0, 2])  # Center of gravity plot    
    ax_rms = fig.add_subplot(gs[1, 2])  # RMS deviation plot    

    # Initialize heatmap      
    extent = [0, NumBins * BinWidth,       
              trigger_levels[0], trigger_levels[-1]]      
    heatmap_im = ax_heatmap.imshow(heatmap_data, aspect='auto', origin='lower',         
                               extent=extent, cmap='hot', interpolation='nearest')       
    ax_heatmap.set_xlabel('Time [ps]')      
    ax_heatmap.set_ylabel('Trigger Threshold [mV]')      
    ax_heatmap.set_title('2D Histogram Heatmap\n(Use mouse wheel to zoom, drag to pan, "r" to reset)')      
    plt.colorbar(heatmap_im, ax=ax_heatmap, label='Counts')      

    # Initialize count rate plot      
    count_line, = ax_count_rate.plot([], [], 'b-', linewidth=2)      
    ax_count_rate.set_xlabel('Trigger Threshold [mV]')      
    ax_count_rate.set_ylabel('Count Rate [cps]')      
    ax_count_rate.set_title('Count Rate vs Trigger Threshold')      
    ax_count_rate.grid(True, alpha=0.3)      

    # Initialize FWHM plot      
    fwhm_line, = ax_fwhm.plot([], [], 'r-', linewidth=2)      
    ax_fwhm.set_xlabel('Trigger Threshold [mV]')      
    ax_fwhm.set_ylabel('FWHM [ps]')      
    ax_fwhm.set_title('FWHM vs Trigger Threshold')      
    ax_fwhm.grid(True, alpha=0.3)      

    # Initialize center of gravity plot      
    cog_line, = ax_cog.plot([], [], 'g-', linewidth=2)      
    ax_cog.set_xlabel('Trigger Threshold [mV]')      
    ax_cog.set_ylabel('Center of Gravity [ps]')      
    ax_cog.set_title('Center of Gravity vs Trigger Threshold')      
    ax_cog.grid(True, alpha=0.3)      

    # Initialize RMS deviation plot      
    rms_line, = ax_rms.plot([], [], 'm-', linewidth=2)      
    ax_rms.set_xlabel('Trigger Threshold [mV]')      
    ax_rms.set_ylabel('RMS Deviation [ps]')      
    ax_rms.set_title('RMS Deviation vs Trigger Threshold')      
    ax_rms.grid(True, alpha=0.3)      

    # Enable matplotlib navigation toolbar      
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk      
    from tkinter import Tk      

    # Create zoom controller      
    zoom_controller = ZoomHeatmap(fig, ax_heatmap, heatmap_data, trigger_levels)      

    plt.show(block=False)      

    # Store original limits after initial display      
    zoom_controller.store_original_limits()      

    # Main measurement loop      
    for i, trigLvl in enumerate(trigger_levels):      
        # Convert to Python int to avoid type conversion errors      
        trigLvl_int = int(trigLvl)      

        # Set trigger level for all channels      
        if sn.deviceConfig["SyncTrigMode"] == "Edge":      
            sn.device.setInputEdgeTrig(-1, trigLvl_int, 1)      
            sn.device.setSyncEdgeTrig(-100, 0)      
        elif sn.deviceConfig["SyncTrigMode"] == "CFD":      
            sn.device.setInputCFD(-1, trigLvl_int, 0)      
            sn.device.setSyncCFD(-100, 0)      

        # Configure histogram      
        sn.histogram.setRefChannel(0)      
        sn.histogram.setBinWidth(BinWidth)  
        sn.histogram.setNumBins(NumBins)      

        # Start measurement      
        sn.histogram.measure(acqTime=acq_time_per_level, waitFinished=True, savePTU=False)      

        # Get histogram data      
        data, bins = sn.histogram.getData()

        # Store heatmap data (use first channel or sum all channels)      
        if len(data) > 0:      
            hist_data = data[Channel] if numChans > 0 else data[0]    
            heatmap_data[i, :] = hist_data    

            # Calculate count rate      
            total_counts = np.sum(hist_data)      
            count_rate = total_counts / (acq_time_per_level / 1000.0)  # cps      
            count_rates.append(count_rate)      

            # Calculate FWHM      
            fwhm = calculate_fwhm(hist_data, bins)      
            fwhm_values.append(fwhm)      

            # Calculate center of gravity      
            cog = calculate_center_of_gravity(hist_data, bins)      
            cog_values.append(cog)      

            # Calculate RMS deviation (now independent of FWHM)  
            rms = calculate_rms_deviation(hist_data, bins, cog)      
            rms_values.append(rms)      
    
    
        # Update plots with logarithmic scale after first iteration     
        heatmap_im.set_data(heatmap_data)       
        if i == 0 and np.max(heatmap_data) > 0:      
            # Set LogNorm after we have actual data      
            heatmap_im.set_norm(colors.LogNorm(vmin=1, vmax=np.max(heatmap_data)))      
        elif np.max(heatmap_data) > 0:      
            # Update color limits for subsequent iterations      
            heatmap_im.set_clim(vmin=1, vmax=np.max(heatmap_data))    
    
        # Update count rate plot      
        count_line.set_data(trigger_levels[:i+1], count_rates)      
        ax_count_rate.relim()      
        ax_count_rate.autoscale_view()      

        # Update FWHM plot      
        fwhm_line.set_data(trigger_levels[:i+1], fwhm_values)      
        ax_fwhm.relim()      
        ax_fwhm.autoscale_view()      

        # Update center of gravity plot      
        cog_line.set_data(trigger_levels[:i+1], cog_values)      
        ax_cog.relim()      
        ax_cog.autoscale_view()      

        # Update RMS deviation plot      
        rms_line.set_data(trigger_levels[:i+1], rms_values)      
        ax_rms.relim()      
        ax_rms.autoscale_view()      

        # Refresh display      
        fig.canvas.draw()      
        fig.canvas.flush_events()      
        plt.pause(0.1)      

        sn.logPrint(f"Trigger Level: {trigLvl} mV, Count Rate: {count_rate:.0f} cps, FWHM: {fwhm:.1f} ps, CoG: {cog:.1f} ps, RMS: {rms:.1f} ps")      

    plt.show(block=True)
