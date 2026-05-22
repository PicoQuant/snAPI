from snAPI.Main import *

# Coincidence timestamps from an unfolded photon stream
# =====================================================
# This demo demonstrates how coincidence events can be generated from photon
# events recorded with a time tagging device or from a PTU file, and how their
# time tags can be accessed directly.
#
# The script creates a virtual coincidence channel from two detector channels,
# Ch1 and Ch2. Photon events on these channels are tested against the selected
# coincidence window, and matching events are written to a new coincidence
# channel in the unfolded data stream.
#
# Setup:
# The input channels used to form the coincidence are selected in the list
# `chans`. The coincidence window defines the maximum allowed time difference
# between the events. With `keepChannels=True`, the original photon events remain
# in the stream in addition to the generated coincidence events. Setting
# `keepChannels=False` keeps only the coincidence events.
#
# During acquisition, the script reads blocks from the unfolded stream and prints
# the channel number together with the corresponding time tag. It then filters
# the unfolded data by the virtual coincidence channel index and prints the time
# tags of the detected coincidence events.
#
# This is useful for applications where the timing of coincidence events is
# required directly, for example for event filtering, coincidence-triggered
# analysis, or custom post-processing workflows based on photon time tags.

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI()
    sn.getDevice()
    
    # offline processing:
    #sn.getFileDevice(r"mnt\d\Data\PicoQuant\Test2.ptu")
    sn.initDevice(MeasMode.T3)
    
    # set the trigger level
    sn.loadIniConfig("config\TH260N.ini")
    
    #list of channels to build the coincidence from
    chans= [1,2]
    ciIndex = sn.manipulators.coincidence(chans, 100000000, mode = CoincidenceMode.CountAll, 
                                time = CoincidenceTime.Average,
                                keepChannels=True) #set keepChannels to false to get the coincidences only
    # ciIndex is the 'channel number' where the coincidences are stored
    sn.logPrint(f"coincidence index: {ciIndex}")

    # block measurement for continuous (acqTime = 0 is until stop) measurement
    sn.unfold.startBlock(acqTime=10, size=1024*1024*1024, savePTU=False)
    
    while(True):
        times, channels  = sn.unfold.getBlock()
        
        if(len(times) > 99):
            sn.logPrint("new data block:")
            sn.logPrint("  channel | time tag") 
            sn.logPrint("--------------------")
            
            # only print the first 10 time tags per block out
            # for performance reasons
            # but it here should all data be stored to disc
            for i in range(100):
                sn.logPrint(f"{channels[i]:9} | {times[i]:8}")
                
                
            # filter the time tags of coincidences
            ciTimes = sn.unfold.getTimesByChannel(ciIndex)
            sn.logPrint("new coincidence block:")
            sn.logPrint("time tag") 
            sn.logPrint("--------")
            if len(ciTimes) > 9:
                for i in range(10):
                    sn.logPrint(f"{ciTimes[i]:8}")
            
            
        #if sn.unfold.finished.contents:
            #break
        
    sn.logPrint("end")
