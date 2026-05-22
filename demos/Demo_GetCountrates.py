import sys
import os
import time 

# Reading count rates from a time tagging device
# ==============================================
# This demo demonstrates how to read the current count rates from the input
# channels of a PicoQuant time tagging device with snAPI.
#
# The script initializes the device, loads an ini configuration file, and then
# repeatedly queries the current count rates with `getCountRates`.
#
# Setup:
# The device type and channel settings are selected by the ini file loaded with
# `loadIniConfig`. The example uses `config\PH330_Edge.ini`, which should be
# replaced by the configuration file matching the connected device and
# measurement setup.
#
# The count rates are read once per second. This is useful for checking detector
# signals before starting a measurement, monitoring input activity, optimizing
# optical alignment, and verifying that the configured channels receive the
# expected signal levels.

from snAPI.Main import *
if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    sn.loadIniConfig("config\PH330_Edge.ini")
    
    while True:                
        cntRs = sn.getCountRates()
        time.sleep(1)
