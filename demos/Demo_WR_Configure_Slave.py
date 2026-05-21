from snAPI.Main import *
import time

# White Rabbit slave configuration
# ================================
# This demo demonstrates how to configure a PicoQuant time tagging device as the
# slave unit in a White Rabbit setup.
#
# The script initializes the selected device, assigns a unique MAC address, reads
# and prints the SFP calibration data, and writes a White Rabbit slave init
# script to the device EEPROM. After rebooting or restarting, the unit can then
# automatically start with the configured White Rabbit slave settings.
#
# Setup:
# The master and slave units must be connected directly with a White Rabbit fiber
# link. This configuration script is intended to be run together with the
# corresponding master configuration script. Each device must receive a unique MAC
# address; in this example, the MAC address is chosen to reflect the device ID.
#
# After writing the init script, the device is reinitialized and the script polls
# the White Rabbit status until the slave is locked, calibrated, running in slave
# mode, and tracking the master's phase.
#
# Finally, the script prints the terminal output and reads the White Rabbit time
# from the slave. This can be used to verify that the slave follows the master
# time correctly. This configuration usually only needs to be performed once;
# after the White Rabbit setup is working, the measurement demos can be used
# directly.
#
#
# Disclaimer
# --------------------------------
#
# This demo is only for configuring the slave. It may be better to use the Operational Software for this,
# as it provides a more convenient implementation of the terminal output.
# It is also recommended not to reconfigure the Harp every time you take measurement. Only Do it once. Once the
# White Rabbit is configured and working, use only the measurement demos.
# Both scripts: DEMO_WR_Configure_Master and DEMO_WR_Configure_Slave must be executed at the same time and the Harp
# devices must be be connected directly via a WR fibre optics cable!

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI()
    # Enter the device ID / serial number here:
    sn.getDevice("1045483")
    sn.initDevice(MeasMode.T2)
    
    # Each WR device needs a unique MAC address.
    # We use the device ID here for an easy identification of the device.
    sn.whiteRabbit.setMAC("00-00-01-04-54-83")
    sn.logPrint(f"MAC: \"{sn.whiteRabbit.mac}\"")
    
    # Print the sfp calibration data.
    sn.whiteRabbit.getSFPData()
    sn.logPrint(f"SFP names: \"{sn.whiteRabbit.SFPnames}\"")
    sn.logPrint(f"SFP dTxs: \"{sn.whiteRabbit.SFPdTxs}\"")
    sn.logPrint(f"SFP dRxs: \"{sn.whiteRabbit.SFPdRxs}\"")
    sn.logPrint(f"SFP alphas: \"{sn.whiteRabbit.SFPalphas}\"")
    
    # Set the init script for the master. It will be written to the EEPROM. After starting the
    # Harp Device will automatically boot with this script.
    sn.whiteRabbit.setInitScript("ptp stop\nsfp detect\nsfp match\nmode slave\nptp start\ngui\n")
    sn.logPrint(f"Init Script: \"{sn.whiteRabbit.initScript}\"")
    
    # Initialize the Harp again.
    sn.initDevice(MeasMode.T2)
        
    # Poll the WR status until the Harp device is ready to use.
    readyState = WRstatus.LockedCalibrated.value | WRstatus.ModeSlave.value | WRstatus.ServoTrackPhase.value
    for i in range(100):
        status = sn.whiteRabbit.getStatus()
        sn.logPrint(f"{status:08x}")
        if (status & readyState) == readyState:
            break
        else:
            time.sleep(1)
                
    sn.logPrint(sn.whiteRabbit.getTermOutput())
    # Check whether the master has set the correct UTC time.
    sn.logPrint(f"WR time: {sn.whiteRabbit.getTime()}")
