from snAPI.Main import *

if(__name__ == "__main__"):
    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    sn.loadIniConfig("C:\Data\PicoQuant\Configs\device.ini")
    # complete device config structure
    sn.logPrint(json.dumps(sn.deviceConfig, indent=2))
    sn.logPrint()
    # device serial number (name)
    sn.logPrint("Serial Number:", sn.deviceConfig["ID"])
    # trigger level of all channels 
    for channel in sn.deviceConfig["ChansCfg"]:
        sn.logPrint("Chan", channel["Index"], "- TrigLvl:", channel["TrigLvl"])

    # trigger edge of channel 2 with 'get()' syntax (this is the second channel - the first one has index 0)
    sn.logPrint()
    sn.logPrint("Chan 2 - Trigger Edge:", "Rising" if sn.deviceConfig["ChansCfg"][1]["TrigEdge"] == 1 else "Falling")
