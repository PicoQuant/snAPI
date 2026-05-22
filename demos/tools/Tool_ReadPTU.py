from snAPI.Main import *

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