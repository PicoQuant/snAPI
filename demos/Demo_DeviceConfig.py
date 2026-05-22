from snAPI.Main import *

# Reading and printing the device configuration
# =============================================
# This demo demonstrates how to access and inspect the configuration of a
# PicoQuant time tagging device with snAPI.
#
# The script initializes the device, loads an ini configuration file, and then
# prints the complete device configuration structure. This structure contains
# device information as well as the current settings of the input channels.
#
# Setup:
# The device type is selected by the ini file loaded with `loadIniConfig`. The
# example uses `config\MH.ini`, which should be replaced by the configuration
# file matching the connected device and measurement setup.
#
# After loading the configuration, the script reads selected entries from
# `sn.deviceConfig`, such as the device ID, the trigger or discriminator levels
# of all channels, and the enable state of a selected channel.
#
# This is useful for checking whether a device has been configured correctly,
# verifying channel settings before a measurement, and learning how to access
# configuration values programmatically for use in custom scripts.

if(__name__ == "__main__"):
    
    # set the library for your device type
    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    
    # set the configuration for your device type
    sn.loadIniConfig("config\MH.ini")
    
    # print complete device config structure
    sn.logPrint(json.dumps(sn.deviceConfig, indent=2))
    sn.logPrint()
    
    # device serial number (name)
    sn.logPrint("----------------------------------------------")
    sn.logPrint("Serial Number:", sn.deviceConfig["ID"])
    
    # trigger/ discriminator level of all channels 
    sn.logPrint("----------------------------------------------")
    for channel in sn.deviceConfig["ChansCfg"]:
        if channel["TrigMode"] == "Edge":
            sn.logPrint("Chan", channel["Index"], "- TrigLvl:", channel["TrigLvl"])
        elif channel["TrigMode"] == "CFD":
            sn.logPrint("Chan", channel["Index"], "- DiscrLvl :", channel["DiscrLvl"])

    # print enable state channel 2 (this is the second channel - the first one has index 0)
    sn.logPrint("----------------------------------------------")
    sn.logPrint("Chan 2:", "enabled" if sn.deviceConfig["ChansCfg"][1]["ChanEna"] else "disabled")
