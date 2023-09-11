# Torsten Krause, PicoQuant GmbH, 2023

import ctypes as ct
import json
import os
import inspect
import sys
import traceback
import typing
import numpy as np

from contextlib import contextmanager
from snAPI.Constants import *
from snAPI.Utils import *


# main class
class snAPI:
    """
This is the main class of the snAPI library. When creating the snAPI object the api is initialized.
Here you have to select the underlying library and therefore the device family you want to work with.
It holds the underlying device dll (dynamic link library), the :obj:`snAPI.deviceConfig`, the measurement classes
and many other API calls. 

Note
----
Creating the snAPI object calls :meth:`initAPI`. Please look there for detailed information.

Parameters
----------
    systemIni: str
        | path to the system.ini file (default: "system.ini")
    libType: LibType (default: LibType.MH)

Returns
-------
    the snAPI object

Example
-------

::

    # This instantiates a snAPI object in sn for TimeHarp260 
    sn = snAPI(libType=LibType.TH260)
        
    """
    dll = ct.WinDLL(os.path.abspath(os.path.join(os.path.dirname(__file__), '.\snAPI64.dll')))
    """
the snAPI.dll

    """

    deviceIDs = [] 
    """
This list contains the IDs serial numbers of the connected devices or the file names of
the opened file devices (files that act as devices) and will be filled after calling :meth:`getDeviceIDs()`.

    """

    deviceConfig = ()
    """
The device config contains all information about the initialized device. To update it it is necessary to call :meth:`getDeviceConfig`.

Note
----
The deviceConfig can not directly written. It is only for checking the current state. To change the configuration, you have to call
the device functions or write the config with :meth:`loadIniConfig` or :meth:`setIniConfig`.
For detailed information read :ref:`configuration`! 

Example
-------
::

    # This is an example of a device config
    
    {
    "DeviceType": 0,
    "FileDevicePath": "",
    "ID": "1045483",
    "Index": 0,
    "Model": "MultiHarp 150 4P",
    "PartNo": "930043",
    "Version": "1.0",
    "BaseResolution": 5.0,
    "Resolution": 5.0,
    "BinSteps": 24,
    "NumChans": 4,
    "NumMods": 2,
    "SyncDivider": 1,
    "SyncTrigMode": "Edge",
    "SyncTrigLvl": -50,
    "SyncTrigEdge": 1,
    "SyncDiscrLvl": -50,
    "SyncZeroXLvL": 0,
    "SyncChannelOffset": 0,
    "SyncChannelEnable": 1,
    "SyncDeadTime": 800,
    "HystCode": 0,
    "StopCount": 4294967295,
    "Binning": 1,
    "Offset": 0,
    "lengthCode": 6,
    "NumBins": 65536,
    "MeasCtrl": 0,
    "StartEdge": 1,
    "StopEdge": 1,
    "TrigOutput": 0,
    "HoldoffTime": 0,
    "HoldTime": 0,
    "MarkerEdges": [
        0,
        0,
        0,
        0
    ],
    "MarkerEna": [
        0,
        0,
        0,
        0
    ],
    "ModsCfg": [
        {
        "Index": 0,
        "ModelCode": 1010,
        "VersionCode": 16843029
        },
        {
        "Index": 1,
        "ModelCode": 1000,
        "VersionCode": 17694997
        }
    ],
    "ChansCfg": [
        {
        "Index": 0,
        "TrigLvl": 100,
        "TrigEdge": 1,
        "DiscrLvl": 100,
        "ZeroXLvl": 0,
        "ChanOffs": 0,
        "ChanEna": 1,
        "DeadTime": 800
        },
        {
        "Index": 1,
        "TrigLvl": -120,
        "TrigEdge": 1,
        "DiscrLvl": -120,
        "ZeroXLvl": 1,
        "ChanOffs": 0,
        "ChanEna": 1,
        "DeadTime": 800
        }
    ],
    "MeasMode": 0,
    "RefSource": 0
    }
    
    """

    measDescription = ()
    """
The measurement description contains special information about the measurement. To update it it is necessary to call :meth:`getMeasDescription`.

Note
----
    The `measDescription` is only valid after a measurement is done or a file device is loaded.

Parameters
    - AcqTime: acquisition 
    - AveSyncRate: if measured with :meth:`getCountRates`
    - AveSyncPeriod: if measured with :meth:`getSyncPeriod`
    - StopReason: why the measurement was stopped
    - StopAfter: the determined time after the measurement was stopped
    - WarningsFlag: currently not supported
    - NumRecs: total number of records

Example
-------
::

    # This is an example of a measurement description
    
    230908_10:29:08.4519796 EXT {
      "AcqTime": 6000000,
      "AveSyncRate": 0.0,
      "AveSyncPeriod": 4294967295.0,
      "StopReason": "Manual",
      "StopAfter": 252036.0,
      "WarningsFlag": 0,
      "NumRecs": 70791781
    }
    
    """

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    

    def __init__(self, systemIni: str | None = None, libType: LibType | None = LibType.MH):
        if systemIni is None:
            systemIni = "\\".join(inspect.getfile(snAPI).split("\\")[:-1])+'\\system.ini'
        self.device = Device(self)
        """This is the object to the device configuration :class:`Device` class"""
        self.filter = Filter(self)
        """This is the object to the hardware filter configuration :class:`Filter` class"""
        self.unfold = Unfold(self)
        """This is the object to :class:`Unfold` class"""
        self.raw = Raw(self)
        """This is the object to :class:`Raw` class"""
        self.histogram = Histogram(self)
        """This is the object to :class:`Histogram`. class"""
        self.timeTrace = TimeTrace(self)
        """This is the object to :class:`TimeTrace`. class"""
        self.correlation = Correlation(self)
        """This is the object to :class:`Correlation`. class"""
        self.manipulators = Manipulators(self)
        """This is the object to :class:`Manipulators`. class"""
        self.initAPI(systemIni, libType)


    def __del__(self,):
        self.exitAPI()


    def logPrint(self,*args, **kwargs):
        """
With logPrint it is possible to print something to the api generated log file.
The generated log file entry will be marked with an "EXT" (External).

Note
----
    See :meth:`initAPI` for information about the logfile destination and configuration!
    
Parameters
----------
    args: It should be used like the normal python print function.

Returns
-------
    none

Example
-------
::

    # Takes the first available device
    sn.logPrint("some text", someVariable)
    

    # This is an example of the log file
    230510_11:33:39.4930338 INF ----------------------------------------------
    230510_11:33:39.4982656 INF INIT
    230510_11:33:39.4983593 INF snAPI 0.1.0.996
    230510_11:33:39.4986360 INF API Init
    230510_11:33:39.4987400 INF Init MHlib
    230510_11:33:39.4988423 DEV MH_GetLibraryVersion: 3.1
    
        """
        summarized_args = " ".join(map(str, args))
        summarized_kwargs = " ".join([f"{key}={value}" for key, value in kwargs.items()])
        self.dll.logExternal.argtypes = [ct.c_char_p]
        if summarized_args and summarized_kwargs:
            self.dll.logExternal(f"{summarized_args} {summarized_kwargs}".encode('utf-8'))
        elif summarized_args:
            self.dll.logExternal(f"{summarized_args}".encode('utf-8'))
        elif summarized_kwargs:
            self.dll.logExternal(f"{summarized_kwargs}".encode('utf-8'))


    def logException(exception_type, exception, eTraceback):
        """
This function is for internal use only and captures unhandled exceptions and add them to the log.

Example
-------
::

    # This is an example of the logged exception
    230911_12:02:53.5338907 ERR Uncaught python exception: IndexError!
    230911_12:02:53.5340906 ERR Text: index 1000000000 is out of bounds for axis 0 with size 300862664
    230911_12:02:53.5349062 ERR   File "e:\Projects\source\Harp\PythonWrapper\Tool_ReadPTU.py", line 25, in <module>
    230911_12:02:53.5350878 ERR     sn.logPrint(f"{channels[1000000000+i]:9} | {times[i]:8}")
    230911_12:02:53.5351972 ERR                    ~~~~~~~~^^^^^^^^^^^^^^

        """
        dll = ct.WinDLL(os.path.abspath(os.path.join(os.path.dirname(__file__), '.\snAPI64.dll')))
        dll.logError.argtypes = [ct.c_char_p]
        dll.logError(f"Uncaught python exception: {exception_type.__name__}!".encode('utf-8'))
        dll.logError(f"Text: {exception}".encode('utf-8'))
        if eTraceback:
            format_exception = traceback.format_tb(eTraceback)
            for line in format_exception:
                for l in repr(line).strip('\'').strip('\\n').replace('\\\\','\\').split("\\n"):
                    dll.logError(l.encode('utf-8'))
    sys.excepthook = logException


    def setLogLevel(self, logLevel: LogLevel, onOff: bool):
        """
This function can set or overwrite the logging flags :class:`snAPI.Constants.LogLevel` for logging. These log levels
will initially set by the `system.ini` defined in :meth:`initAPI`.

Parameters
----------
    logLevel: LogLevel

Returns
-------
    True:  operation successful
    False: operation failed

Example
-------
::

    # This switches the log entries 'Dev' off 
    
    sn.setLogLevel(LogLevel.Device, False)

        """
        return self.dll.setLogLevel(logLevel.value, onOff)


    def initAPI(self, systemIni: typing.Optional[str] = "system.ini", libType: typing.Optional[LibType] = LibType.MH):
        """
This function is called by constructor of the snAPI class. 
It loads a system INI file where it is possible to set flags for logging
or change the data path.

Parameters
----------
    systemIni: str
        | path to the system.ini file (default: "system.ini")
    libType: LibType (default: LibType.MH)

Returns
-------
    True:  operation successful
    False: operation failed

Example
-------
::

    sn.initAPI("system.ini")
    
    # This is an example of an system INI file
    
        [Paths]
        # the path where the device configurations are stored
        Config = C:\Data\PicoQuant\Configs
        
        # the path, where the data (default.ptu) files are stored if no path is specified by `setPTUFilePath`
        # this folder and a subfolder named `log` will automatically generated by `initAPI`
        Data = C:\Data\PicoQuant

        [Log]
        # log to files
        File = 1
        
        # log to std out
        Console = 1
        
        # select witch parts should be logged
        [LogLevel]
        Api = 1
        Config = 0
        Device = 1
        DataFile = 0
        Manipulators = 1
        
        # buffer size in number ofb blocks of 1048576 Bytes
        [Params]
        BufferSize = 128
    
        """
        SBuf = systemIni.encode('utf-8')
        ok = self.dll.initAPI(SBuf, libType.value)
        self.getDeviceConfig()
        return ok


    def exitAPI(self,):
        """
This is function is called in the snAPI destructor. 
It deletes the API instance and frees its memory.
    
Parameters
----------
    none

Returns
-------
    none
    
        """
        self.dll.exitAPI()
    

    def getDeviceIDs(self):
        """
With this function it is possible to read the device identifiers (serial numbers). This `DeviceIDs`
can be used to identify the devices if more than one are connected. If only on device is connected,
:meth:`getDevice` can be called directly to get this device.
    
Parameters
----------
    none

Returns
-------
    True:  operation successful
    False: operation failed
| The list of the device names is stored in deviceNames.
| They will also be shown in the log.

Example
-------
::

    sn.getDeviceIDs()
    
    #Log
    230405_12:11:07.8882089 INF API getDeviceIDs ["1045483","","","","","","",""]
    
        """
        devIDs = (ct.c_char * 8192)()
        found = self.dll.getDeviceIDs(devIDs)
        devIDs = str(devIDs, "utf-8").replace('\x00','')
        if found:
            self.deviceIDs = json.loads(devIDs)
            return True
        else:
            self.logPrint(devIDs)
            return False


    def getDevice(self, *dev):
        """
The `getDevice` function acquires a PicoQuant TCSPC device and sets it as the current device.
From now on all functions will act on this device until another device is acquired.
    
Parameters
----------
    none: 
        takes the first available device
    str:
        identifier of device
            - If the DeviceType is :obj:`.DeviceType.HW` it is the serial number
            - If the DeviceType is :obj:`.DeviceType.File` it is the file name

    int:
        device index [0..7]

Returns
-------
    True:  A device was acquired
    False: No device was acquired

Example
-------
::

    # Takes the first available device
    sn.getDevice()
    sn.getDevice("")
    sn.getDevice(0)

    # Takes the device with the serial number "1045483"
    sn.getDevice("1045483")
    
        """
        self.logPrint("getDevice")
        if not dev: # no device parameter
            name = ""
            SBuf = name.ljust(8, '\0').encode('utf-8')
            if self.dll.getDevice(SBuf):
                return self.getDeviceConfig()
            else:
                self.logPrint(f"{Color.Red}Device not found!")

        elif (len(dev) == 1 and isinstance(dev[0], str)): # name of device
            name = dev[0]
            SBuf = name.ljust(8, '\0').encode('utf-8')
            if len(self.deviceIDs) == 0:
                self.getDeviceIDs()

            if self.dll.getDevice(SBuf): 
                return self.getDeviceConfig()
            else:
                self.logPrint(Color.Red + "Device \"" +name+ "\" not found!")

        elif len(dev) == 1 and isinstance(dev[0], int): # index of device
            if len(self.deviceIDs) == 0:
                self.getDeviceIDs()

            if(dev[0] >= 0 and dev[0] < len(self.deviceIDs)) :
                name = self.deviceIDs[dev[0]]
                if(self.deviceIDs[dev[0]] != ""):
                    SBuf = self.deviceIDs[dev[0]].encode('utf-8')
                    if self.dll.getDevice(SBuf):
                        return self.getDeviceConfig()
                    else:
                        self.logPrint(f"{Color.Red}Error getting Device @ index: {dev[0]} \"{name}\"!") # should not happen
                else:
                    self.logPrint(f"{Color.Red}No device at index: {dev[0]}")
            else:
                self.logPrint(f"{Color.Red}Device index: {dev[0]} out of bounds!")
        else:
            self.logPrint(f"{Color.Red}Invalid device parameter @ getDevice(): {dev[0]}")
            
        return False
    

    def getFileDevice(self, path: str):
        """
This function allows opening a PTU file with a specific path. The file will be handled
like a real device. It is possible to read the ptu header with :obj:`getDeviceConfig`.
The measurement classes can then be used to calculate a histogram, a time trace or perform
other operations on the data.

Parameters
----------
    path: str
        string of the path to the ptu file

Returns
-------
    True:  The file device was successfully acquired
    False: No file device was acquired

Example
-------
::

    sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    
        """
        self.logPrint("getFileDevice", path)
        SBuf = path.encode('utf-8')
        if ok:= self.dll.getFileDevice(SBuf):
            ok = self.getDeviceConfig()
        return ok


    def initDevice(self, measMode: typing.Optional[MeasMode] = MeasMode.T2,
                refSrc: typing.Optional[RefSource] = RefSource.Internal):
        """
This function initializes the device, sets its measurement mode and the reference source.
After that it is possible to do measurements on the device.

Note
----
In case of a file device it is not needed to call initDevice and will be ignored. 

Parameters
----------
    measMode: :class:`snAPI.Constants.MeasMode`
        path of the ptu file (default: MeasMode.T2)
    refSrc: :class:`snAPI.Constants.RefSource`
        (default: RefSource.Internal)

Returns
-------
    True: The device was successfully initialized
    False: Device initialization failed

Example
-------
::

    sn.initDevice(MeasMode.T3)
    
        """
        self.logPrint("initDevice", measMode, refSrc)
        if ok:= self.dll.initDevice(measMode.value, refSrc.value):
            ok = self.getDeviceConfig()
        return ok
    

    def closeDevice(self, allDevices: typing.Optional[bool] = True):
        """

This function closes the current device.
If the current device is a file device it closes the file.



Parameters
----------
    all: bool [True: all opened devices (default) | False: the current device]

Returns
-------
    none
    
    """
        self.dll.closeDevice(allDevices)


    def setPTUFilePath(self, path: str):
        """

This function sets the path to the ptu file, if the measurement supports writing the `Raw` data stream to file.
If no special path is set the file will be written to the data path defined in the INI file
that was called with :meth:`initAPi`. The default file name ist default.ptu.

Parameters
----------
    path: str
        absolute path to the ptu file destination 

Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::

    sn.setPTUFilePath("C:\Data\PicoQuant\default.ptu")
    
    """
        self.logPrint("set PTU file path ", path)
        SBuf = path.encode('utf-8')
        return self.dll.setPTUFilePath(SBuf)
    

    def loadIniConfig(self, path: str):
        """
The device will be initialized with default parameters from intDevice. If is desired to change a
parameter this can be done subsequently with corresponding API call.
Alternatively multiple parameters can be conveniently loaded at once by using :meth:`loadIniConfig`. 
This loads an ini configuration file that contains a [Device]
section for general device parameters, a [Default] section that will set parameters for
all channels and possibly [Channel_N] sections with N starting at 0 for individual channel
settings. Only the parameters which need need to be changed have to be defined in the config file.

Note
----
For detailed information read :ref:`configuration` section!
If you encounter any issues reading a config.ini file enable the config log level in the system.ini. The file location 
is shown in the first log entry: 'loadSettingsIni: e:\path\to\system.ini'.

Parameters
----------
    path: str
        path to the device configuration INI file
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::

    sn.loadIniConfig("C:\Data\PicoQuant\Configs\device.ini")
    
    # This is an example for a device INI file
    [Device]
    HystCode = 0
    SyncDiv = 1
    SyncEdgeTrig = -50,1
    SyncChannelOffset = 0
    SyncChannelEnable = 1
    SyncDeadTime = 00
    StopCount = 4294967295
    Binning = 1
    Offset = 0
    TriggerOutput = 0

    [All_Channels]
    EdgeTrig = -50,1
    ChanOffs = 0
    ChanEna = 1
    DeadTime = 0

    [Channel_0]
    EdgeTrig = 0,1
    ChanOffs = 0

    [Channel_1]
    EdgeTrig = -120,1
    
        """
        SBuf = path.encode('utf-8')
        if ok:= self.dll.loadIniConfig(SBuf):
            ok = self.getDeviceConfig()
        return ok
    

    def setIniConfig(self, text: str):
        """
This command is similar to :meth:`loadIniConfig` but it takes the INI string instead of the path
to the file.

Note
----
    An INI file uses multiple lines to separate the entries. It is therefore necessary
    to use the separator '\\\\n' to be able to pass it as a single-line string.
    For detailed information read :ref:`configuration`!
    If you encounter any issues setting the config enable the config log level in the system.ini. The file location 
    is shown in the first log entry as follows: 'loadSettingsIni: e:\\path\\to\\system.ini'.

Parameters
----------
    text: str
        device configuration INI string
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::

    # sets the Channel 2 Input Edge to -50mV with falling edge
    sn.setIniConfig("[Channel_1]\\nEdgeTrig = -50,0")
    
        """
        self.logPrint("setConfigIni")
        SBuf = text.encode('utf-8')
        if ok:= self.dll.setIniConfig(SBuf):
            ok = self.getDeviceConfig()
        return ok


    def getDeviceConfig(self,):
        """
This command reads the device configuration stored by the API and returns it to
:obj:`snAPI.deviceConfig`.

Note
----
    Normally you have do not have to call this function in order to refresh the :obj:`snAPI.deviceConfig`. 
    It should always be up to date automatically. However, under certain circumstances it might be desired to
    update the device configuration manually. For detailed information read :ref:`configuration`! 

Parameters
----------
    none
    
Returns
-------
    True:  operation successful
    False: operation failed
        
Example
-------
::
    
    # reads the device config from the API 
    
    sn.getDeviceConfig()
    
        """
        conf = (ct.c_char * 65535)()
        ok = self.dll.getDeviceConfig(conf)
        conf = str(conf, "utf-8").replace('\x00','')
        if ok:
            self.deviceConfig = json.loads(conf)
            return True
        else:
            self.logPrint(conf)
            return False


    def getMeasDescription(self):
        """
This reads measurement description that contains special information about the measurement and stores it in :obj:`snAPI.measDescription`.

Note
----
The `measDescription` is only valid after a measurement is done or a file device is loaded.

Parameters
----------
    none
    
Returns
-------
    True:  operation successful
    False: operation failed
        
Example
-------
::
    
    # reads the measurement description an prints it out
    
    sn.getMeasDescription()
    sn.logPrint(json.dumps(sn.measDescription, indent=2))
    
    # prints
    230908_11:06:23.9252150 EXT {
      "AcqTime": 6000000,
      "AveSyncRate": 0.0,
      "AveSyncPeriod": 4294967295.0,
      "StopReason": "Manual",
      "StopAfter": 252036.0,
      "WarningsFlag": 0,
      "NumRecs": 70791781
    }

        """
        conf = (ct.c_char * 65535)()
        ok = self.dll.getMeasDescription(conf)
        conf = str(conf, "utf-8").replace('\x00','')
        if ok:
            self.measDescription = json.loads(conf)
            return True
        else:
            self.parent.logPrint(conf)
            return False

    def _stopMeasure(self):
        """
After a measurement is started it will normally be left running until the defined acquisition
time has elapsed. However, sometimes it may be necessary to stop a measurement manually with
this function.

Note
----
This is the private function that will be called internally if stopMeasure() will be called from a measure class.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.dll.stopMeasure()
        

    def _clearMeasure(self):
        """
Some measurements calculate their results on large sets of historical data. When conditions have changed,
the old data must be deleted to get a fresh view of the new data. Therefore this function was created.
It deletes the internal data without having to restart the measurement.

Note
----
    This is the private function that will be called internally if clearMeasure() will be called from a measure class.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.dll.clearMeasure()


    def getCountRates(self,):
        """
This function retrieves the count rates. This measurement is first performed by the hardware by counting with a
gate time of 100ms. You will therefore obtain new values only after this time has elapsed.
Afterwards the function will return an array of count rates, where the first element is the sync rate, followed
by the count rates of the channels.

Parameters
----------
    none
    
Returns
-------
    countrates: array of int
    
Example
-------
::
    
    cntRs = sn.getCountRates()
    syncrate = cntRs[0]
    chan1rate = cntRs[1]
    
        """
        syncRate =  ct.pointer(ct.c_int(0))
        countRates = ct.ARRAY(ct.c_int, 64)()
        ok = self.dll.getCountRates(syncRate, countRates)
        a = np.array(countRates)
        a = np.resize(a, self.getNumAllChannels())
        a = np.insert(a, 0, syncRate.contents.value)
        return a
    
    
    def getSyncPeriod(self,):
        """
This function only gives meaningful results while a measurement is running and after two sync periods have elapsed.
The return value is `0.0` in all other cases. Resolution is the device base resolution. Accuracy is determined by
single shot jitter and clock stability.

Parameters
----------
    none
    
Returns
-------
    syncPeriod: float
    
Example
-------
::
    
    syncPeriod = sn.getSyncPeriod()
    
        """
        syncPeriod =  ct.c_double(0)
        self.dll.getSyncPeriod.argtypes = [ct.POINTER(ct.c_double)]
        ok = self.dll.getSyncPeriod(ct.pointer(syncPeriod))
        return syncPeriod.value


    def getNumAllChannels(self,):
        """
This functions returns the number of available channels from the active device has plus the number of channels for
the :class:`Manipulators` and one for the sync channel. It describes the number of channels a measurement returns
and is used for memory allocation.

Parameters
----------
    none
    
Returns
-------
    numAllChannels: number of all channels
    
Example
-------
::
    
    numChans = sn.getNumAllChannels();
    
        """
        return self.dll.getNumAllChans()



class Device():
    """
This is the low level device configuration class. It has to be noted that the functions and parameters you can use
depend on the connected device. Therefore, the correct library must be chosen when creating the snAPI object. 

    """
    

    def __init__(self, parent):
        self.parent = parent


    def setSyncDiv(self, syncDiv: typing.Optional[int] = 1):
        """
    Supported devices: [MH150/160 | HH400 | PH330]
    
The sync divider must be used in order to keep the effective sync rate at values < 78 MHz.
It should only be used with sync sources of stable period. Using a larger divider
than strictly necessary may result in an slightly larger timing jitter.
    
Parameters
----------
    syncDiv: int
        | sync rate divider 
        | 1(default)
        | MH150/160, HH400  [1, 2, 4, 8, 16]
        | TH260 | PH330: [1, 2, 4, 8]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    sn.device.setSyncDiv(1)
    
        """
        if ok:= self.parent.dll.setSyncDiv(syncDiv):
            self.parent.deviceConfig["SyncDivider"] = syncDiv
        return ok


    def setSyncTrigMode(self, syncTrigMode: typing.Optional[TrigMode] = TrigMode.Edge):
        """
    Supported devices: [PH330]
    
The function sets the trigger mode of the sync channel.
For the trigger mode of the input channels use :meth:`setInputTrigMode`.
    
Parameters
----------
    syncTrigMode: TriggerMode
        | (default: TriggerMode.Edge)
        | [TriggerMode.Edge | TriggerMode.CFD]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the sync trigger mode to edge trigger
    sn.device.setSyncTrigMode(TriggerMode.Edge)
    
        """
        if ok:= self.parent.dll.setSyncTrigMode(syncTrigMode.value):
            if syncTrigMode == TrigMode.Edge:
                self.parent.deviceConfig["SyncTrigMode"] = "Edge"
            elif syncTrigMode == TrigMode.CFD:
                self.parent.deviceConfig["SyncTrigMode"] = "CFD"
        return ok


    def setSyncEdgeTrig(self, syncTrigLvl: typing.Optional[int] = -50, syncTrigEdge: typing.Optional[int] = 1):
        """
    Supported devices: [MH150/160 | TH260N | PH330]
    
This function sets the trigger level and trigger slope of the sync channel.
The hardware uses a 10 bit DAC that can resolve the level value only
in steps of about 2.34 mV.
To set the input edge trigger of the input channels use :meth:`setInputEdgeTrig`.
    
Parameters
----------
    syncTrigLvl: int
        | trigger level [mV] 
        | (default:-50mV)
        | MH150/160, TH260N : [-1200..1200]
        | PH330: [-1500..1500]
    syncTrigEdge: int
        | trigger edge 
        | 0: falling
        | 1: rising (default)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the sync trigger to -50mV on rising edge
    sn.device.setSyncEdgeTrig(-50,1)
    
        """
        if ok:= self.parent.dll.setSyncEdgeTrig(syncTrigLvl, syncTrigEdge):
            self.parent.deviceConfig["SyncTrigLvl"] = syncTrigLvl
            self.parent.deviceConfig["SyncTrigEdge"] = syncTrigEdge
        return ok


    def setSyncCFD(self, syncDiscrLvl: typing.Optional[int] = 50, syncZeroXLvL: typing.Optional[int] = 20):
        """
    Supported devices: [HH400 | TH260P | PH330]
    
This function configures the CFD (Constant Fraction Discriminator) of the sync channel.
For the input CFD of the input channels use :meth:`setInputCFD`.
    
Parameters
----------
    syncDiscrLvl: int
        | level [mV] (default:50mV)
        | HH400: [0..1000]
        | TH260P: [-1200..0]
        | PH330: [-1500..0]
    syncZeroXLvL: int
        | trigger edge 
        | HH400: [0..40]
        | TH260P: [-40..0]
        | PH330: [-100..0]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the sync CFD to a discriminator level of 100mV and the zero cross level to 30mV
    sn.device.setSyncCFD(100, 30)
    
        """
        if ok:= self.parent.dll.setSyncCFD(syncDiscrLvl, syncZeroXLvL):
            self.parent.deviceConfig["SyncZeroXLvL"] = syncZeroXLvL
            self.parent.deviceConfig["SyncDiscrLvl"] = syncDiscrLvl
        return ok
    
    
    def setSyncChannelOffset(self, syncChannelOffset: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330]
    
This sets a virtual delay time to the sync pulse. This is equivalent to changing
the cable length on the sync input. The current resolution is the device's base resolution.
    
Parameters
----------
    syncChannelOffset: int
        | sync timing offset [ps]
        | (0: default)
        | MH150/160, HH400, TH260, PH330: [-99999..99999]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the sync channel offset to 10ps
    sn.device.setSyncChannelOffset(10)
    
        """
        if ok := self.parent.dll.setSyncChannelOffset(syncChannelOffset):
            self.parent.deviceConfig["SyncChannelOffset"] = syncChannelOffset
        return ok


    def setSyncChannelEnable(self, syncChannelEnable: typing.Optional[int] = 1):
        """
    Supported devices: [MH150/160 | PH330]
    
This enables or disables the sync channel. This is only useful in :obj:`.MeasMode.T2`.
Histogram and :obj:`.MeasMode.T3` always need an active sync signal.
To enable or disable the other channels use :meth:`setInputChannelEnable`.

Parameters
----------
    syncChannelEnable: int
        | 0: disabled 
        | 1: enabled (default)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # enables the sync channel
    sn.device.setSyncChannelEnable(1)
    
        """
        if ok:= self.parent.dll.setSyncChannelEnable(syncChannelEnable):
            self.parent.deviceConfig["SyncChannelEnable"] = syncChannelEnable
        return ok


    def setSyncDeadTime(self, syncDeadTime: typing.Optional[int] = 800):
        """
    Supported devices: [MH150/160 | PH330] 
    
This call is primarily intended for the suppression of afterpulsing artifacts caused by some detectors.
An extended dead-time does not prevent the TDC from measuring the next event and hence enter a
new dead-time. It only suppresses events occurring within the extended dead-time from further processing.
For the configuration of the dead time of the other channels use :meth:`setInputDeadTime`. 

Note
----
    Setting an extended dead-time will also affect the count rate meter readings.
    The extended deadtime will be rounded to the nearest multiple of the device's base resolution.

Parameters
----------
    syncDeadTime:
        | extended dead-time [ps]
        | 800 (default)
        | MH150/160, PH330: [801..160000], <=800: disabled
        | TH206P only [24000, 44000, 66000, 88000, 112000, 135000, 160000 or 180000]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the sync dead time to 1000ps
    sn.device.setSyncDeadTime(1000)
    
        """
        if ok := self.parent.dll.setSyncDeadTime(syncDeadTime):
            self.parent.deviceConfig["SyncDeadTime"] = syncDeadTime
        return ok
    

    def setInputHysteresis(self, hystCode: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | PH330] 
    
This function is intended for the suppression of noise or pulse shape artifacts caused by some detectors by setting
a higher input hysteresis.

Note
----
    This setting affects sync and all channels simultaneously.

Parameters
----------
    hystCode: int
        | 0: 3mV approx. (default) 
        | 1: 35mV approx.
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the input hysteresis to approximately 3mV
    sn.device.setInputHysteresis(0)
    
        """
        if ok := self.parent.dll.setInputHysteresis(hystCode):
            self.parent.deviceConfig["HystCode"] = hystCode
        return ok


    def setTimingMode(self, timingMode: typing.Optional[int] = 0):
        """
    Supported devices: [TH260P] 
    
This will change the base resolution for very long measurements.

Note
----
    This setting is only available for TimeHarp 260 P.

Parameters
----------
    hystCode: int
        | 0: Hires (25ps) (default) 
        | 1: Lores (2.5 ns, a.k.a. “Long range”) 
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the input hysteresis to approximately 3mV
    sn.device.setInputHysteresis(0)
    
        """
        if ok := self.parent.dll.setTimingMode(timingMode):
            self.parent.deviceConfig["TimingMode"] = timingMode
        return ok


    def setStopOverflow(self, stopCount: typing.Optional[int] = 4294967295):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This setting causes the measurement to stop if any channel reaches the maximum set by `stopCount`.
The maximum value that could be count is 4294967295, which is the equivalent to the 32 bit storage.

Note
----
    This is for :class:`Histogram` measurements only!

Parameters
----------
    stopCount:
        | 0: off
        | 1..4294967295 (default)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the measurement to stop at 1000000000 counts 
    sn.device.setStopOverflow(1000000000)
    
        """
        if ok := self.parent.dll.setStopOverflow(stopCount):
            self.parent.deviceConfig["StopCount"] = stopCount
        return ok


    def setBinning(self, binning: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This sets the with of the time bins.
Binning only applies in Histogram and :obj:`.MeasMode.T3`. 
The binning can be set in doubling multiples of the base resolution.
    
Parameters
----------
    binning: 
        | (default: 0 - 1*br)
        | MH150/160, PH330: [1: 2*br, 2: 4*br, .., 24: 16777216*br]
        | HH400: [1: 2*br, 2: 4*br, .., 26: 67108864*br]
        | TH260: [1: 2*br, 2: 4*br, .., 22: 4194304*br]
        | (br stands for base resolution)
    
Returns
-------
    True: operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the binning to 1 
    sn.device.setBinning(0)
    
        """
        if ok := self.parent.dll.setBinning(binning):
            self.parent.deviceConfig["Binning"] = binning
        return ok
    

    def setOffset(self, offset: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This offset only applies in Histogram and :obj:`.MeasMode.T3`. It affects only the difference between start
and stop before it is put into the T3 record or is used when allocating the corresponding histogram bin.
It is intended for situations where the range of the histogram is not long enough to look at “late” data.
By means of the offset the viewed time window. This is not the same as changing or compensating cable delays.
If the latter is desired please use :meth:`setSyncChannelOffset` and/or :meth:`setInputChannelOffset`.
    
Parameters
----------
    offset:
        | histogram time offset [ns]
        | (0: default)
        | MH150/160, TH260, PH330: [0..100000000]
        | HH400: [0..500000]
    
Returns
-------
    True: operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the offset to 0ns 
    sn.device.setOffset(0)
    
        """
        if ok:= self.parent.dll.setOffset(offset):
            self.parent.deviceConfig["Offset"] = offset
        return ok


    def setHistoLength(self, lengthCode: typing.Optional[int] = 6):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This function sets the number of bins of the collected histograms in :obj:`.MeasMode.Histogram`.
The maximum histogram length obtained is 65536 which is also the default after initialization.
In :obj:`.MeasMode.T2` the number of bins is fixed 65536 and in :obj:`.MeasMode.T3` it is 32768. 

Parameters
----------
    lengthCode: int
        | number of bins that can be calculated by :math:`2^{(10 + \\mathrm{lengthCode})}`
        | MH150/160: [0..6] (default: 65536 bins = lengthCode 6)
        | HH400, TH260, PH330: [0..5] (default: 32768 bins = lengthCode 5)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the number of bins to 10000
    sn.device.setHistoLength(10000)
    
        """
        if ok:= self.parent.dll.setHistoLength(lengthCode):
            self.parent.deviceConfig["NumBins"] = pow(2, 10 + lengthCode)
            self.parent.deviceConfig["LengthCode"] = lengthCode
        return ok


    def setMeasControl(self, measCtrl: typing.Optional[MeasControl] = MeasControl.SingleShotCTC, startEdge: typing.Optional[int] = 0, stopEdge: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This sets the measurement control mode and for other than the default it must be called before starting a measurement.
The default is 0: CTC controlled acquisition time. The modes 1..5 allow hardware triggered measurements
through TTL signals at the control port or through White Rabbit. 

Note
----
    White Rabbit modes are not fully supported at the moment. 

Parameters
----------
    measCtrl: MeasControl
    startEdge: int
        | 0: falling (default)
        | 1: rising
    stopEdge:
        | 0: falling (default)
        | 1: rising
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the measurement control mode to ::obj:`SingleShotCTC`
    sn.device.setMeasControl(MeasControl.SingleShotCTC, 0, 0)
    
        """
        if ok:= self.parent.dll.setMeasControl(measCtrl, startEdge, stopEdge):
            self.parent.deviceConfig["MeasCtrl"] = measCtrl
            self.parent.deviceConfig["StartEdge"] = startEdge
            self.parent.deviceConfig["StopEdge"] = stopEdge
        return ok


    def setTriggerOutput(self, trigOutput: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | TH260 | PH330] 
    
This can be used to set the period of the programmable trigger output. A period zero (0) switches it off.

Warning
-------
    Respect laser safety when using this feature to trigger a laser.

Parameters
----------
    trigOutput: int [units of 100ns]
    | 0: switch output off (default)
    | MH150/160, TH260, PH330: [0..16777215]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the programmable trigger output to 10 * 100ns = 1µs
    sn.device.setTriggerOutput(10)
    
        """
        if ok:= self.parent.dll.setTriggerOutput(trigOutput):
            self.parent.deviceConfig["TriggerOutput"] = trigOutput
        return ok
    

    def setMarkerEdges(self, edge1: typing.Optional[int] = 0, edge2: typing.Optional[int] = 0, edge3: typing.Optional[int] = 0, edge4: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This can be used to change the active edge on which the external TTL signals are connected to the marker inputs trigger.

Note
----
    Only meaningful in :obj:`.MeasMode.T2` and :obj:`.MeasMode.T3`.

Parameters
----------
    edge1: int
    edge2: int
    edge3: int
    edge4: int
        | 0: falling (default)
        | 1: rising
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the active edge of marker signal 1 to rising, and the others to falling
    sn.device.setMarkerEdges(1,0,0,0)
    
        """
        if ok:= self.parent.dll.setMarkerEdges(edge1, edge2, edge3, edge4):
            self.parent.deviceConfig["MarkerEdges"] = [edge1, edge2, edge3, edge4]
        return ok
    

    def setMarkerEnable(self, ena1: typing.Optional[int] = 0, ena2: typing.Optional[int] = 0, ena3: typing.Optional[int] = 0, ena4: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This can be used to enable or disable the external TTL marker inputs.

Note
----
    Only meaningful in :obj:`.MeasMode.T2` and :obj:`.MeasMode.T3`.

Parameters
----------
    ena1: int
    ena2: int
    ena3: int
    ena4: int
        | 0: disabled (default)
        | 1: enabled
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # enables the first external TTL marker input and disables the other three
    sn.device.setMarkerEnable(1,0,0,0)
    
        """
        if ok:= self.parent.dll.setMarkerEnable(ena1, ena2, ena3, ena4):
            self.parent.deviceConfig["MarkerEna"] = [ena1, ena2, ena3, ena4]
        return ok
    

    def setMarkerHoldoffTime(self, holdofftime: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This setting is normally not required but it can be used to deal with glitches
on the marker lines. Using this function causes the suppression of markers following
a previous marker within the hold-off time.

Note
----
    Only meaningful in :obj:`.MeasMode.T2` and :obj:`.MeasMode.T3`.
    The actual hold-off time is only approximated to about ±20ns.

Parameters
----------
    holdofftime: int [ns]
        | (0: default)
        | MH150/160, PH330: [0.. 25500]
        | HH400: [0.. 524296]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the marker hold off time to 100ns
    sn.device.setMarkerHoldoffTime(100)
    
        """
        if ok:= self.parent.dll.setMarkerHoldoffTime(holdofftime):
            self.parent.deviceConfig["Holdofftime"] = holdofftime
        return ok
    

    def setOflCompression(self, holdtime: typing.Optional[int] = 2):
        """
    Supported devices: [MH150/160 | PH330] 
    
This setting is normally not required but it can be useful when data rates are very low and the overflows is high compared to the number of
photons. If used the hardware will count overflows and only transfer them to the FiFo when the holdtime has elapsed. The default
value is 2 ms. If you are implementing a real-time preview and data rates are very low you may observe “stutter” when the
holdtime is too large because then there is nothing no readout of the FiFo for these long times. This is
aggravated by the fact that the FiFo has a transfer granularity of 16 records. Supposing a data stream without any
regular event records (i.e. only overflows) this means that effectively there will be a transfer only every 16*holdtime ms.
Whenever there is a true event record arriving (photons or markers) the previously accumulated overflows will instantly
be transferred. This is the case even with dark counts from the detector. Hence, the stutter will rarely occur. In any case you can
switch overflow compression off by setting the holdtime to zero (0).

Note
----
    Only meaningful in :obj:`.MeasMode.T2` and :obj:`.MeasMode.T3`.

Parameters
----------
    holdtime: int
        0..255ms (default: 2ms)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the overflow compression to 10ns
    sn.device.setOflCompression(10)
    
        """
        if ok:= self.parent.dll.setOflCompression(holdtime):
            self.parent.deviceConfig["Holdtime"] = holdtime
        return ok


    def setInputTrigMode(self, channel: typing.Optional[int] = -1, trigMode: typing.Optional[TrigMode] = TrigMode.Edge):
        """
    Supported devices: [PH330] 
    
This sets the input trigger mode.
For the input edge trigger of the sync channel use :meth:`setSyncTrigMode`.

Note
----
    The maximum input channel index must be less than deviceConfig["numChans"].

Parameters
----------
    channel: int
        | 0 .. ["numChans"]-1
        | -1: all channels (default)
    trigMode:
        | (default: TriggerMode.Edge)
        | [TriggerMode.Edge | TriggerMode.CFD]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the input mode of channel 1 to trigger edge
    sn.device.setInputTrigMode(0, TriggerMode.Edge)
    
        """
        if ok:= self.parent.dll.setInputTrigMode(channel, trigMode.value):
            trigModeS = ""
            if trigMode == TrigMode.CFD:
                trigModeS = "CFD"
            elif trigMode == TrigMode.Edge:
                trigModeS = "Edge"
                
            if channel == -1:
                for chan in range(self.parent.deviceConfig["NumChans"]):
                    self.parent.deviceConfig["ChansCfg"][chan]["TrigMode"] = trigModeS
            else:
                self.parent.deviceConfig["ChansCfg"][channel]["TrigMode"] = trigModeS
                
        return ok


    def setInputEdgeTrig(self, channel: typing.Optional[int] = -1, trigLvl: typing.Optional[int] = -50, trigEdge: typing.Optional[int] = 1):
        """
    Supported devices: [MH150/160 | TH260 | PH330] 
    
This command sets the input trigger. Both the trigger level and the trigger slope have to be configured.
For the input edge trigger of the sync channel use :meth:`setSyncEdgeTrig`.

Note
----
    The maximum input channel index must be less than deviceConfig["numChans"].
    The hardware uses a 10 bit DAC that can resolve the level value only in steps of about 2.34 mV.

Parameters
----------
    channel: int
        | 0 .. [numChannels]-1
        | -1: all channels (default)
    trigLvl: int [mV]
        | (default: -50mV)
        | MH150/160, TH260: [-1200..1200]
    trigEdge: int
        | 0: falling
        | 1: rising (default)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the input of channel 1 to a trigger edge of -100mV on a falling edge
    sn.device.setInputEdgeTrig(0, -100, 0)
    
        """
        if ok:= self.parent.dll.setInputEdgeTrig(channel, trigLvl, trigEdge):
            if channel == -1:
                for chan in range(self.parent.deviceConfig["NumChans"]):
                    self.parent.deviceConfig["ChansCfg"][chan]["TrigLvl"] = trigLvl
                    self.parent.deviceConfig["ChansCfg"][chan]["TrigEdge"] = trigEdge
            else:
                self.parent.deviceConfig["ChansCfg"][channel]["TrigLvl"] = trigLvl
                self.parent.deviceConfig["ChansCfg"][channel]["TrigEdge"] = trigEdge
                
        return ok


    def setInputCFD(self, channel: typing.Optional[int] = -1, discrLvl: typing.Optional[int] = 50, zeroXLvl: typing.Optional[int] = 20):
        """
    Supported devices: [HH400 | TH260P | PH330] 
    
This function can be used to configure the CFD (Constant Fraction Discriminator) of the sync channel.
For the input CFD of the input channels use :meth:`setSyncCFD`.
    
Parameters
----------
    channel: int
        | 0 .. [numChannels]-1
        | -1: all channels (default)
    discrLvlSync: int
        | level [mV] (default:50mV)
        | HH400: [0..1000]
        | TH260P: [-1200..0]
    syncZeroXLvL: int
        | zero cross level [mV]
        | HH400: [0..40]
        | TH260P: [-40..0]
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the input of channel 1 to a discriminator level of 100mV on zero cross level of 30mV
    sn.device.setInputEdgeTrig(0, 100, 30)
    
        """
        if ok:= self.parent.dll.setInputCFD(channel, discrLvl, zeroXLvl):
            if channel == -1:
                for chan in range(self.parent.deviceConfig["NumChans"]):
                    self.parent.deviceConfig["ChansCfg"][chan]["DiscrLvl"] = discrLvl
                    self.parent.deviceConfig["ChansCfg"][chan]["ZeroXLvl"] = zeroXLvl
            else:
                self.parent.deviceConfig["ChansCfg"][channel]["DiscrLvl"] = discrLvl
                self.parent.deviceConfig["ChansCfg"][channel]["ZeroXLvl"] = zeroXLvl
                
        return ok
    

    def setInputChannelOffset(self, channel: typing.Optional[int] = -1, chanOffs: typing.Optional[int] = 0):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This operation equivalent to changing the cable length (delay) on the chosen input. The offset resolution is equal to the device base resolution.
For the input channel offset of the sync channel use :meth:`setSyncChannelOffset`.

Note
----
    The maximum input channel index must be less than deviceConfig["numChans"].

Parameters
----------
    channel: int
        | 0 .. [numChannels]-1
        | -1: all channels (default)
    chanOffs: int channel timing offset [ps]
        | (default: 0)
        | MH150/160, HH400, TH260, PH330 [-99999..99999] 
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the offset of the input of channel 1 to 100ps
    sn.device.setInputChannelOffset(0, 100)
    
        """
        if ok:= self.parent.dll.setInputChannelOffset(channel, chanOffs):
            if channel == -1:
                for chan in range(self.parent.deviceConfig["NumChans"]):
                    self.parent.deviceConfig["ChansCfg"][chan]["ChanOffs"] = chanOffs
            else:
                self.parent.deviceConfig["ChansCfg"][channel]["ChanOffs"] = chanOffs
        return ok


    def setInputChannelEnable(self, channel: typing.Optional[int] = -1, chanEna: typing.Optional[int] = 1):
        """
    Supported devices: [MH150/160 | HH400 | TH260 | PH330] 
    
This function enables or disables the input channels.
To enable the sync channel use :meth:`setSyncChannelEnable`.

Note
----
    The maximum input channel index must be less than deviceConfig["numChans"].

Parameters
----------
    channel: int
        0 .. [numChannels]-1
        -1: all channels (default)
    chanEna: 
        | 1: enable channel (default)
        | 0: disable channel
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # disables the input channel 4
    sn.device.setInputEdgeTrig(3, 0)
    
        """
        if ok:= self.parent.dll.setInputChannelEnable(channel, chanEna):
            if channel == -1:
                for chan in range(self.parent.deviceConfig["NumChans"]):
                    self.parent.deviceConfig["ChansCfg"][chan]["ChanEna"] = chanEna
            else:
                self.parent.deviceConfig["ChansCfg"][channel]["ChanEna"] = chanEna
        return ok


    def setInputDeadTime(self, channel: typing.Optional[int] = -1, deadTime: typing.Optional[int] = 800):
        """
    Supported devices: [MH150/160 | TH260 | PH330] 
    
This call is primarily intended for the suppression of afterpulsing artifacts of some detectors.
An extended dead-time does not prevent the TDC from measuring the next event and hence enter a
new dead-time. It only suppresses events occurring within the extended dead-time from further processing.
For the dead time of the sync channel use :meth:`setSyncDeadTime`. 

Note
----
    When an extended dead-time is set then it will also affect the count rate meter readings.
    The the extended deadtime will rounded to the nearest step of the device base resolution.

Parameters
----------
    channel: int
        0 .. [numChannels]-1
        -1: all channels (default)
    deadTime:
        | extended dead-time [ps]
        | MH150/160, TH260, PH330 [800..160000] (default: 800) (<=800: disabled)
        | TH260 [24000 | 44000 | 66000 | 88000 | 112000 | 135000 | 160000 | 180000] (default: 24000)
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # sets the sync dead time too 1000ps
    sn.device.setInputDeadTime(1000)
    
        """
        if ok:= self.parent.dll.setInputDeadTime(channel, deadTime):
            if channel == -1:
                for chan in range(self.parent.deviceConfig["NumChans"]):
                    self.parent.deviceConfig["ChansCfg"][chan]["DeadTime"] = deadTime
            else:
                self.parent.deviceConfig["ChansCfg"][channel]["DeadTime"] = deadTime
        return ok



class Filter():
    """
Filtering the TTTR data stream before transfer helps to reduce the USB bus load in TTTR mode by eliminating photon events
that carry no information of interest as typically found in many coincidence correlation experiments. 
There are two types of event filters. The Row Filters are implemented in the local FPGA processing a row of
input channels. Each Row Filter can act only on the input channels within its own row and never on the sync
channel. The Main Filter is implemented in the main FPGA processing the aggregated events arriving from
the row FPGAs. The Main Filter can therefore act on all channels of the device including the sync
channel. Since the Row Filters and Main Filter form a daisychain, the overall filtering result depends on their
combined action. Both filters are by default disabled upon device initialization and can be independently enabled
when needed.

Both filters follow the same concept but with independently programmable parameters. The parameter
`timeRange` determines the time window the filter is acting on. The parameter `matchCount` specifies how
many other events must fall into the chosen time window for the filter condition to act on the event at hand.
The parameter `inverse` inverts the filter action, i.e. when the filter would regularly have eliminated an event
it will then keep it instead and vice versa. For the typical case, let it be not inverted. Then, if `matchCount` is 1 we will
obtain a simple 'singles filter'. This is the most straight forward and most useful filter in typical quantum optics
experiments. It will suppress all events that do not have at least one coincident event within the chosen time
range. This can be in the same or any other channel.

In addition to the filter parameters explained so far it is possible to mark individual channels for use. Used
channels will take part in the filtering process. Unused channels will be suppressed altogether. Furthermore, it
is possible to indicate if a channel is to be passed through the filter unconditionally, whether it is marked as
`use` or not. The events on a channel that is marked neither as `use` nor as `pass` will not pass the filter, provided
the filter is enabled.

Note
----
    As outlined earlier, the Row Filters and Main Filter form a daisychain and the overall filtering result depends
    on their combined action. It is usually sufficient and easier to use the Main Filter alone. The only reasons for
    using the Row Filter(s) are early data reduction, so as to not overload the Main Filter, and the possible need
    for more complex filters, e.g. with different time ranges.
    
    """
    

    def __init__(self, parent):
        self.parent = parent    


    def setRowParams(self, row: int, timeRange: int, matchCount: int, inverse: bool, useChans:typing.List[int], passChans:typing.List[int]):
        """
    Supported devices: [MH150/160] 
    
This sets the parameters for one Row Filter implemented in the local FPGA processing that row of input channels. Each
Row Filter can act only on the input channels within its own row and never on the sync channel. The parameter `timeRange` determines
the time window the filter is acting on. The parameter `matchCount` specifies how many other events must fall into the
chosen time window for the filter condition to act on the event at hand. The parameter `inverse` inverts the filter action, i.e.
when the filter would regularly have eliminated an event it will then keep it instead and vice versa. For the typical case, let it be not
inverted. Then, if `matchCount` is 1 we will obtain a simple 'singles filter'. This is the most straight forward and most useful filter
in typical quantum optics experiments. It will suppress all events that do not have at least one coincident event within the
chosen time range, be this in the same or any other channel marked as 'use' in this row. The list `passChans` is used
to indicate if a channel is to be passed through the filter unconditionally, whether it is marked as 'use' or not. The events on a
channel that is marked neither as 'use' nor as 'pass' will not pass the filter, provided the filter is enabled. The parameter
settings are irrelevant as long as the filter is not enabled. The output from the Row Filters is fed to the Main Filter. The overall
filtering result depends on their combined action. Only the Main Filter can act on all channels of the PicoQuant TCSPC device including
the sync channel. 

Note
----
    It is usually sufficient and easier to use the Main Filter alone. The only reasons for using the Row Filter(s)
    are early data reduction, so as to not overload the Main Filter, and the possible need for more complex filters, e.g. with
    different time ranges.
    
Parameters
----------
    row: int [0..8]
        | index of the row of input channels, counts bottom to top
    timeRange: int [0..160000ps]
        | time distance in ps to other events to meet filter condition
    matchCount: int [1..6]
        | number of other events needed to meet filter condition
    inverse: bool
        | set regular or inverse filter logic
        | false: regular, true: inverse
    useChans: List[int] [0..7]
        | List of channels to use
    passChans: List[int] [0..7]
        | List of channels to pass
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # set the row filter to row 0, time range 1ns with singles filter between channel 0 and 1
    sn.filter.setRowParams(0, 1000, 1, False, [0,1], [])
    
        """
        
        uc = 0
        for i in useChans:
            uc |= pow(2, i)
            
        pc = 0
        for i in passChans:
            pc |= pow(2, i)

        return self.parent.dll.setRowEventFilter(row, timeRange, matchCount, inverse, uc, pc)


    def enableRow(self, row: int, enable: bool):
        """
    Supported devices: [MH150/160] 
    
When the filter is disabled all events will pass. This is the default after initialization. When it is enabled, events may be
filtered out according to the parameters set with :meth:`setRowParams`.
    
Parameters
----------
    row: int [0..8]
        | index of the row of input channels, counts bottom to top
    enable: bool
        | desired enable state of the filter
    
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # enable the row filter on row 0
    sn.filter.enableRow(0, True)
    
        """
        return self.parent.dll.enableRowEventFilter(row, enable)


    def setMainParams(self, timeRange: int, matchCount: int, inverse: bool):
        """
    Supported devices: [MH150/160 | PH330] 
    
This sets the parameters for the Main Filter implemented in the main FPGA processing the aggregated events arriving from
the row FPGAs. The Main Filter can therefore act on all channels of the device including the sync channel. The
value `timeRange` determines the time window the filter is acting on. The parameter `matchCount` specifies how many other
events must fall into the chosen time window for the filter condition to act on the event at hand. The parameter `inverse` inverts
the filter action, i.e. when the filter would regularly have eliminated an event it will then keep it instead and vice versa. For the
typical case, let it be not inverted. Then, if `matchCount` is 1 we obtain a simple 'singles filter'. This is the most straight forward
and most useful filter in typical quantum optics experiments. It will suppress all events that do not have at least one coincident
event within the chosen time range, be this in the same or any other channel. In order to mark individual channel as 'use'
and/or 'pass' please use meth:`setMainChannels`. The parameter settings are irrelevant if the filter is not
enabled. Note that the Main Filter only receives events that passes the Row Filters (if they are enabled). The overall filtering
result depend on the combined action of both filters.

Note
----
    It is usually sufficient and easier to use the Main Filter alone. The only reasons for using the Row Filters are early data reduction,
    to prevent overloading of the Main Filter, and for possible need for more complex filters, e.g. with different time ranges are needed.
    
Parameters
----------
    timeRange: int [0..160000ps]
        | time distance in ps to other events to meet filter condition
    matchCount: int [1..6]
        | number of other events needed to meet filter condition
    inverse: bool
        | set regular or inverse filter logic
        | false: regular, true: inverse
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # set the main filter to time range 1ns with singles filter
    sn.filter.setMainParams(0, 1000, 1, False
    
        """
        return self.parent.dll.setMainEventFilterParams(timeRange, matchCount, inverse)


    def setMainChannels(self, row: int, useChans:typing.List[int], passChans:typing.List[int]):
        """
    Supported devices: [MH150/160 | PH330] 
    
This selects the Main Filter channels for one row of input channels. Doing this row by row is to address the fact that the various
device models have different numbers of rows. The list `useChans` is used to to indicate if a channel is to be
used by the filter. The list `passChans` is used to to indicate if a channel is to be passed through the filter unconditionally,
whether it is marked as 'use' or not. The events on a channel that is marked neither as 'use' nor as 'pass' will not
pass the filter, provided the filter is enabled. The channel settings are irrelevant as long as the filter is not enabled.
The Main Filter receives its input from the Row Filters. If the Row Filters are enabled, the overall filtering result
therefore depends on the combined action of both filters. Only the Main Filter can act on all channels of the PicoQuant TCSPC device
including the sync channel.

Note
----
The settings for the sync channel are only meaningful in :obj:`.MeasMode.T2` and will be ignored in :obj:`.MeasMode.T3`.

Note
----
    It is usually sufficient and easier to use the `Main Filter` alone. The only reasons for using the Row Filters are early data reduction,
    to prevent overloading of the Main Filter, and if for more complex filters, e.g. with different time ranges are needed.
    
Parameters
----------
    row: int [0..8]
        | index of the row of input channels, counts bottom to top
    useChans: List[int] [0..7]
        | List of channels to use
    passChans: List[int] [0..7]
        | List of channels to pass
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # set the main filter on row 0 to filter between channel 0 and 1, pass the sync channel
    sn.filter.setRowParams(0, [0,1], [8])
    
        """
        uc = 0
        for i in useChans:
            uc |= pow(2, i)
            
        pc = 0
        for i in passChans:
            pc |= pow(2, i)
        
        return self.parent.dll.setMainEventFilterChannels(row, uc, pc)


    def enableMain(self, enable: typing.Optional[bool] = True):
        """
    Supported devices: [MH150/160 | PH330] 
    
When the filter is disabled all events will pass. This is the default after initialization. When it is enabled, events may be
filtered out according to the parameters set with :meth:`setMainParams` and :meth:`setMainParams`.

Note
----
    The Main Filter only receives events that pass the Row Filters (if they are enabled). The overall filtering result
    therefore depends on the combined action of both filters. It is usually sufficient and easier to use the Main Filter alone. The
    only reasons for using the Row Filters are early data reduction, to prevent overloading of the Main Filter, and if for
    more complex filters, e.g. with different time ranges are needed.

Parameters
----------
    enable: bool
        | desired enable state of the filter
    
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # enables the main filter
    sn.filter.enableMain(True)
    
        """
        return self.parent.dll.enableMainEventFilter(enable)
        #     self.parent.deviceConfig["SyncDivider"] = syncDiv
        # return ok
    
    
    def setTestMode(self, testMode: typing.Optional[bool] = True):
        """
    Supported devices: [MH150/160 | PH330] 
    
One important purpose of the event filters is to reduce USB load. When the input data rates are higher than the USB bandwith,
there will  be a FiFo overrun at some point. Under such conditions can be difficult to empirically optimize the filter settings.
Activating the filter test mode disables all data transfers into the FiFo so that a test measurement can be run without being interrupted
by a FiFo overrun. The library routines :meth:`getRowRates` and :meth:`getMainRates` can then be used to monitor the count rates
after the Row Filter and after the Main Filter. When the filtering effect is satisfactory the test mode can be switched off again
to perform the regular measurement.
    
Parameters
----------
    testMode: bool
        | desired mode of the filter
        | 0: regular operation
        | 1: test mode
    
Returns
-------
    True:  operation successful
    False: operation failed
    
Example
-------
::
    
    # enables the filter test mode
    sn.filter.setTestMode(True)
    
        """
        return self.parent.dll.setFilterTestMode(testMode)
        #     self.parent.deviceConfig["SyncDivider"] = syncDiv
        # return ok
    
    
    def getRowRates(self):
        """
    Supported devices: [MH150/160 | PH330] 
    
This call retrieves the count rates after the Row Filter before entering the FiFO. A measurement must be running to obtain
valid results. Allow at least 100 ms to get a new reading. This is the gate time of the rate counters. The list which is returned
contains the sync rate and the rates of the input channels.

Note
----
In case of PH330 this function gives you the input filter rates, where :meth:`getMainRates` gives you the output filter rates.
    
Parameters
----------
    None
    
Returns
-------
    countrates: array of int
    
Example
-------
::
    
    cntRs = sn.filter.getRowRates()
    syncrate = cntRs[0]
    chan1rate = cntRs[1]
    
        """
        syncRate =  ct.pointer(ct.c_int(0))
        countRates = ct.ARRAY(ct.c_int, 64)()
        if ok:=  self.parent.dll.getRowFilteredRates(syncRate, countRates):
            a = np.array(countRates)
            a = np.resize(a, self.parent.deviceConfig["NumChans"])
            a = np.insert(a, 0, syncRate.contents.value)
            return a
        
        else:
            return []
    
    
    def getMainRates(self):
        """
    Supported devices: [MH150/160 | PH330] 
    
This call retrieves the count rates after the Main Filter before entering the FiFO. A measurement must be running to obtain
valid results. Allow at least 100 ms to get a new reading. This is the gate time of the rate counters. The list which is returned
contains the sync rate and the rates of the input channels.
    
Parameters
----------
    None
    
Returns
-------
    countrates: array of int
    
Example
-------
::
    
    cntRs = sn.filter.getMainRates()
    syncrate = cntRs[0]
    chan1rate = cntRs[1]
    
        """
        syncRate =  ct.pointer(ct.c_int(0))
        countRates = ct.ARRAY(ct.c_int, 64)()
        if ok:= self.parent.dll.getMainFilteredRates(syncRate, countRates):
            a = np.array(countRates)
            a = np.resize(a, self.parent.deviceConfig["NumChans"])
            a = np.insert(a, 0, syncRate.contents.value)
            return a
        
        else:
            return []
    
    
# measurement classes
class Raw():
    """This is the `Raw` measurement class.

This class is made to directly access the TTTR (Time Tagged Time-Resolved) data. 
The format of the data depends on the :class:`.MeasMode` in the :meth:`snAPI.initDevice` function.

Each :obj:`.MeasMode.T2` event record consists of 32 bits. There are 6 bits for the channel number and 25 bits 
for the time tag. If the time tag overflows, a special overflow marker record is inserted in the
data stream, so that upon processing of the data stream a theoretically infinite time span can be
recovered at full resolution. 

Each :obj:`.MeasMode.T3` event record consists of 32 bits. There are 6 bits for the channel number, 15 bits
for the start stop time and 10 bits for the sync counter. If the counter overflows, a special
overflow marker record is inserted in the data stream, so that upon processing of the data stream
a theoretically infinite time span can be recovered. The 15 bits for the start stop time cover a
time span of 32768 times the chosen resolution. If the time difference between photon and the last
sync event is larger than this span the photon event cannot be recorded. This is the same as in
:obj:`.MeasMode.Histogram`, where the number of time bins is larger but also finite. However, by choosing a
suitable sync rate and a compatible resolution, it should be possible to reasonably accommodate
all relevant experiment scenarios. 

Note
----
    This class is provided primarily to enable compatibility with the native MHLib data formats. 
    It is recommended to use the :class:`Unfold` class instead, which allows much more convenient access to the data.
    
There are special functions to decode the :obj:`.MeasMode.T2`and :obj:`.MeasMode.T3` data records:
    - :meth:`isSpecial`
    - :meth:`timeTag_T2`
    - :meth:`nSync_T3`
    - :meth:`dTime_T3`
    - :meth:`channel`
    - :meth:`isMarker`
    - :meth:`markers`

.. seealso ::
    | To fully understand the TTTR format please read the MultiHarp manual and/or
    | `Time Tagged Time-Resolved Fluorescence Data Collection in Life Sciences <https://www.picoquant.com/images/uploads/page/files/14528/technote_tttr.pdf>`_
    | :ref:`TCSPC specific record formats <TCSPC specific record formats>`

    """

    def __init__(self, parent):
        self.parent = parent
        self.data = ct.ARRAY(ct.c_uint32, 0)()
        self.finished = ct.pointer(ct.c_bool(False))
        self.idx = ct.pointer(ct.c_uint64(0))
        

    def measure(self, acqTime: typing.Optional[int] = 1000, size: typing.Optional[int] = 134217728, waitFinished: typing.Optional[bool] = True, savePTU: typing.Optional[bool] = False):
        """
With this function a simple measurement of `Raw` data records into RAM and/or disc is provided.
Therefore, you must define the size of the buffer raw.data. If `waitFinished` is set `True` the call will be blocked
until the measurement is completed. If you wish to avoid blocking you can pass `waitFinished` as `False`
and run other code. In order to check later if the measurement is completed you can use
the :meth:`isFinished` function. The data can be accessed with :meth:`getData`.

Caution
-------
If a `Raw Buffer overrun - clearing!` warning or `Raw Buffer full - waiting!` info means, that data cant be stored
in the allocated memory `size`. Increase the memory `size`, to resolve this issue by using the non blocking measure
or the :meth:`startBlock` and :meth:`getBlock`!

Note
----
    If you want to write the data to disc only, set the size to zero.

Warning
-------
    If the colleted data exceeds the buffer size a warning will be added to the log: 
    'WRN RawStore buffer overrun - clearing!' and de internal buffer will be cleared. That
    means that this part of the data is lost! You should reduce the count rate to prevent this!

Parameters
----------
    acqTime: int (default: 1s)
        | 0: means the measurement will run until :meth:`stopMeasure`
        | acquisition time [ms]
        | will be ignored if device is a FileDevice
    size: int number of records (default: 128 million records = 1GB)
        memory size for the data array
    waitFinished: bool (default: True)
        True: block execution until finished (will be False on acqTime = 0)
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # reads `Raw` data for 1 sec in :obj:`.MeasMode.T2` 
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.raw.measure(1000)
    data = sn.raw.getData()
    sn.logPrint(f"{len(data)} records read!")
    
    # this reads `Raw` data for 1 sec in :obj:`.MeasMode.T2` and writes it to disc only
    sn.raw.measure(1000, 0, True, True)
    
        """
        self.data = ct.ARRAY(ct.c_uint32, size)()
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "measurement is not supported for Raw class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return False
        return self.parent.dll.rawMeasure(acqTime, waitFinished, savePTU, ct.byref(self.data), self.idx, ct.c_uint64(size), self.finished)
    

    def startBlock(self, acqTime: typing.Optional[int] = 1000, size: typing.Optional[int] = 134217728, savePTU: typing.Optional[bool] = False):
        """
This function starts a block-wise data measurement. It refers to the practice of collecting, processing,
or transmitting data in discrete blocks or chunks, rather than as a continuous stream. Instead of receiving
all the data at once, the data is divided into manageable blocks, which are processed or analyzed one at a
time. This approach offers several benefits, such as efficient use of resources, real-time processing,
and the ability to handle data streams that are too large to process all at once.
The data is collected by the API until you capture it by the :meth:`getBlock` function.
The size of the block depends on the count rate and the time that reached until the next :meth:`getBlock` is executed. You also
have to set the size parameter to define the maximum size of the available block buffer. The data can be accessed with :meth:`getBlock`.

Warning
-------
    If the colleted data exceeds the maximum block size a warning will be added to the log: 
    'WRN RawStore buffer overrun - clearing!' and de internal buffer will be cleared. That
    means that this part of data is lost! You should reduce the count rate!

Parameters
----------
    acqTime: int (default: 1s)
        acquisition time [ms]
        will be ignored if device is a FileDevice
    size: int number of records (default: 1GB = 256 million records * 32Bit)
        maximum memory size for the block
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # reads `Raw` data every second for 10 seconds :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.raw.startBlock(10000)
    while not sn.raw.isFinished():
        time.sleep(1)
        data = sn.raw.getBlock()
        if sn.raw.numRead():
            sn.logPrint(f"{sn.raw.numRead()} records read")
    
        """
        self.storeData = ct.ARRAY(ct.c_uint32, size)()
        self.data = ct.ARRAY(ct.c_uint32, size)()
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "startBlock is not supported for Raw class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return False
        return self.parent.dll.rawStartBlock(acqTime, savePTU, ct.byref(self.storeData), ct.c_uint64(size), self.finished)
    

    def getBlock(self):
        """
This function gets the last block of data from the API and returns it in form of an array of `Raw` data records.

Parameters
----------
    none

Returns
-------
    NDArray[int]:
        `Raw` data

Example
-------
::

    # reads `Raw` data every second for 10 seconds :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.raw.startBlock(10000)
    while not sn.raw.isFinished():
        time.sleep(1)
        data = sn.raw.getBlock()
        if sn.raw.numRead():
            sn.logPrint(f"{sn.raw.numRead()} records read")
    
        """
        size = ct.pointer(ct.c_uint64(0))
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "startBlock is not supported for Raw class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            self.idx.contents.value = 0
        else:
            self.parent.dll.rawGetBlock(ct.byref(self.data), size)
            self.idx.contents.value = size.contents.value
        return self.getData()
    

    def getData(self, numRead: typing.Optional[int] = None):
        """
This function returns the data of a measurement.

Note
----
    This function is part of the :meth:`getBlock` function.

Parameters
----------
    numRead: int (default: None)
        number of data records to read (default: all data available)
        
Returns
-------
    NDArray[int]:
        `Raw` data

Example
-------
::

    # reads `Raw` data every second for 10 seconds :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.raw.startBlock(10000)
    while not sn.raw.isFinished():
        time.sleep(1)
        data = sn.raw.getBlock()
        if sn.raw.numRead():
            sn.logPrint(f"{sn.raw.numRead()} records read")
    
        """
        if not numRead:
            numRead = self.numRead()
            
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "getData is not supported for Raw class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return []
        return np.lib.stride_tricks.as_strided(self.data, shape=(1, numRead),
            strides=(ct.sizeof(self.data._type_) * numRead, ct.sizeof(self.data._type_)))[0]
    

    def numRead(self):
        """
This function returns the number of available data records if you measure into the RAM with :meth:`measure` or it gives the
block size if you measure in block mode with :meth:`getBlock`.

Parameters
----------
    none

Returns
-------
    int:
        number of data records

Example
-------
::

    # prints the number of data records
        sn.logPrint(f"{sn.raw.numRead()} data records")
    
        """
        return self.idx.contents.value
    

    def isFinished(self):
        """
This function tells you if the measurement is finished.

Warning
-------
    If the measurement is finished, there might be some data available, which was not retrieved yet. It may be necessary to 
    call :meth:`getData()` or :meth:`getBlock()` once again after `isFinished` returns `True`.
    Check out the example of a possible implementation below.

Parameters
----------
    none

Returns
-------
    True: the measurement is finished
    False: the measurement is running

Example
-------
::

    # runs a while loop until the measurement is finished (wrong)
        while not sn.raw.isFinished():
        data = sn.raw.getData()
        if len(data) > 0:
            ...
    
    # break a while loop if the measurement is finished and reads the last data 
        while True:
        finished = sn.raw.isFinished()
        data = sn.raw.getData()
        if len(data) > 0:
            ...
            
        if finished:
            break
    
        """
        return self.finished.contents.value
        

    def stopMeasure(self):
        """
After a measurement is started it will normally be left running until the defined acquisition
time has elapsed. However, sometimes it may be necessary to stop a measurement manually with
this function.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._stopMeasure()
    

    def isSpecial(self, data: int) :
        """
This function takes a T2 or T3 `Raw` data record and returns `True` if it is a special record.

Parameters
----------
    data: int
        a `Raw` data record
Returns
-------
    True: the given data record is a special record
    False: it is not a special record

Example
-------
::

    # branches if data[i] is a special record 
    if sn.raw.isSpecial(data[i]):
        ...
    
        """
        return ((0x80000000 & data) !=0 )
        

    def timeTag_T2(self, data: int) :
        """
This function takes a T2 `Raw` data record and returns the timetag.

Warning
-------
    Do not use this function with a T3 `Raw` data record.
    
Parameters
----------
    data: int
        a T2 `Raw` data record
Returns
-------
    timetag: int


Example
-------
::

    # prints out the timetag of a T2 `Raw` data record in data[i]
    sn.logPrint(sn.raw.timeTag_T2(data[i]))
    
        """
        return (0x01FFFFFF & data)
    

    def nSync_T3(self, data: int) :
        """
This function takes a T3 `Raw` data record and returns the number of the sync period this event occurred in.

Warning
-------
    Do not use this function with a T2 `Raw` data record.
    
Parameters
----------
    data: int
        a T3 `Raw` data record
        
Returns
-------
    timetag: int


Example
-------
::

    # prints out the number of the sync period of the `Raw` T3 record in data[i] 
    sn.print(sn.raw.nSync_T3(data[i]))
    
        """
        return (0x000003FF & data)
    

    def dTime_T3(self, data: int) :
        """
This function takes a T3 `Raw` data record and returns the differential time.

Warning
-------
    Do not use this function with a T2 `Raw` data record.
    
Parameters
----------
    data: int
        a T3 `Raw` data record
        
Returns
-------
    differential time: int

Example
-------
::

    # prints out the differential time of a T3 `Raw` data record 
    sn.print(sn.raw.dTime_T3(data[i]))
    
        """
        return (0x00007FFF & (data >> 10))
    

    def channel(self, data: int) :
        """
This function takes a T2 or T3 `Raw` data record and returns the channel number if its not
a special record or a marker record. Check it with :meth:`isMarker`.

Parameters
----------
    data: int
        a `Raw` data record
        
Returns
-------
    channelNumber: int

Example
-------
::

    # counts the number of records by the channel number
    cnts  = [0] * sn.deviceConfig["NumChans"] + 1
    for i in range(sn.raw.numRead()):
        if not sn.raw.isMarker(data[i]):
            chanIdx = sn.raw.channel(data[i])
            cnts[chanIdx] += 1

        """
        return ((data >> 25) &  0x0000003F) + 1
    

    def isMarker(self, data: int) :
        """
This function takes a T2 or T3 `Raw` data record and returns `True` if it is a marker record.

Parameters
----------
    data: int
        a `Raw` data record
Returns
-------
    True: the given data record is a marker record
    False: it is not a marker record

Example
-------
::

    # branches if data[i] is a marker record 
    if sn.raw.isMarker(data[i]):
        ...
    
        """
        c = self.channel(data)
        return (self.isSpecial(data) and c >= 1 and c <= 15)
    

    def markers(self, data: int) :
        """
This function takes a T2 or T3 `Raw` data record and returns an array holding the 4 possible
markers.

Warning
-------
    Only use this function with a marker record. Check it with :meth:`isMarker` before.
    
Parameters
----------
    data: int
        a `Raw` data marker record
        
Returns
-------
    array: bool

Example
-------
::

    # branches if the marker 2 is set in the `Raw` data record
        if sn.raw.isMarker(data[i]):
            if sn.raw.markers(data[i])[1]
                ...

        """
        markers = (0x7F & data)
        return [markers & 0x01 != 0, (markers & 0x02) != 0, (markers & 0x04) != 0, (markers & 0x08) != 0]
    


class Unfold():
    """This is the `Unfold` measurement class.

This measurement class can be used to conveniently access the TTTR (Time Tagged Time-Resolved) data. 
The format does not depend on the :class:`.MeasMode` in the :meth:`snAPI.initDevice` function,
but in the :obj:`.MeasMode.T3`, the sync records are removed to increase the throughput on the usb bus.

Note
----
    This class was created to provide a better user experience than the `Raw` data class. The overflow records
    have been removed an the timetags now have a width of 64Bit. The channel information is stored in a separate
    array.
        
There are special functions to decode the channel information:
    - :meth:`isMarker`
    - :meth:`markers`

.. seealso ::
    | To fully understand the TTTR format read
    | `Time Tagged Time-Resolved Fluorescence Data Collection in Life Sciences <https://www.picoquant.com/images/uploads/page/files/14528/technote_tttr.pdf>`_

    """
        

    def __init__(self, parent):
        self.parent = parent
        self.times = ct.ARRAY(ct.c_uint64, 0)()
        self.channels = ct.ARRAY(ct.c_uint8, 0)()
        self.idx = ct.pointer(ct.c_uint64(0))
        self.finished = ct.pointer(ct.c_bool(False))


    def setT3Format(self, format: typing.Optional[UnfoldFormat] = UnfoldFormat.DTimesSyncCntr) :
        """
This function sets the content format of the times array of the unfold data stream.

Note
----
    Only meaningful in :obj:`.MeasMode.T3`.
    
Parameters
----------
    format: UnfoldFormat (default: UnfoldFormat.DTimesSyncCntr)
        
Returns
-------
    none

Example
-------
::

    # creates a unfold data stream in :obj:`.UnfoldFormat.DTimes` with differential times 
    sn.histogram.setT3Format(UnfoldFormat.DTimes)

        """
        if(self.parent.deviceConfig["MeasMode"] != MeasMode.T3.value):
            self.parent.logPrint( "setT3Format is not supported in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
        self.parent.dll.setUnfoldT3Format(format.value)


    def measure(self, acqTime: typing.Optional[int] = 1000, size: typing.Optional[int] = 134217728, waitFinished: typing.Optional[bool] = True, savePTU: typing.Optional[bool] = False):
        """
With this function a simple measurement of Unfolded data records into RAM and/or disc is provided.
Beforehand, you must define the size of the buffer that is unfold.data. If waitFinished is set `True` the call
will block until the measurement is completed. If `waitFinished` is set `False` (default) you can get
updates on the fly, and you can request the execution status with the :meth:`isFinished` function.
If you wish to avoid blocking you can set `waitFinished` `False` and proceed with other code. Again, you
can check if the measurement is completed by using the :meth:`isFinished` function.
The data can be accessed with :meth:`getData`.

Caution
-------
The `Unfold buffer overrun - clearing!` warning or `Unfold Buffer full - waiting!` info means, that data could not be stored
in the allocated memory. Increase the memory by the `size` parameter, use the non blocking measure or block read 
functions the :meth:`startBlock` and :meth:`getBlock` instead!
    
Parameters
----------
    acqTime: int (default: 1s)
        | 0: means the measurement will run until :meth:`stopMeasure`
        | acquisition time [ms]
        | will be ignored if device is a FileDevice
    size: int number of records (default: 1 billion records = 8GB)
        memory size for the data array
    waitFinished: bool (default: True)
        True: block execution until finished (will be False on acqTime = 0)
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # reads `Unfold` data for 1 sec in :obj:`.MeasMode.T2`
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.unfold.measure(1000)
    data = sn.unfold.getData()
    sn.logPrint(f"{len(data)} records read")
    
    # this reads `Unfold` data for 1 sec in :obj:`.MeasMode.T2` and write it to disc only
    sn.unfold.measure(1000, 0, True, True)
    
        """
        self.times = ct.ARRAY(ct.c_uint64, size)()
        self.channels = ct.ARRAY(ct.c_uint8, size)()
        self.idx = ct.pointer(ct.c_uint64(0))
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "measurement is not supported for Unfold class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return False
        return self.parent.dll.ufMeasure(acqTime, waitFinished, savePTU, ct.byref(self.times), ct.byref(self.channels), self.idx, ct.c_uint64(size), self.finished)
    

    def startBlock(self, acqTime: int= 1000, size: int = 134217728, savePTU: typing.Optional[bool] = False):
        """
This function starts a block-wise data measurement. It refers to the practice of collecting, processing,
or transmitting data in discrete blocks or chunks, rather than as a continuous stream. Instead of receiving
all the data at once, the data is divided into manageable blocks, which are processed or analyzed one at a
time. This approach offers several benefits, such as efficient use of resources, real-time processing,
and the ability to handle data streams that are too large to process all at once.
The data is collected by the API internally until you retrieve it via the :meth:`getBlock` function.
The size of the block depends on the count rate and the time that elapsed until the next blockRead is executed.
Beforehand, you have to define the maximum size of the available block buffer. The data can be accessed with :meth:`getBlock`.

Warning
-------
    If the colleted data exceeds the maximum block size a warning will be added to the log: 
    'WRN UfStore buffer overrun - clearing!' and the internal buffer will be cleared. This
    means that this part of data is lost! To prevent this you should reduce the count rate!

Parameters
----------
    acqTime: int (default: 1s)
        | 0: means the measurement will run until :meth:`stopMeasure`
        | acquisition time [ms]
        | will be ignored if device is a FileDevice
    size: int number of records (default: 1GB = 128 million records * 64Bits)
        maximum memory size for the block
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # reads `Unfold` data every second for 10 seconds :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.unfold.startBlock(10000)
    while not sn.unfold.isFinished():
        time.sleep(1)
        data = sn.unfold.getBlock()
        if sn.unfold.numRead():
            sn.logPrint(f"{sn.unfold.numRead()} records read")
    
        """
        self.storeTimes = ct.ARRAY(ct.c_uint64, size)()
        self.storeChannels = ct.ARRAY(ct.c_uint8, size)()
        self.times = ct.ARRAY(ct.c_uint64, size)()
        self.channels = ct.ARRAY(ct.c_uint8, size)()
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "startBlock is not supported for Unfold class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return False
        return self.parent.dll.ufStartBlock(acqTime, savePTU, ct.byref(self.storeTimes), ct.byref(self.storeChannels), ct.c_uint64(size), self.finished)
    

    def getBlock(self):
        """
This function retrieves the last block of data from the API and returns the of `Unfold` data as an array.

Parameters
----------
    none

Returns
-------
    tuple [1DArray, 1DArray]
        times: 1DArray[int]
            `Unfold` data array of timetags
        channels: 1DArray[int]
            `Unfold` data array of channel information

Example
-------
::

    # reads `Unfold` data every second for 10 seconds in :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.unfold.startBlock(10000)
    while not sn.unfold.isFinished():
        time.sleep(1)
        times, channels = sn.unfold.getBlock()
        if sn.unfold.numRead():
            sn.logPrint(f"{sn.unfold.numRead()} records read")
    
        """
        size = ct.pointer(ct.c_uint64(0))
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "startBlock is not supported for Unfold class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            self.idx.contents.value = 0
        else:
            self.parent.dll.ufGetBlock(ct.byref(self.times), ct.byref(self.channels), size)
            self.idx.contents.value = size.contents.value
        return self.getData()
    

    def getData(self, numRead: typing.Optional[int] = None):
        """
This function returns the data of a measurement.


Note
----
    This function is also used as part a of the :meth:`getBlock` function.

Parameters
----------
    numRead: int (default: None)
        number of data to read (default: all data available)
        
Returns
-------
    tuple [1DArray, 1DArray]
        times: 1DArray[int]
            `Unfold` data array of timetags
        channels: 1DArray[int]
            `Unfold` data array of channel information


Example
-------
::

    # reads `Unfold` data every second for 10 seconds in :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.unfold.startBlock(10000)
    while not sn.unfold.isFinished():
        time.sleep(1)
        times, channels = sn.unfold.getBlock()
        if sn.unfold.numRead():
            sn.logPrint(f"{sn.unfold.numRead()} records read")
    
        """
        if not numRead:
            numRead = self.numRead()
        return self.getTimes(numRead), self.getChannels(numRead)
    

    def getTimes(self, numRead: int):
        """
This function returns a tuple of two arrays holding the data of an `Unfold` measurement. The arrays contain the timetag and the 
channel information.

Note
----
    This function is part of the :meth:`getBlock` function.

Parameters
----------
    numRead: int (default: None)
        number of data to read (default: all data available)
        
Returns
-------
    tuple [1DArray, 1DArray]
        times: 1DArray[int]
            `Unfold` data array of timetags
        channels: 1DArray[int]
            `Unfold` data array of channel information

Example
-------
::

    # reads `Unfold` data every second for 10 seconds in :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.unfold.startBlock(10000)
    while not sn.unfold.isFinished():
        time.sleep(1)
        times, channels = sn.unfold.getBlock()
        if sn.unfold.numRead():
            sn.logPrint(f"{sn.unfold.numRead()} records read")
    
        """
        return np.lib.stride_tricks.as_strided(self.times, shape=(1, numRead),
            strides=(ct.sizeof(self.times._type_) * numRead, ct.sizeof(self.times._type_)))[0]
    

    def getChannels(self, numRead: int):
        """
This function returns an array of channel information of an `Unfold` measurement. This can contain
channels and marker. If you ar using markers you can check it with :meth:`isMarker` and get the marker
index with :meth:`markers`.

Note
----
    This function is part of the :meth:`getData` function.

Parameters
----------
    numRead: int (default: None)
        number of data records to read (default: all data available)
Returns
-------
        channels: 1DArray[int]
            `Unfold` data array of timetags
    
        """
        return np.lib.stride_tricks.as_strided(self.channels, shape=(1, numRead),
            strides=(ct.sizeof(self.channels._type_) * numRead, ct.sizeof(self.channels._type_)))[0]
    

    def numRead(self):
        """
This function returns the number of available data records if you measure into RAM with :meth:`measure`
otherwise it gives the block size if you measure in block mode with :meth:`getBlock`.

Parameters
----------
    none

Returns
-------
    int:
        number of data records

Example
-------
::

    # prints the number of data records
        sn.logPrint(f"{sn.unfold.numRead()} data records")
    
        """
        return self.idx.contents.value
    

    def isFinished(self):
        """
This function reports whether the measurement is finished.

Warning
-------
    If the measurement is finished, there might be some data available, which was not retrieved yet. It may be necessary to 
    call :meth:`getData()` or :meth:`getBlock()` once again after `isFinished` returns `True`.
    Check out the example of a possible implementation below.

Parameters
----------
    none

Returns
-------
    True: the measurement is finished
    False: the measurement is running

Example
-------
::

    # runs a while loop until the measurement is finished
        while sn.unfold.isFinished():
        data = sn.unfold.getData()
        if len(data[0]) > 0:
            ...
    
    # break a while loop if the measurement is finished and reads the last data 
        while True:
        finished = sn.unfold.isFinished()
        data = sn.unfold.getData()
        if len(data[0]) > 0:
            ...
            
        if finished:
            break
    
        """
        return self.finished.contents.value
    

    def stopMeasure(self):
        """
After a measurement is started it will normally be left running until the defined acquisition
time has elapsed. However, sometimes it may be necessary to stop a measurement manually with
this function.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._stopMeasure()
    

    def getTimesByChannel(self, channel: int, size: typing.Optional[int] = None):
        """
This function gives you the timetags of a given channel of the current measurement.

Parameters
----------
    channel: int
        channel number starting at 0 for the sync channel and 1 for channel 1 
    size: int (default: None)
        number of data records to process (default: all data available)

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # reads `Unfold` data every second for 10 seconds in :obj:`.MeasMode.T3`  
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    sn.unfold.startBlock(10000)
    while not sn.unfold.isFinished():
        time.sleep(1)
        data = sn.unfold.getBlock()
        if sn.unfold.numRead():
            sn.logPrint(f"{sn.unfold.numRead()} records read")
    
        """
        if not size:
            size = self.numRead()
        timesOut = ct.ARRAY(ct.c_uint64, size)()
        size = ct.pointer(ct.c_uint64(size))
        if size.contents.value > 0:
            self.parent.dll.getTimesFromChannelUF(ct.byref(self.channels), ct.byref(self.times), ct.byref(timesOut), channel, size)
        return np.lib.stride_tricks.as_strided(timesOut, shape=(1, size.contents.value),
            strides=(ct.sizeof(timesOut._type_) * size.contents.value, ct.sizeof(timesOut._type_)))[0]
    

    def isMarker(self, channel) :
        """
This function takes a T2 or T3 `Unfold` channel record and returns `True` if it is a marker record.

Parameters
----------
    data: int
        a `Unfold` channel record
Returns
-------
    True: the given channel record is a marker record
    False: it is not a marker record

Example
-------
::

    # branches if its a marker record 
    if sn.unfold.isMarker(channels[i]):
        ...
    
        """
        return ((0x80 & channel) != 0) 
    

    def markers(self, channel) :
        """
This function takes an `Unfold` data record and returns an array of the four possible markers signals.

Warning
-------
    Only use this function with a marker record. Check the `channel` array with :meth:`isMarker` before.
    
Parameters
----------
    data: int
        a `Unfold` data marker record
        
Returns
-------
    array: bool

Example
-------
::

    # branches if the marker 2 is set in the `Raw` data record
    if sn.unfold.isMarker(data[i]):
        if sn.unfold.markers(data[i])[1]
            ...

        """
        marker = (0x7F & channel)
        return [marker & 0x01, (marker & 0x02) != 0, (marker & 0x04) != 0, (marker & 0x08) != 0]


    def nSync_T3(self, times: int) :
        """
This function takes a T3 `Unfold` data record and returns the number of the sync period this event occurred in.

Warning
-------
    Use this function with a T3 `Unfold` data record. with :obj:`.UnfoldFormat.DTimesSyncCntr`.
    
Parameters
----------
    data: int
        a T3 `Raw` data record
        
Returns
-------
    timetag: int


Example
-------
::

    # prints out the number of the sync period of the `Raw` T3 record in data[i]
    sn.print(sn.unfold.nSync_T3(times[i]))
    
        """
        return (times.astype(np.int64) >> 15).astype(np.uint64)
    

    def dTime_T3(self, times: int) :
        """
This function takes a T3 `Unfold` data record and returns the differential time.

Warning
-------
    Use this function with the T3 `Unfold` data record. with :obj:`.UnfoldFormat.DTimesSyncCntr`.
    When using the T3 `Unfold` data record with :obj:`.UnfoldFormat.DTimes` this function is not required,
    because the times array consists only of `dTimes`.
    
Parameters
----------
    data: int
        a T3 `Unfold` data record
        
Returns
-------
    differential time: int

Example
-------
::

    # prints out the differential time of a T3 `Unfold` data record 
    sn.print(sn.unfold.dTime_T3(times[i]))
    
        """
        return (0x00007FFF & times.astype(np.int64)).astype(np.uint64)
    

class Histogram():
    """
This measurement class provides you with histograms of time differences between the channels. 
The device's internal histogramming and :obj:`.MeasMode.T3` always calculate the
differences between the sync and the other channels. However, in :obj:`.MeasMode.T2` you
can change the reference channel and histograms of the time differences between this refChannel
and itself as well as all other channels including the sync channel are created.

.. image:: _static/01_Histogram.png
    :width: 600px
    :class: only-light
    
.. image:: _static/01_Histogram_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the generation of a Histogram measurement.`

Caution
-------
To calculate the histogram in :obj:`.MeasMode.T3` it is necessary to store `dTimes` (time difference between the
sync- and the channel events) in the returned bins array of the internal unfold data stream, because the sync events
are removed. Therefore the :class:`Manipulators` may work different than with absolute times stored in the unfold
data stream. They may only be correct in between there sync periods. If you need the default behaviour you have
to use the :obj:`.MeasMode.T2` instead.
    
    """
    

    def __init__(self, parent):
        self.parent = parent
        self.data = ct.ARRAY(ct.c_long, 0)()
        self.numBins = 0
        self.bins = []
        self.finished = ct.pointer(ct.c_bool(False))
        

    def setRefChannel(self, channel: typing.Optional[int] = 0) :
        """
This function sets the reference channel used to calculate the time differences with respect
to the other channels. The histograms are then created from these calculated data.

Note
----
    Only meaningful in :obj:`.MeasMode.T2`.
    
Parameters
----------
    channel: int (default: 0 sync channel)
        the reference channel (0 is sync channel)
        
Returns
-------
    none

Example
-------
::

    # creates a histogram in :obj:`.MeasMode.T2` with channel 1 as reference channel
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.histogram.setRefChannel(1)
    sn.histogram.measure(1000)
    data, bins = sn.histogram.getData()
            ...

        """
        if(self.parent.deviceConfig["MeasMode"] != MeasMode.T2.value):
            self.parent.logPrint( "setRefChannel is not supported in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
        self.parent.dll.setHistoT2RefChan(channel)


    def setBinWidth(self, binWidth: typing.Optional[int] = None):
        """
This function sets the `binWidth` of the time differences for the histograms are to be build.

Warning
-------
    Only meaningful in :obj:`.MeasMode.T2`.
    
Parameters
----------
    binWidth: int (default: BaseResolution)
        the bin width in ps
        
Returns
-------
    none

Example
-------
::

    # creates a histogram T2 mode with bin width of 5ps
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.histogram.setBinWidth(5)
    sn.histogram.measure(1000)
    data, bins = sn.histogram.getData()
            ...

        """
        if not binWidth:
            binWidth = self.parent.deviceConfig["BaseResolution"]
        if(self.parent.deviceConfig["MeasMode"] != MeasMode.T2.value):
            self.parent.logPrint( "setBinWidth is not supported in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
        self.parent.dll.setHistoT2BinWidth(binWidth)


    def measure(self, acqTime: typing.Optional[int] = 1000, waitFinished: typing.Optional[bool] = True, savePTU: typing.Optional[bool] = False):
        """
With this function a measurement and creation of a histogram us initiated, which ist stored 
into RAM and/or disc. If `waitFinished` is set `True` the call will be blocked until the measurement
is completed. If `waitFinished` is set to `False` (default) you can get updates on the fly,
and you can access the execution status with the :meth:`isFinished` function.
If you wish to obtain updates on the fly the data can be accessed with :meth:`getData`.

Note
----
    If you want to write the data to disc only, set the size to zero.

Warning
-------
    If the colleted data exceeds the buffer size a warning will be added to the log: 
    'WRN UfStore buffer overrun - clearing!' and the internal buffer will be cleared. This
    means that this part of data is lost! To prevent this, you should reduce the count rate.
    
Parameters
----------
    acqTime: int (default: 1s)
        | 0: means the measurement will run until :meth:`stopMeasure`
        | acquisition time [ms]
        | will be ignored if device is a FileDevice
    size: int number of records (default: 128 million records = 1GB)
        memory size for the data array
    waitFinished: bool (default: True)
        True: block execution until finished (will be False on acqTime = 0)
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # calculates `Histogram` data for 1 sec in MeasMode.T2 
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.histogram.measure(1000)
    data, bins = sn.histogram.getData()
    
        """
        self.numBins = self.parent.deviceConfig["NumBins"]
        numChans = self.parent.getNumAllChannels()
        self.data = ct.ARRAY(ct.c_long, numChans * self.numBins)(0)
        
        self.bins = range(self.numBins)
        if (self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.bins = np.multiply(self.bins, self.parent.deviceConfig["BaseResolution"])
        else:
            self.bins = np.multiply(self.bins, self.parent.deviceConfig["Resolution"])
            
        return self.parent.dll.getHistogram(acqTime, waitFinished, savePTU, ct.byref(self.data), self.finished)
    

    def getData(self):
        """
This function returns the data of the histogram measurement.

Parameters
----------
    none
            
Returns
-------
    tuple [1DArray, 1DArray]
        histogram: 1DArray[int]
            data array of counts
        bins: 1DArray[int]
            data array of bins [s]

Example
-------
::

    # reads `Histogram` data every second for 10 seconds :obj:`.MeasMode.T3`
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.device.setInputDeadTime(-1,1000)
    waitFinished = False
    sn.device.setStopOverflow(1000000)
    sn.histogram.setRefChannel(0)
    sn.histogram.measure(100000, waitFinished, False)
    
    while True:
        data, bins = sn.histogram.getData()
        ...
        
        if waitFinished or sn.histogram.isFinished():
            break
    
        """
        self.numBins = self.parent.deviceConfig["NumBins"]
        numChans = self.parent.getNumAllChannels()
        dataOut = np.lib.stride_tricks.as_strided(self.data, shape=(numChans, self.numBins),
            strides=(ct.sizeof(self.data._type_) * self.numBins, ct.sizeof(self.data._type_)))
        return dataOut, self.bins
    

    def stopMeasure(self):
        """
After a measurement is started it will normally be left running until the defined acquisition
time has elapsed. However, sometimes it may be necessary to stop a measurement manually with
this function.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._stopMeasure()
    
        
    def clearMeasure(self):
        """
Some measurements calculate their results on large sets of historical data. When conditions have changed,
the old data may need to be deleted to get an unobstructed view of the new data. This function deletes the internal 
data without having to restart the measurement.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._clearMeasure()
    

    def isFinished(self):
        """
This function reports whether the measurement is finished.

Warning
-------
    If the measurement is finished, there might be some data available, which was not retrieved yet. It may be necessary to 
    call :meth:`getData()` or :meth:`getBlock()` once again after `isFinished` returns `True`.
    Check out the example of a possible implementation below.

Parameters
----------
    none

Returns
-------
    True: the measurement is finished
    False: the measurement is running

Example
-------
::

    # runs a while loop until the measurement is finished
        while sn.histogram.isFinished():
        data = sn.histogram.getData()
            ...
    
    # break a while loop if the measurement is finished and reads the last data 
        while True:
        finished = sn.histogram.isFinished()
        data = sn.histogram.getData()
            ...
            
        if finished:
            break
    
        """
        return self.finished.contents.value



class TimeTrace():
    """
This measurement class provides you with time trace data. This can be used for real-time
calibration of and optimization ae measurement setup.

Note
----
    Only meaningful in :obj:`.MeasMode.T2` and :obj:`.MeasMode.T3`.

.. image:: _static/02_TimeTrace.png
    :width: 600px
    :class: only-light
    
.. image:: _static/02_TimeTrace_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the principle of the TimeTrace measurement.`
    
    """

    def __init__(self, parent):
        self.parent = parent
        self.data = ct.ARRAY(ct.c_long, 0)()
        self.t0 = ct.c_uint64(0)
        self.numBins = 10000
        self.historySize = 10
        self.finished = ct.pointer(ct.c_bool(False))
        

    def setNumBins(self, numBins: typing.Optional[int] = 10000):
        """
This function sets the number of bins into which the counts are sorted.

Note
----
    The bin width can calculated as :math:`binWidth = historySize / numBins`.

Parameters
----------
    numBins: int (default: 10000)
        number of bins

Returns
-------
    none

Example
-------
::

    # sets thew number of bins to 10000
    sn.timeTrace.setNumBins(10000)
    
        """
        self.numBins = numBins
        self.parent.dll.setTimeTraceNumBins(numBins)
        

    def setHistorySize(self, historySize: typing.Optional[float] = 1):
        """
This function sets the length or duration of the recorded data in the time domain in which
the counts are collected.

Warning
-------
    It is possible to set the history size to nanoseconds to see the individual photons.
    However, because the data is processed in real time this may not be sustainable for live measurements at high count rates.
    If the data is read from a file it will work at any rate, but processing the file may take
    longer than it took to record it.
    
Note
----
    The bin width can calculated as :math:`binWidth = historySize / numBins`.

Parameters
----------
    historySize: float [s] (default: 1s)
        length or duration of the recorded data in the time domain

Returns
-------
    none

Example
-------
::

    # sets a history size of 10s
    sn.timeTrace.setHistorySize(10)
    
        """
        self.historySize = historySize
        self.parent.dll.setTimeTraceHistorySize.argtypes = [ct.c_double]
        self.parent.dll.setTimeTraceHistorySize(historySize)
        

    def measure(self, acqTime: typing.Optional[int] = 1000, waitFinished: typing.Optional[bool] = False, savePTU: typing.Optional[bool] = False):
        """
With this function a simple `TimeTrace` measurement into RAM and/or disc is provided. When waitFinished
is set `True` the call will block until the measurement is completed. However, in most cases you probably
want to avoid blocking in order to retrieve and display the data in real time. the data can be accessed
with :meth:`getData`.

Parameters
----------
    acqTime: int (default: 1s)
        | 0: means the measurement will run until :meth:`stopMeasure`
        | acquisition time [ms]
        | will be ignored if device is a FileDevice
    waitFinished: bool (default: False)
        True: block execution until finished (will be False on acqTime = 0)
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # gets real time data with a history size of 10s
    ...
    sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\HH400-PMT-cw-1MHz.ptu")
    sn.initDevice(MeasMode.T2)
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)
    
        """
        numChans = self.parent.getNumAllChannels()
        self.data = ct.ARRAY(ct.c_long, numChans * self.numBins)(0)
        
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "measure is not supported for TimeTrace class in MeasMode:", 
                MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return False
        
        return self.parent.dll.getTimeTrace(acqTime, waitFinished, savePTU, ct.byref(self.data), ct.byref(self.t0), self.finished)
    

    def getData(self, normalized: typing.Optional[bool] = True):
        """
This function returns the data of the time trace measurement. The data is optimized for display in a chart and therefore held in a FIFO buffer.

Parameters
----------
    normalized: bool (default: True)
        The counts will be normalized to its bin width, otherwise you get the absolute number of count per bin
    
Returns
-------
    tuple [1DArray, 1DArray]
        data: 1DArray[int]
            data array of counts normalized to counts per second
            :math:`countsPerSecond =  countsPerBin * historySize / numBins`
        times: 1DArray[int]
            data array of the start times of the bins from the beginning of the measurement [s]

Example
-------
::

    # plots a time trace from a file
    ...
    sn = snAPI()
    sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(255)
    sn.timeTrace.measure()
    counts, times = sn.timeTrace.getData()
    plt.clf()
    plt.plot(times, counts[0], linewidth=2.0, label='sync')
    plt.plot(times, counts[1], linewidth=2.0, label='chan1')
    plt.plot(times, counts[2], linewidth=2.0, label='chan2')
    plt.plot(times, counts[3], linewidth=2.0, label='chan3')
    plt.xlabel('Time [s]')
    plt.ylabel('Counts[Cts/s]')
    plt.legend()
    plt.title("TimeTrace")
    plt.pause(0.01)
    plt.show(block=True)
    
        """
        
        numChans = self.parent.getNumAllChannels()
        dataOut = np.lib.stride_tricks.as_strided(self.data, shape=(numChans, self.numBins),
            strides=(ct.sizeof(self.data._type_) * self.numBins, ct.sizeof(self.data._type_)))
        if normalized:
            dataOut = np.multiply(dataOut, self.numBins/self.historySize)
        
        t0 = (self.t0.value / self.numBins * self.historySize) - self.historySize
        times = range(self.numBins)
        times = np.multiply(times, self.historySize/self.numBins )
        times = np.add(times, t0 )

        return dataOut,times
    
    
    def isFinished(self):
        """
This function reports whether the measurement is finished.

Warning
-------
    If the measurement is finished, there might be some data available, which was not retrieved yet. It may be necessary to 
    call :meth:`getData()` or :meth:`getBlock()` once again after `isFinished` returns `True`.
    Check out the example of a possible implementation below.

Parameters
----------
    none

Returns
-------
    True: the measurement is finished
    False: the measurement is running

Example
-------
::

    # runs a while loop until the measurement is finished
        while sn.timetrace.isFinished():
        data = sn.timetrace.getData()
            ...
    
    # break a while loop if the measurement is finished and reads the last data 
        while True:
        finished = sn.timetrace.isFinished()
        counts, times = sn.timetrace.getData()
            ...
            
        if finished:
            break
    
        """
        return self.finished.contents.value


    def stopMeasure(self):
        """
After a measurement is started it will normally be left running until the defined acquisition
time has elapsed. However, sometimes it may be necessary to stop a measurement manually with
this function.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._stopMeasure()
        
        
    def clearMeasure(self):
        """
Some measurements calculate their results on large sets of historical data. When conditions have changed,
the old data may need to be deleted to get a an unobstructed view of the new data. This function deletes
the internal data without having to restart the measurement.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._clearMeasure()



class Correlation():
    """
This is the correlation measurement class with which it is possible to perform 
FCS (Fluorescence Correlation Spectroscopy) or g(2) correlations.
The g(2) correlation is calculated with bins of the same width while the FCS correlation with the
multi-tau algorithm uses pseudo-logarithmically increasing bin widths.

.. image:: _static/03_Correlation_Bunching.png
    :width: 600px
    :class: only-light

.. image:: _static/03_Correlation_Bunching_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the principle of the Correlation measurement.`
    
    """
    

    def __init__(self, parent):
        self.parent = parent
        self.data = ct.ARRAY(ct.c_double, 0)()
        self.bins = ct.ARRAY(ct.c_double, 0)()
        self.startChannel = 1
        self.stopChannel = 2
        self.numIntervals = 1
        self.intervalLength = 1000
        self.binWidth = 1000
        self.numBins = 0
        self.isFcs = False
        self.finished = ct.pointer(ct.c_bool(False))
        

    def setG2Parameters(self, startChannel: int, stopChannel: int, windowSize: float, binWidth: typing.Optional[float] = None):
        """
This function sets the the parameters for the g(2) correlation. If the `startChannel` is the same as the
`stopChannel` an autocorrelation is performed and if the channels are different a
cross calculation is done instead.

Note
----
    The g(2) correlation is normalized with the following factor:

.. math::
    :label: g2factor

    \\frac{\\Delta t}{binWidth \\cdot N_1 \\cdot N_2}
    
Here the :math:`\\Delta t` term represents the total time span of the correlation,
and :math:`N_1` and :math:`N_2` represent the total number of events in the two detection channels
during this time span.
    
Parameters
----------
    startChannel: int (0 is sync channel)
        start channel
    stopChannel: int (0 is sync channel)
        click channel
    windowSize: int [ps]
        size of the correlation window
    binWidth: int [ps]
        width of bins (Default: None - T2: BaseResolution, T3: Resolution) 

Returns
-------
    none

Example
-------
::

    # sets the window size to 5000ps with a bin width of 5ps (that means 1000 bins will be calculated)
    sn.correlation.setG2Parameters(1, 2 , 5000, 5)
    
        """
        if binWidth is None:
            if self.parent.deviceConfig["MeasMode"] == MeasMode.T2.value:
                binWidth = self.parent.deviceConfig["BaseResolution"]
            elif self.parent.deviceConfig["MeasMode"] == MeasMode.T3.value:
                binWidth = self.parent.deviceConfig["Resolution"]
                
        self.startChannel = startChannel
        self.stopChannel = stopChannel
        self.windowSize = windowSize
        self.binWidth = binWidth
        self.intervalLength = int(windowSize / binWidth)
        self.isFcs = False
        
        self.parent.dll.setG2Params.argtypes = [ct.c_int, ct.c_int, ct.c_double, ct.c_double]
        self.parent.dll.setG2Params(startChannel, stopChannel, windowSize, binWidth)
    

    def setFCSParameters(self, startChannel: int, stopChannel: int, windowSize: typing.Optional[float] = 1e12, startTime: typing.Optional[int] = None):
        """
This function sets the the parameters for the FCS correlation. If the `startChannel` is the same as the
`stopChannel` an autocorrelation is calculated and if the channels are different a
cross calculation is calculated.

Note
----
    The FCS correlation is calculated using the multiple tau algorithm with lag times according to:

.. math::
    :label: multiTau
    
    \\tau_k = \\tau_0 \\cdot 2^{\\left\\lfloor \\frac{k}{p} \\right\\rfloor} \\cdot \\left(1 + (k \\bmod p) \\right)

where:

- :math:`\\tau_0` is the initial lag time which is defined by the :obj:`snAPI.deviceConfig` **BaseResolution**
- :math:`k` is the index of the lag time in the sequence, with :math:`k = 0, 1, 2, \\dots, N-1`, where :math:`N` is the **numIntervals**
- :math:`p` is the period of the sequence, which is defined by **intervalLength** between successive powers of :math:`2`. \
For example, if :math:`\\tau_0 = 1` and :math:`p = 4`, then the sequence would include lag times of 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, and so on.
- :math:`\\lfloor \\cdot \\rfloor` denotes the floor function, which rounds a number down to the nearest integer
- :math:`\\bmod` is the modulus operator, which gives the remainder when dividing one number by another.

Parameters
----------
    startChannel: int (0 is sync channel)
        start channel
    stopChannel: int (0 is sync channel)
        click channel
    windowSize: int [ps]
        size of the correlation window
    startTime: int [ps]
        minimum tau, the left border of the correlation (Default: None - T2: BaseResolution, T3: Resolution)

Returns
-------
    none

Example
-------
::

    # sets the window size to 1s with a startTime of 50000ps
    sn.correlation.setG2Parameters(1, 2 , 1e12, 5e4)
    
        """
        if startTime is None:
            if self.parent.deviceConfig["MeasMode"] == MeasMode.T2.value:
                startTime = self.parent.deviceConfig["BaseResolution"]
            elif self.parent.deviceConfig["MeasMode"] == MeasMode.T3.value:
                startTime = self.parent.deviceConfig["Resolution"]
            
        self.startChannel = startChannel
        self.stopChannel = stopChannel
        self.windowSize = windowSize
        self.startTime = startTime
        self.isFcs = True
        pNumIntervals = ct.pointer(ct.c_int(0))
        pIntervalLength = ct.pointer(ct.c_int(0))
        
        self.parent.dll.setFCSParams.argtypes = [ct.c_int, ct.c_int, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.c_double, ct.c_double]
        self.parent.dll.setFCSParams(startChannel, stopChannel, pNumIntervals, pIntervalLength, windowSize, startTime)
        self.numIntervals = pNumIntervals.contents.value
        self.intervalLength = pIntervalLength.contents.value
        

    def measure(self, acqTime: typing.Optional[int] = 1000, waitFinished: typing.Optional[bool] = False, savePTU: typing.Optional[bool] = False):
        """
With this function a simple `Correlation` measurement is initiated. The results are stored into
RAM and/or disc. If `waitFinished` is set `True` the call will be blocked until the measurement
is completed. If `waitFinished` is set `False` (default) you can get updates on the fly, and you
can access the execution status with the :meth:`isFinished` function.
The data can be accessed with :meth:`getData`.

Parameters
----------
    acqTime: int (default: 1s)
        | 0: means the measurement will run until :meth:`stopMeasure`
        | acquisition time [ms]
        | will be ignored if device is a FileDevice
    waitFinished: bool (default: False)
        True: block execution until finished (will be False on acqTime = 0)
    savePTU: bool (default: False)
        Save data to ptu file

Returns
-------
    True: operation successful
    False: operation failed

Example
-------
::

    # calculates the g2 correlation of ptu file 
    sn = snAPI()
    sn.getDeviceIDs()
    sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    sn.correlation.setG2Parameters(1, 2, 1000, 200)
    sn.correlation.measure()

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getData()
    
    if sn.correlation.isFinished():
        break
        
        """
        
        if self.isFcs:
            self.numBins = self.numIntervals * self.intervalLength
            self.data = ct.ARRAY(ct.c_double, 2 * self.numBins)(0)
        else:
            self.numBins = 2 * self.intervalLength
            self.data = ct.ARRAY(ct.c_double, self.numBins)(0)
            
        self.bins = ct.ARRAY(ct.c_double, self.numBins)(0) 
        if(self.parent.deviceConfig["MeasMode"] == MeasMode.Histogram.value):
            self.parent.logPrint( "measurement is not supported for Correlation class in MeasMode:", MeasMode(self.parent.deviceConfig["MeasMode"]).name)
            return False
        
        return self.parent.dll.getCorrelation(acqTime, waitFinished, savePTU, ct.byref(self.data), ct.byref(self.bins), self.finished)


    def getG2Data(self):
        """
This function returns the data of the g(2) correlation measurement.

Parameters
----------
    none
    
Returns
-------
    tuple [1DArray, 1DArray]
        data: 1DArray[int]
            data array of the normalized g(2) measurement :eq:`g2factor`
        bins: 1DArray[int]
            data array of the start times of bins from the beginning of the measurement [s]

Example
-------
::

    # correlates the data from a file and plots the result
    ...
    sn = snAPI()
    sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    sn.correlation.setG2Parameters(1, 2, 1000, 200)
    sn.correlation.measure()

    while True:
        data, bins = sn.correlation.getG2data()
        if len(data) > 0:
            plt.clf()
            plt.plot(bins, data, linewidth=2.0, label='g(2)')
            plt.xlabel('Time [s]')
            plt.ylabel('g(2)')
            plt.legend()
            plt.title("g(2)")
            plt.pause(0.01)
        
        if sn.correlation.isFinished():
                break
                
    plt.show(block=True)
    
        """
        return self.data, self.bins


    def getFCSData(self):
        """
This function returns the data of the FCS correlation measurement.

Parameters
----------
    none
    
Returns
-------
    tuple [2DArray, 1DArray]
        data: 2DArray[int]
            data array of the FCS measurement. (A->B | B->A)
        bins: 1DArray[int]
            data array of the start times of the bins :eq:`multiTau`

Example
-------
::

    # FCS of the data from a file and plotting the result
    ...
    sn = snAPI()
    sn.getDeviceIDs()
    sn.getDevice()
    sn.getFileDevice(r"E:\Data\PicoQuant\CW_Shelved.ptu")
    sn.correlation.setFCSparameters(1, 1, 30, 16)
    sn.correlation.measure()

    while True:
        finished = sn.correlation.isFinished()
        data, bins = sn.correlation.getFCSdata()
        if len(data) > 0:
            plt.clf()
            plt.plot(bins, data[0], linewidth=2.0, label='AB')
            plt.plot(bins, data[1], linewidth=2.0, label='BA')
            plt.xlabel('Time [s]')
            plt.xscale('log')
            plt.ylabel('FCS')
            plt.legend()
            plt.title("FCS")
            plt.pause(0.01)
            
        if finished:
            break

    plt.show(block=True)    
    
        """
        return np.lib.stride_tricks.as_strided(self.data, shape=(2, self.numBins),
            strides=(ct.sizeof(self.data._type_) * self.numBins, ct.sizeof(self.data._type_)))[:, 4:], self.bins[4:]


    def stopMeasure(self):
        """
After a measurement is started it will normally be left running until the defined acquisition
time has elapsed. However, sometimes it may be necessary to stop a measurement manually with
this function.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._stopMeasure()
    

    def clearMeasure(self):
        """
Some measurements calculate their results on large sets of historical data. When conditions have changed,
the old data may need to be deleted to get a fresh view of the new data. This function deletes the internal 
data without having to restart the measurement.

Parameters
----------
    none
    
Returns
-------
    none
    
        """
        self.parent._clearMeasure()


    def isFinished(self):
        """
This function reports whether the measurement is finished.

Warning
-------
    If the measurement is finished, there might be some data available, which was not retrieved yet. It may be necessary to 
    call :meth:`getData()` or :meth:`getBlock()` once again after `isFinished` returns `True`.
    Check out the example of a possible implementation below.
    
Parameters
----------
    none

Returns
-------
    True: the measurement is finished
    False: the measurement is running

Example
-------
::

    # runs a while loop until the measurement is finished
        while sn.correlation.isFinished():
        data = sn.correlation.getData()
            ...
    
    # break a while loop if the measurement is finished and reads the last data 
        while True:
        finished = sn.correlation.isFinished()
        data = sn.correlation.getData()
            ...
            
        if finished:
            break
    
        """
        return self.finished.contents.value



class Manipulators():    
    """
This is the manipulators class. It can be used to modify the unfold data stream in snAPI. It it is
possible to modify existing channel records and/or create or delete new ones which are then added
to the data stream.

.. image:: _static/08_snAPI_Flow.png
    :width: 600px
    :class: only-light
    
.. image:: _static/08_snAPI_Flow_dark.png
    :width: 600px
    :class: only-dark
    

:figure-caption:`This figure shows the flow chart of the integration of the Manipulators.`

    """
    
    config = []
    """
Stores a list of the defined manipulators and can manually read with :meth:`getConfig`

Note
----
The Manipulator.config can not be written to. It is only for checking the current state. To change
the configuration, you have to call the specific functions directly.

Example
-------
::

    # example of a manipulator config

    {
    "ManisCfg": [
        {
        "Index": 0,
        "Type": "Herald",
        "Channels": [
            {
                "Channel": 5
            },
            {
                "Channel": 6
            }
            ]
        },
        {
            "Index": 1,
            "Type": "Coincidence",
            "Channels": [
            {
                "Channel": 7
            }
            ]
        },
        {
            "Index": 2,
            "Type": "Delay",
            "Channels": [
            {
                "Channel": 8
            }
            ]
        },
        {
            "Index": 3,
            "Type": "Coincidence",
            "Channels": [
            {
                "Channel": 9
            }
            ]
        }
    ]
    }
"""
    

    def __init__(self, parent):
        self.parent = parent
        self.config = []

    def getConfig(self):
        """
This command reads the manipulator configuration stored by th API and returns it to
:obj:`config`.

Note
----
    Normally you do not have to to call this function in order to refresh the manipulator.config.
    It should always be up to date. However, under certain circumstances it might be desired to
    update the manipulator.config manually.

Parameters
----------
    none
    
Returns
-------
    True:  operation successful
    False: operation failed
        
Example
-------
::
    
    # reads the manipulator config from the API 
    
    sn.manipulator.getConfig()
    
        """
        conf = (ct.c_char * 65535)()
        ok = self.parent.dll.getManisConfig(conf)
        conf = str(conf, "utf-8").replace('\x00','')
        if ok:
            self.config = json.loads(conf)
            return True
        else:
            self.parent.logPrint(conf)
            return False

    def clearAll(self):
        """
This clears all manipulators.

Warning
-------
    It is not allowed to clear the manipulators while acquisition is running!

        """
    
        self.parent.dll.clearManis()
        self.getConfig()

    def coincidence(self, chans: typing.List[int], windowTime: typing.Optional[float] = 1000, mode: typing.Optional[CoincidenceMode] = CoincidenceMode.CountAll, keepChannels: typing.Optional[bool] = True):
        """
This creates a coincidence manipulator. You have to define which channels should be part of the coincidence and its window size.

Note
----
    If only the coincidence channel is needed for further investigations set `keepChannels` to False.
    This will reduce the data stream and therefore the processor load and memory consumption.

.. image:: _static/04_Coincidence.png
    :width: 600px
    :class: only-light
    
.. image:: _static/04_Coincidence_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the principle of the Coincidence.`

Parameters
----------
    chans: List[int]
        channel indices that build a coincidence
    windowTime: float 
        window size [ps]
    mode: CoincidenceMode (default: CoincidenceMode.CountAll)
        coincidence counting mode
    keepChannels: bool (default: True)
        | True: the coincidence channel is be integrated in the data stream as an additional channel 
        | False: only the coincidence channel is in the data stream

Returns
-------
    int: 
        the channel index of the coincidence

Example
-------
::

    # plots a timetrace of channel 1 and 2 and their coincidence within a window time of 1ns 
    
    sn = snAPI()
    sn.getFileDevice(r"C:\Data\PicoQuant\default_1.ptu")

    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)

    ci = sn.manipulators.coincidence([1, 2], 1000)
    
    sn.timeTrace.measure(10000, False, False)

    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData() 
        plt.clf()
        plt.plot(times, counts[1], linewidth=2.0, label='chan1')
        plt.plot(times, counts[2], linewidth=2.0, label='chan2')
        plt.plot(times, counts[ci], linewidth=2.0, label='coincidence 1&2-1ns')

        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
    
        """

        length = len(chans)
        channels = (ct.c_int * length)()
        for i in range(length):
            channels[i] = chans[i]
        self.parent.dll.addMCoincidence.argtypes = [ct.c_void_p, ct.c_int, ct.c_double, ct.c_int, ct.c_bool]
        chanOut = self.parent.dll.addMCoincidence(ct.pointer(channels), length, windowTime, mode.value, keepChannels)
        self.getConfig()
        return chanOut
    
    
    def merge(self, chans: typing.List[int], keepChannels: typing.Optional[bool] = True):
        """
This manipulator combines the data steam of the specified channels. You only have to define
which channels should be merged.

Note
----
    If only the merged channel is needed for further investigations set `keepChannels` to False.
    This will reduce the data stream and therefore the processor load and memory consumption.

.. image:: _static/06_Merge.png
    :width: 600px
    :class: only-light
    
.. image:: _static/06_Merge_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the Merge operator principle.`

Parameters
----------
    chans: List[int]
        channel indices to be merged
    keepChannels: bool (default: True)
        | True: the merged channel is be integrated in the data stream as additional channel 
        | False: only the merged channel is in the data stream

Returns
-------
    int: 
        the merged channel index

Example
-------
::

    # the example looks like a coincidence example except the configuration of the manipulator
    # this would merge the channels 1 and 2
    
    cm = merge([1,2])
    
        """

        length = len(chans)
        channels = (ct.c_int * length)()
        for i in range(length):
            channels[i] = chans[i]
        chanOut = self.parent.dll.addMMerge(ct.pointer(channels), length, keepChannels)
        self.getConfig()
        return chanOut
    
    
    def delay(self, channel: int, delayTime: float, keepSourceChannel: typing.Optional[bool] = True):
        """
This manipulator, gives you the ability to add a delay to the specified channels. Its generally
better to use :meth:`setInputChannelOffset` because it does the same but on a hardware level and
therefore it doesn't uses any resources of the PC. But if you handle data of a ptu file this is
the only.

.. image:: _static/05_Delay.png
    :width: 600px
    :class: only-light
    
.. image:: _static/05_Delay_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the principle of the Delay operator.`

Note
----
    If you don't need the original channel anymore set `keepSourceChannel` to False.
    This will reduce the data stream and therefore the processor load and memory consumption.
    
Parameters
----------
    channel: int
        index of the channels, for which a coincidence will be calculated
    delayTime: int 
        window size [ps]
    keepSourceChannel: bool (default: True)
        | True: the delayed channel is being integrated in the data stream as an additional channel 
        | False: the source channel will be delayed

Returns
-------
    int: 
        the index of the channel to be delayed

Example
-------
::

    # creates a delay of channel 1 with 1ms and stores it in cd
    
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(10)

    cd = sn.manipulators.delay(1, 1000000000)
    
    sn.timeTrace.measure(10000, False, False)
    
    while True:
        finished = sn.timeTrace.isFinished()
        counts, times = sn.timeTrace.getData() 
        plt.clf()
        plt.plot(times, counts[1], linewidth=2.0, label='chan1')
        plt.plot(times, counts[cd], linewidth=2.0, label='delay 1ms')

        plt.xlabel('Time [s]')
        plt.ylabel('Counts[Cts/s]')
        plt.legend()
        plt.title("TimeTrace")
        plt.pause(0.1)
        
        if finished:
            break
    
    plt.show(block=True)
    
        """

        self.parent.dll.addMDelay.argtypes = [ct.c_int, ct.c_double, ct.c_bool]
        chanOut = self.parent.dll.addMDelay(channel, delayTime, keepSourceChannel)
        self.getConfig()
        return chanOut


    def herald(self, herald:int, gateChans: typing.List[int], delayTime: typing.Optional[int] = 0, gateTime: typing.Optional[int] = 1000, keepChannels: typing.Optional[bool] = True):
        """
This manipulator performs as heralded gate filter. You have to define from which channel the herald events
will be taken and which channels will be filtered. Therefore it is been necessary to set the delay time and
the gate time of the following gate accordingly.

.. image:: _static/07_Herald.png
    :width: 600px
    :class: only-light
        
.. image:: _static/07_Herald_dark.png
    :width: 600px
    :class: only-dark
    
:figure-caption:`This figure shows the principle of the Herald operator.`

Note
----
    If only the gated channels are needed for further investigations set `keepChannels` to False.
    This will reduce the data stream size and therefore the processor load and memory consumption.
    
Caution
-------
To calculate the histogram in :obj:`.MeasMode.T3` it is necessary to store `dTimes` (time difference
between the sync- and the channel events) in the internal unfold data stream, because the sync events
are removed. Therefore the herald manipulator only works in between to sync pulses. If you need the
default behaviour you have to use the :obj:`.MeasMode.T2` instead.

Parameters
----------
    herald:
        the channel that contains the herald events
    chans: List[int]
        channel numbers that should be gated
    delayTime: (default: 0ps)
        time between the herald event and the start of the gate
    gateTime: int (default: 1ns)
        size of the gate [ps]
    keepChannels: bool (default: True)
        | True: the gate channels are to be integrated in the data stream as additional channels
        | False: the gate channels are directly filtered

Returns
-------
    int: 
        the channel indices of the gated channels

Example
-------
::

    # sets a herald on sync channel that cuts of a window from 66ns to 76ns from channel 2
    
    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    waitFinished = False
    hChans = sn.manipulators.herald(0, [2], 66000, 10000, True)
    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(5)
    sn.histogram.measure(10000, False)
    
    while True:
        finished = sn.histogram.isFinished()
        data, bins = sn.histogram.getData()
        
        plt.clf()
        plt.plot(bins, data[2], linewidth=2.0, label='chan2')
        plt.plot(bins, data[hChans[0]], linewidth=2.0, label='heralded')
        plt.xlabel('Time [ps]')
        plt.xlim(67000, 73000) #set the scale range of the time scale to the region of interest
        plt.ylabel('Counts')
        plt.yscale('log')
        plt.legend()
        plt.title("Histogram")
        
        if waitFinished or finished:
            break
        
    plt.show(block=True)
    
        """

        length = len(gateChans)
        channels = (ct.c_int * length)()
        for i in range(length):
            channels[i] = gateChans[i]
        hChan = self.parent.dll.addMHerald(herald, ct.pointer(channels), len(channels), delayTime, gateTime, keepChannels)
        self.getConfig()
        return list(range(hChan, hChan + len(channels))) if keepChannels else gateChans
