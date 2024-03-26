from snAPI.Main import *

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI()
    sn.getDevice()
    
    # offline processing:
    # sn.getFileDevice(r"E:\Data\PicoQuant\G2_T3_sameTTs.ptu")
    sn.initDevice(MeasMode.T2)
    
    # set the trigger level
    sn.loadIniConfig("config\MH.ini")
    
    #list of channels to build the coincidence from
    chans= [1,2]
    ciIndex = sn.manipulators.coincidence(chans, 1000, mode = CoincidenceMode.CountOnce, 
                                time = CoincidenceTime.Last,
                                keepChannels=True) #set keepChannels to false to get the coincidences only
    # ciIndex is the 'channel number' where the coincidences are stored
    sn.logPrint(f"coincidence index: {ciIndex}")

    # block measurement for continuous (acqTime = 0 is until stop) measurement
    sn.unfold.startBlock(acqTime=1000, size=1024*1024*1024, savePTU=False)
    
    while(True):
        times, channels  = sn.unfold.getBlock()
        
        if(len(times) > 9):
            sn.logPrint("new data block:")
            sn.logPrint("  channel | time tag") 
            sn.logPrint("--------------------")
            
            # only print the first 10 time tags per block out
            # for performance reasons
            # but it here should all data be stored to disc
            for i in range(10):
                sn.logPrint(f"{channels[i]:9} | {times[i]:8}")
                
                
            # filter the time tags of coincidences
            ciTimes = sn.unfold.getTimesByChannel(ciIndex)
            sn.logPrint("new coincidence block:")
            sn.logPrint("time tag") 
            sn.logPrint("--------")
            if len(ciTimes) > 9:
                for i in range(10):
                    sn.logPrint(f"{ciTimes[i]:8}")
            
            
        if sn.unfold.finished.contents:
            break
        
        # if otherBreakCondition:
            sn.unfold.stopMeasure

    sn.logPrint("end")