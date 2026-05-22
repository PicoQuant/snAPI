import sys
import os
import time 

from snAPI.Main import *
if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    sn.loadIniConfig("config\PH330_Edge.ini")
    
    while True:                
        cntRs = sn.getCountRates()
        time.sleep(1)