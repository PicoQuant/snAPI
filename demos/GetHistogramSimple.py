from snAPI.Main import *
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())

if(__name__ == "__main__"):
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.histogram.measure(1000,True,True)
    data, bins = sn.histogram.getData()
    if len(data):
        plt.clf()
        plt.plot(bins, data[0], linewidth=2.0, label='sync')
        plt.plot(bins, data[1], linewidth=2.0, label='chan1')
        plt.plot(bins, data[2], linewidth=2.0, label='chan2')
        plt.plot(bins, data[3], linewidth=2.0, label='chan3')
        plt.plot(bins, data[4], linewidth=2.0, label='chan4')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Counts / Time")
        plt.pause(0.01)

    plt.show(block=True)