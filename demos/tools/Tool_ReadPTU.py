from snAPI.Main import *

# Read PTU file contents and unfolded photon records
# ========================================================
# This tool demonstrates how to open a PTU file with snAPI and inspect both its
# metadata and photon event records.
#
# The script opens a PTU file as a snAPI file device, reads the device
# configuration and measurement description from the file, and prints both
# structures in JSON format. This provides access to information such as the
# recorded device settings and the number of photon records stored in the file.
#
# Setup:
# The PTU file path is defined directly in the script and should be adapted to
# the file that should be inspected. The variables `start` and `length` select
# which range of unfolded photon records is printed.
#
# After reading the metadata, the script unfolds the stored photon stream and
# retrieves the event times and channel numbers with `sn.unfold.getData`.
#
# The selected unfolded records are then printed as channel number and absolute
# event time. This is useful for quickly checking the contents of a PTU file,
# inspecting individual photon events, and verifying that recorded data can be
# accessed correctly before running further analysis.

if(__name__ == "__main__"):

    # PTU data
    start = 0
    length = 10
    
    sn = snAPI()
    sn.getFileDevice(r"C:\Data\PicoQuant\default.ptu")
    sn.getDeviceConfig()
    sn.logPrint(json.dumps(sn.deviceConfig, indent=2))
    
    sn.getMeasDescription()
    sn.logPrint(json.dumps(sn.measDescription, indent=2))
    
    sn.unfold.measure(acqTime=1000, size=int(sn.measDescription["NumRecs"]), waitFinished=True)
    times, channels  = sn.unfold.getData()
    sn.logPrint(f"Unfold data records: {len(times)}")
    sn.logPrint("  channel |  absTime") 
    sn.logPrint("--------------------")
    
    for i in range(start,start+length):
        sn.logPrint(f"{channels[i]:9} | {times[i]:8}")
