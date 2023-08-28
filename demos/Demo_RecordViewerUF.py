from snAPI.Main import *

if(__name__ == "__main__"):

    start = 0
    length = 10

    sn = snAPI(libType=LibType.HH)
    sn.getDevice()
    
    sn.getFileDevice(r"C:\Data\PicoQuant\default_1.ptu")
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig("config\HH.ini")
    
    # 4GB 
    sn.unfold.measure(size=4*134217728)
    times, channels = sn.unfold.getData()

    sn.logPrint("channel |        timetag") 
    sn.logPrint("------------------------")
    sn.logPrint(f"{channels[0]:7} | {times[0]:14}")
    for i in range(start,start+length):
        sn.logPrint(f"{channels[i]:7} | {times[i]:14}")