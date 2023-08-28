from snAPI.Main import *

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI(libType=LibType.HH)
    sn.getDevice()
    
    sn.getFileDevice(r"C:\Data\PicoQuant\default.ptu")
    sn.initDevice(MeasMode.T3)
    #sn.setLogLevel(LogLevel.Config, True)
    sn.loadIniConfig("config\HH.ini")
    
    countRates = sn.getCountRates()
    
    # 1GB 
    sn.unfold.setT3Format(UnfoldFormat.Absolute)
    sn.unfold.measure(acqTime=1000, size=1024*1024*1024, waitFinished=True, savePTU=False)
    times, channels  = sn.unfold.getData()
    sn.logPrint("Unfold Data: UnfoldFormat.Absolute")
    sn.logPrint("  channel | absTime") 
    sn.logPrint("-------------------")
    
    for i in range(start,start+length):
        sn.logPrint(f"{channels[i]:9} | {times[i]:7}")
        
    sn.unfold.setT3Format(UnfoldFormat.DTimes)
    sn.unfold.measure(acqTime=1000, size=1024*1024*1024, waitFinished=True, savePTU=False)
    times, channels  = sn.unfold.getData()
    sn.logPrint("Unfold Data: UnfoldFormat.DTimes")
    sn.logPrint("  channel |   dTime") 
    sn.logPrint("-------------------")
    
    for i in range(start,start+length):
        sn.logPrint(f"{channels[i]:9} | {times[i]:7}")
        
    sn.unfold.setT3Format(UnfoldFormat.DTimesSyncCntr)
    sn.unfold.measure(acqTime=1000, size=1024*1024*1024, waitFinished=True, savePTU=False)
    times, channels  = sn.unfold.getData()
    sn.logPrint("Unfold Data: UnfoldFormat.DTimesSyncCntr")
    sn.logPrint("  channel | syncCtr |   dTime |   absTime") 
    sn.logPrint("-----------------------------------------")
        
    syncPeriod = 1e12 / countRates[0] # in ps
    for i in range(start,start+length):
        sn.logPrint(f"{channels[i]:9} | {sn.unfold.nSync_T3(times[i]):7} | {sn.unfold.dTime_T3(times[i]):7} | {(syncPeriod * sn.unfold.nSync_T3(times[i]) + sn.unfold.dTime_T3(times[i])):.1f}")