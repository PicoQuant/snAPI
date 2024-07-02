.. role:: fwLighter
    :class: fw-lighter


Configuration
#############

The :obj:`.deviceConfig` stores the state of the device in the API and can be updated with :meth:`.getDeviceConfig`.
From :obj:`.deviceConfig` the parameters can only be read. To set them you need to call :meth:`.loadIniConfig` or :meth:`.setIniConfig`.
An other and more pythonesque way to change them is to use the commands defined in the :class:`.Device` directly.
This document will give you an overview about the configuration parameters and there corresponding functions or constants,
where their values and/or their maximum and minimum are defined.

.. note::
    If you encounter any issues reading a config.ini file enable the config log level in the system.ini. The file location 
    is shown at the firs log entry: 'loadSettingsIni: e:\\path\\to\\system.ini'.


Parameter Description
*********************

Read only parameters
====================

.. list-table:: Read only from :obj:`.deviceConfig` (can't be set via :meth:`.loadIniConfig` or :meth:`.setIniConfig`)
    :widths: 25 25 50
    :header-rows: 1

    *   - Name
        - Object / Reference
        - Description 

    *   - DeviceType
        - :obj:`.DeviceType`
        - real Hardware or File Device

    *   - FileDevicePath
        - string
        - path to the ptu file

    *   - ID
        - string
        - serial number

    *   - Index
        - int
        - index number of the device in the list of :obj:`.deviceIDs` (only valid after :meth:`.getDeviceIDs`)

    *   - Model
        - string
        - model name

    *   - PartNo
        - string
        - part number

    *   - Version
        - string
        - version number
        
    *   - BaseResolution
        - double
        - base resolution in ps (timing resolution in T2 mode)
        
    *   - Resolution
        - double
        - current resolution (histogram bin width) in ps (not meaningful in T2 mode)
        
    *   - Binning
        - int
        - current binning code (multiplier for BaseResolution) - (not meaningful in T2 mode)
        
    *   - NumChans
        - int
        - number of input channels (without sync)
        
    *   - NumMods
        - int
        - number of installed modules
        
    *   - MeasMode
        - :obj:`.MeasMode`
        - Histogram, T2, T3

    *   - RefSource
        - :obj:`.RefSource`
        - source of the reference clock


INI Device Section
==================

.. list-table:: INI Section: [Device]
    :widths: 25 25 50
    :header-rows: 1

    *   - Name
        - Object / Reference
        - Description

    *   - SyncDivider
        - :meth:`.setSyncDiv`
        - sync rate divider

    *   - SyncTrigMode
        - :meth:`.setSyncTrigMode`
        - `Edge` or `CFD` trigger

    *   - SyncEdgeTrig, SyncTrigLvl , SyncTrigEdge
        - :meth:`.setSyncEdgeTrig`
        - sets both parameters at once: trigger level and edge

    *   - SyncCFD, SyncDiscrLvl , SyncZeroXLvL
        - :meth:`.setSyncCFD`
        - sets both parameters at once: discriminator- and zero cross level

    *   - SyncChannelOffset
        - :meth:`.setSyncChannelOffset`
        - sync timing offset in ps

    *   - SyncChannelEnable
        - :meth:`.setSyncChannelEnable`
        - enable state of the sync channel

    *   - SyncDeadTime
        - :meth:`.setSyncDeadTime`
        - dead-time in ps

    *   - HystCode
        - :meth:`.setInputHysteresis`
        - input hysteresis

    *   - StopCount
        - :meth:`.setStopOverflow`
        - stop count for histogram 

    *   - Binning
        - :meth:`.setBinning`
        - binning factor

    *   - Offset
        - :meth:`.setOffset`
        - histogram time offset in ns

    *   - LengthCode, NumBins
        - :meth:`.setHistoLength`
        - number of bins

    *   - TriggerOutput
        - :meth:`.setTriggerOutput`
        - programmable trigger output period in ns

    *   - MarkerHoldoffTime
        - :meth:`.setMarkerHoldoffTime`
        - marker hold of time to remove glitches in ns

    *   - HoldTime
        - :meth:`.setOflCompression`
        - low data rates


INI Channel Section
===================

.. list-table:: INI Section: [All_Channels] | [Channel_N]
    :widths: 25 25 50
    :header-rows: 1

    *   - Name
        - Object / Reference
        - Description

    *   - TrigMode
        - :meth:`.setInputTrigMode`
        - `Edge` or `CFD` trigger

    *   - EdgeTrig, TrigLvl , TrigEdge
        - :meth:`.setInputEdgeTrig` 
        - sets both values at once: trigger level and edge

    *   - CFD, DiscrLvl , ZeroXLvl
        - :meth:`.setInputCFD` 
        - sets both values at once: discriminator- and zero cross level

    *   - ChanOffs
        - :meth:`.setInputChannelOffset`
        - input channel offset timing offset in ps

    *   - ChanEna
        - :meth:`.setInputChannelEnable`
        - enable state of the input channel

    *   - DeadTime
        - :meth:`.setInputDeadTime`
        - dead-time in ps


Example of the :obj:`.deviceConfig`
===================================
::

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
    "MeasControl": 0,
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
    
Example of the device ini file
==============================
::

    [Device]
    HystCode = 0
    SyncDiv = 1
    SyncEdgeTrig = -50,1
    SyncChannelOffset = 0
    SyncChannelEnable = 1
    SyncDeadTime = 0
    StopOverflow = 4294967295
    Binning = 1
    Offset = 0
    MeasControl = 0
    StartEdge = 1
    StopEdge = 1
    TriggerOutput = 0

    [All_Channels]
    InputEdgeTrig = -50,1
    InputChannelOffset = 0
    SetInputChannelEnable = 1
    InputDeadTime = 0

    [Channel_0]
    InputEdgeTrig = -10,1
    InputChannelOffset = 100

    [Channel_1]
    InputEdgeTrig = -120,1
