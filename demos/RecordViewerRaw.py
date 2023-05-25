from snAPI.Main import *

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    #sn.getFileDevice(r"E:\Data\PicoQuant\HH400-PMT-cw-1MHz.ptu")
    sn.initDevice(MeasMode.T2)
    sn.raw.measure(1000,1024*1024*1024, True, True)
    data = sn.raw.getData(25)
    sn.logPrint("from raw data")
    sn.logPrint("channel |   timetag")
    sn.logPrint("-------------------")
    for i in range(25):
        time = sn.raw.timeTag_T2(data[i])
        chan = sn.raw.channel(data[i])
        sn.logPrint(f"{chan:9} | {time:7}")