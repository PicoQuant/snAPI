# Torsten Krause, PicoQuant GmbH, 2023

from enum import Enum, IntFlag, auto

class LibType(Enum):
    """
snAPI supports different library types / devices families. Which one is used has to be defined when creating a snAPI instance. 
    
    """

    Undefined = -1
    """
This is for internal use only. 
    
    """
    MH = 0
    """
This selects the library for
`MultiHarp 160 <https://www.picoquant.com/products/category/tcspc-and-time-tagging-modules/multiharp-160>`_
`MultiHarp 150 <https://www.picoquant.com/products/category/tcspc-and-time-tagging-modules/multiharp-150-high-throughput-multichannel-event-timer-tcspc-unit>`_
(MH150/160) devices.
    
    """
    HH = 1
    """
This selects the library for the
`HydraHarp 400 <https://www.picoquant.com/products/category/tcspc-and-time-tagging-modules/hydraharp-400-multichannel-picosecond-event-timer-tcspc-module>`_
(HH400) devices.
    
    """
    TH260 = 2
    """
This selects the library for the
`TimeHarp 260 <https://www.picoquant.com/products/category/tcspc-and-time-tagging-modules/timeharp-260-tcspc-and-mcs-board-with-pcie-interface>`_
(TH260) devices. 
There are two versions of the
`TimeHarp 260 <https://www.picoquant.com/products/category/tcspc-and-time-tagging-modules/timeharp-260-tcspc-and-mcs-board-with-pcie-interface>`_
. The PICO version (TH260P) has a resolution of 25 ps
and a deadtime of 25 ns whereas the NANO version (TH260N) provides a time resolution of 250 ps
with a deadtime below 2 ns.
    
    """
    PH330 = 3
    """
This selects the library for the
`PicoHarp 330 <https://www.picoquant.com/products/category/tcspc-and-time-tagging-modules/picoharp_330_precise_and_versatile_event_timer_and_tcspc_unit>`_
(PH330) devices.
    
    """

class DeviceType(Enum):
    """
The PicoQuant TCSPC devices can use their internal crystal clock but can be synchronized with an external
reference clock as well. The latter is preferable when a clock drift between multiple instruments in
an experiment needs to be avoided. The constants defined here specify the reference clock to use.
    """

    Undefined = -1
    """
This is for internal use only. 
    
    """
    HW = 0
    """
This is a real device, for instance a MultiHarp.
    
    """
    File = 1
    """
This is a file device. That means a ptu file treated as a device.
    
    """
    
class MeasMode(Enum):
    """
The PicoQuant TCSPC devices support different measurement modes. 
The constants defined here are specified by the measurement mode with which the device gets initialized
when using :meth:`snAPI.initDevice<snAPI.Main.snAPI.initDevice>`.

In histogram mode, the photon arrival time data is instantly processed to calculate the time differences 
between sync events and events on the input channels. These then get accumulated in a set of histograms,
one for each input channel. This is typically used for classic fluorescence lifetime measurements
and requires very little data processing effort by the user. As opposed to this, the time tagging 
modes T2 and T3 are designed to stream the raw photon arrival time data to the host PC where the data then
can be processed and analyzed. This allows more flexibility to facilitate a huge range of more advanced applications.
Data processing can be carried out directly "on the fly" while the measurement is running. Alternatively the data 
can be streamed to a file or PC memory and be processed later. The snAPI library supports both approaches.


    """

    Histogram = 0
    """
**Histogram Mode**

For the measurement class :class:`.Histogram` it is useful to initialize the device in Histogram mode.
For devices that support hardware histogramming this will enable higher count rates than software processing
of the raw stream of time tags.

Note
----
    In histogram  mode no data is written to disc because the raw data stream is processed internally and
    does not get transmitted to the API.

    
    """
    T2 = 2
    """
**T2 mode**

    .. image:: _static/T2_mode.jpg
        :class: p-2
    
    The T2 mode is PicoQuants time-tagging mode. In T2 mode, no periodic sync signal is required.
    The sync input can therefore be used to connect an additional photon detector. T2 mode is often
    used for any kind of coincidence detection, such as coincidence counting and correlation for,
    e.g., antibunching in a HBT set-up. Two pieces of information are collected for each event:
    
    • The elapsed time since the start of the measurement
    • The channel at which the event has been detected
    
    """

    T3 = 3
    """
**T3 Mode**

.. image:: _static/T3_mode.jpg
    :class: p-2

The T3 mode is an elegant solution for performing measurements at very high synchronization rates
and can provide more effective data encoding for many applications. This mode is ideally suited
for luminescence lifetime imaging and fluorescence correlation spectroscopy. Three different pieces
of information are recorded for each detected event:

• The start-stop time difference (similar to classic  TCSPC)
• The number of elapsed sync pulses since measure ment start
• The channel at which the event has been detected
    
    """

class MeasControl(Enum):
    """this constant is for software or hardware starting and stopping (triggered) measurements in :meth:`Device.setMeasControl<snAPI.Main.Device.setMeasControl>`."""

    SingleShotCTC = 0
    """
    
Supported devices [MH150/160 | HH400 | TH260 | PH330]
        
Acquisition starts by software command and runs until CTC expires. The duration is set by the
aqcTime parameter (>0).
    
    """
    
    C1Gated = 1
    """
Supported devices [MH150/160 | HH400 | TH260 | PH330]

Data is collected for the period where C1 is active. This can be the logical high or low period
dependent on the value supplied to the parameter startEdge.
    
    """
    
    C1StartCtcStop = 2
    """
Supported devices [MH150/160 | HH400 | TH260 | PH330]

Data collection is started by a transition on C1 and stopped by expiration of the internal CTC.
Which transition actually triggers the start is given by the value supplied to the parameter startEdge.
The duration is set by the aqcTime parameter (>0).
    
    """
    
    C1StartC2Stop = 3
    """
Supported devices [MH150/160 | HH400 | TH260 | PH330]

Data collection is started by a transition on C1 and stopped by by a transition on C2. Which transitions
actually trigger start and stop is given by the values supplied to the parameters startEdge and stopEdge."""
    
    WrM2S = 4
    """
Supported devices [MH150/160]

White Rabbit master to slave (for further use)
    
    """
    
    WrS2M = 5
    """
Supported devices [MH150/160]

White Rabbit slave to master (for further use)
    
    """
    
    SwStartSwStop = 6
    """
Supported devices [MH150/160 | PH330]

Software Start and Software Stop is in use if aqcTime parameter is 0.
    
    """
    
    ContC1Gated = 7
    """
Supported devices [HH400]

Software Start and Software Stop is in use if aqcTime parameter is 0.
    
    """
    
    Cont_C1_Start_CTC_Stop = 8
    """
Supported devices [HH400]

Software Start and Software Stop is in use if aqcTime parameter is 0.
    
    """
	
    Cont_CTC_Restart = 9
    """
Supported devices [HH400]

Software Start and Software Stop is in use if aqcTime parameter is 0.
    
    """
    
class RefSource(Enum):
    """
PicoQuant TCSPC devices can use their internal crystal clock but can be synchronized with an external
reference clock as well. The latter is preferable when a clock drift between multiple instruments in
an experiment needs to be avoided. The constants defined here specify the reference clock to use.
    """

    Internal = 0
    """
Supported devices [MH150/160 | HH400 | (TH260) | PH330]
    
| **Internal clock**
| This is the default and normally selected by most users when only one device is being used. 

    """
    External_10MHZ = 1
    """
Supported devices [MH150/160 | HH400 | PH330]
        
| **10MHz external clock**
| This is for use with an industry standard 10MHz reference such as an atomic clock or another Harp.
    
    """
    Wr_Master_Generic = 2
    """
Supported devices [MH150/160]
        
**White Rabbit master with generic partner**
    
    """
    Wr_Slave_Generic = 3
    """
Supported devices [MH150/160]
        
**White Rabbit slave with generic partner**
    
    """
    Wr_Grandm_Generic = 4
    """
Supported devices [MH150/160]
        
**White Rabbit grand master with generic partner**
    
    """
    Extn_GPS_PPS = 5
    """
Supported devices [MH150/160]
        
**10 MHz + PPS from GPS**
    
    """
    Extn_GPS_PPS_UART = 6
    """
Supported devices [MH150/160]
        
**10 MHz + PPS + time via UART from GPS**
    
    """
    Wr_Master_Mharp = 7
    """
Supported devices [MH150/160]
        
**White Rabbit master with the Harp as partner**
    
    """
    Wr_Slave_Mharp = 8
    """
Supported devices [MH150/160]
        
**White Rabbit slave with the Harp as partner**
    
    """
    Wr_Grandm_Mharp = 9
    """
Supported devices [MH150/160]

**White Rabbit grand master with the Harp as partner**
    
    """
    External_100MHZ = 10
    """
Supported devices [PH330]
        
| **100MHz external clock**
    
    """
    External_500MHZ = 11
    """
Supported devices [PH330]
        
| **500MHz external clock**
    
    """
class TrigMode(Enum):
    """
The PicoQuant TCSPC devices have different trigger modes. Some of them can switch between them. 
    
    """
    Edge = 0
    """
This selects the edge trigger.
    
    """
    CFD = 1
    """
This selects the CFD (Constant Fraction Discriminator) trigger
    
    """

class LogLevel(Enum):
    """
This is for switching the different log levels on and off with :meth:`snAPI.setLogLevel()<snAPI.Main.snAPI.setLogLevel>`. 

    """
    Api = 0
    """
This logs API commands.

    """
    Config = 1
    """
This logs the loading of :meth:`snAPI.setIniConfig<snAPI.Main.snAPI.setIniConfig>` and notifies you, if something goes wrong.

    """
    Device = 2
    """
This logs the low level device commands :class:`.Device`.

    """
    DataFile = 3
    """
This logs loading and creating of th ptu file entries.

    """
    Manipulators = 4
    """
This logs the creating, deleting and many more of the :class:`.Manipulators`.

    """
    
class CoincidenceMode(Enum):
    """
This defines the different coincidence modes.

    """
    CountAll = 0
    """
This is the standard mode. Every new event can count as coincidence if it meets the conditions of the different channel count in the defined window time.

    """
    CountOnce = 1
    """
This mode allows to count every new event only one time. If count it meets the conditions of the different channel count in the defined window time it will
generate a coincidence count and get erased for the generation of further coincidences.

    """
    
class UnfoldFormat(Enum):
    """
This changes the format of the `Unfold` data stream in :obj:`.MeasMode.T3`.
    """
    Nothing = 0
    """
This is for internal use only. 
    """
    Absolute = 1
    """
This value will generate absolute times.
    """
    DTimes = 2
    """
This generates only `dTimes` (differential time between sync and input channel).
    """
    DTimesSyncCntr = 3
    """
This generates `dTimes` (differential time between sync and input channel) and
`syncCntr` (sync counter).
    """