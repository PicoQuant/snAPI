# -*- coding: utf-8 -*-
"""
Spyder Editor

"""




import time
import numpy as np
import matplotlib.pyplot as plt
from snAPI.Main import snAPI, MeasMode

sn = snAPI()
sn.getDevice()
sn.initDevice(MeasMode.T3)

# Time Gating
GateStart = 36300
GateWidth = 3450
ch = sn.manipulators.herald(0, [1,2], GateStart, GateWidth, True)

# Measure
tic = time.time()
sn.histogram.measure(2000, waitFinished=True, savePTU=False)
print(time.time()-tic)

# Plot
data, bins = sn.histogram.getData()
print(data.shape, bins.shape)

plt.figure()
plt.plot(bins*1e-3, data[0])
plt.plot(bins*1e-3, data[1])
plt.plot(bins*1e-3, data[2])
plt.plot(bins*1e-3, data[ch[0]])
plt.plot(bins*1e-3, data[ch[1]])
plt.show()
    



    
