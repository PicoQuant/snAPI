from snAPI.Main import *

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\MH160_Sun.ptu")
    sn.initDevice(MeasMode.T2)
    
    sn.unfold.measure(1000,1024*1024*1024, True, False)
    times, channels  = sn.unfold.getData()
    sn.logPrint("from unfold data")
    sn.logPrint("channel   | timetag") 
    sn.logPrint("-------------------")
    for i in range(100):
        sn.logPrint(f"{channels[i]:9} | {times[i]:7}")