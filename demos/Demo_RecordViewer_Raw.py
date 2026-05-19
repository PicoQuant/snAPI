from snAPI.Main import *

# Viewing raw photon records from a time tagging device
# =====================================================
# This demo demonstrates how to access raw photon records recorded with a
# PicoQuant time tagging device or loaded from a PTU file.
#
# The script initializes the device in T3 mode, loads an ini configuration file,
# and starts a raw-data measurement. The recorded photon stream is kept in memory
# and then read back with `sn.raw.getData`.
#
# Setup:
# The amount of raw data that can be recorded is limited by the buffer size
# passed to `sn.raw.measure`. In this example, a 1 GB buffer is allocated. The
# measurement can be performed on a connected device or, by using
# `getFileDevice`, on an existing PTU file.
#
# After the measurement, the script iterates over a selected range of raw records
# and prints the decoded channel number together with the corresponding T3
# arrival time. This shows how individual photon records can be inspected before
# applying higher-level analysis such as histograms, correlations, or custom
# event filtering.

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI()
    sn.getDevice()
    
    #sn.getFileDevice(r"C:\Data\PicoQuant\default.ptu")
    sn.initDevice(MeasMode.T3)
    sn.loadIniConfig("config\HH.ini")
    
    # 1GB 
    sn.raw.measure(1000, 1024*1024*1024, True, False)
    data  = sn.raw.getData()
    sn.logPrint("from raw data")
    sn.logPrint("channel   | timetag") 
    sn.logPrint("-------------------")
    
    for i in range(start,start+length):
        sn.logPrint(f"{sn.raw.channel(data[i]):9} | {sn.raw.dTime_T3(data[i]):7}")
