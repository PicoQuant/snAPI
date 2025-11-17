from snAPI.Main import *
import matplotlib

matplotlib.use("TkAgg", force=True)
from matplotlib import pyplot as plt

if __name__ == "__main__":

    sn = snAPI()
    sn.getDevice("1000509")
    sn.initDevice(MeasMode.T2)

    sn.loadIniConfig(r"config\HH500.ini")

    history_size = 1
    sn.setLogLevel(LogLevel.DataFile, True)
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(history_size)
    
    
    # set Marker (1..4)
    sn.device.setMarkerEdges(1, 0, 0, 0)
    sn.device.setMarkerEnable(1, 1, 1, 0)
    
    # set Image Tag
    sn.setMeasurementSubMode(subMode=MeasSubMode.Image)
    # Marker (1) in TTTR stream defining a line start
    sn.addIntTag("ImgHdr_LineStart", 1)
    # Marker (2) in TTTR stream defining a line end
    sn.addIntTag("ImgHdr_LineStop", 2)
    # Marker (3) in TTTR stream defining a frame change
    sn.addIntTag("ImgHdr_Frame", 3)
        
    #  Dimension of the measurement: 1 = Point; 2 = Line; 3 = Image; 4 = Stack
    sn.addIntTag("ImgHdr_Dimensions", 3)
    
    # Identifies the scanner hardware: 
    # (1 = PI E-710; 3 = LSM; 5 = PI Line WBS; 6 = PI E-725; 7 = PI E-727; 8 = MCL; 9 = FLIMBee; 10 = ScanBox)
    #sn.addIntTag("ImgHdr_Ident", 3)
    
    # Scan direction, defining the configuration of fast and slowscan axis
    # First Axis = Fast Scan axis, Second Axis = SlowAxis
    # PI_SCANMODE_XY(0) = X-Y Scan (default)
    # PI_SCANMODE_XZ(1) = X-Z Scan
    # PI_SCANMODE_YZ(2) = Y-Z Scan
    #sn.addIntTag("ImgHdr_ScanDirection", 0)
    
    # Scan pattern:
    # TRUE identifies bidirectional scanning
    #  1st line forward scan
    #  2nd line backward scan
    #  3rd line forward 
    #  4th line backward; ...)
    # FALSE identifies monodirectional scanning (all lines forward - default)
    #sn.addBoolTag("ImgHdr_BiDirect", False)

    # If > 0, the image was recorded using a sinuidal instead of a linear movement
    # Value represents percentage of the sinus wave used for the measurement (0-100%)
    # (default: 0)
    #sn.addIntTag("ImgHdr_SinCorrection", 0)

    # [ms]
    # Integration time per pixel for image measurements
    sn.addIntTag("ImgHdr_TimePerPixel", 20)
    
    # [µm]
    # X, Y, Z Position of measurement (interpretation depends on ImgHdr_Dimensions 
    # for point measurements: the coordinate of measurement 
    # for line: the start point 
    # for images: the offset of the upper left edge of the image)
    sn.addFloatTag("ImgHdr_X0", 0.0)
    sn.addFloatTag("ImgHdr_Y0", 0.0)
    sn.addFloatTag("ImgHdr_Z0", 0.0)
    
    # Number of pixels in the fast scan direction (for image measurements)
    sn.addIntTag("ImgHdr_PixX", 256)
    # Number of pixels in the slow scan direction (for image measurements)
    sn.addIntTag("ImgHdr_PixY", 256)
    #  [µm]; Resolution of a single pixel (line and image measurements)
    sn.addFloatTag("ImgHdr_PixResol", 1.0)
    
    #sn.addIntTag("TestInt", 9223372036854775807, 123)
    #sn.addFloatArrayTag("TestFloatArray", [1.1, 2.3, 3.3, 4.4])
    #sn.addByteArrayTag("TestIntArray", [0,1,2,3,4,0,0,0])
        
    # set the file name
    sn.setPTUFilePath("out.ptu")

    sn.timeTrace.measure(int(history_size * 1e3), waitFinished=False, savePTU=True)
    ft = 0
    while True:
        finished = sn.timeTrace.isFinished()
        #if finished:
        #    sn.timeTrace.t0.value = 0
        counts, times = sn.timeTrace.getData()
        plt.clf()

        plt.plot(times, counts[0], linewidth=2.0, label="sync")
        for c in range(1, 1 + sn.deviceConfig["NumChans"]):
            plt.plot(times, counts[c], linewidth=2.0, label=f"chan{c}")
        plt.grid()
        plt.xlabel("Time [s]")
        plt.ylabel("Counts[Cts/s]")
        plt.yscale('log', base=10, nonpositive='clip')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)

        if finished:
            ft+=1
            if ft > 10:
                break

    plt.show(block=True)
    plt.close()
