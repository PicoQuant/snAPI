from snAPI.Main import *

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\HH400-PMT-cw-1MHz.ptu")
    sn.initDevice(MeasMode.T2)
    sn.unfold.measure(1000,1024*1024*1024, True, True)
    times, channels  = sn.unfold.getData()
    sn.logPrint("from unfold data")
    sn.logPrint("channel |   timetag") 
    sn.logPrint("-------------------")
    for i in range(25):
        sn.logPrint(f"{channels[i]:9} | {times[i]:7}")