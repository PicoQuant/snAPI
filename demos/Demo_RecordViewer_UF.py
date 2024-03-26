from snAPI.Main import *

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI()
    sn.getDevice()
    
    #sn.getFileDevice(r"E:\Data\PicoQuant\default.ptu")          # T2 File
    #sn.getFileDevice(r"E:\Data\PicoQuant\G2_T3_sameTTs.ptu")   # T3 File
    sn.initDevice(MeasMode.T3)
    #sn.setLogLevel(LogLevel.Config, True)
    sn.loadIniConfig("config\MH.ini")
    
    countRates = sn.getCountRates()
    
    # 1GB 
    resolution = sn.deviceConfig['Resolution']
    sn.unfold.measure(acqTime=1000, size=1024*1024*1024, waitFinished=True, savePTU=False)
    times, channels  = sn.unfold.getData()
    
    if sn.deviceConfig['MeasMode'] == 3: # T3
        sn.logPrint("Unfold T3 Data:")
        sn.logPrint("  channel | syncCtr |    dTime |   absTime") 
        sn.logPrint("------------------------------------------")
            
        syncPeriod = 1e12 / countRates[0] # in ps
        for i in range(start,start+length):
            sn.logPrint(f"{channels[i]:9} | {sn.unfold.nSync_T3(times[i]):7} | {(resolution * sn.unfold.dTime_T3(times[i])):8} | {sn.unfold.abs_T3(times[i]):.1f}")

    else: # T2
        sn.logPrint("Unfold T2 Data:")
        sn.logPrint("  channel |   absTime") 
        sn.logPrint("---------------------")
            
        syncPeriod = 1e12 / countRates[0] # in ps
        for i in range(start,start+length):
            sn.logPrint(f"{channels[i]:9} | {times[i]:.1f}")
            
    sn.logPrint("end")