# Torsten Krause, PicoQuant GmbH, 2023

from enum import Enum, IntFlag, auto

class LibType(Enum):
    """
snAPI provides different library types / devices families. This has to be defined at crating the snAPI instance. 
    
    """

    Undefined = -1
    """
This is for internal use only. 
    
    """
    MH = 0
    """
This selects the library for MultiHarp 150/160 (MH150/160) devices.
    
    """
    HH = 1
    """
This selects the library for the HydraHarp 400 (HH400) devices.
    
    """

class DeviceType(Enum):
    """
The Harp devices can use their internal crystal clock but alternatively they can be synchronized
to an external reference clock. The latter is important when clock drift between multiple instruments in
an experiment must be avoided. The constants defined here specify the reference clock to use.
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
The constants defined here specify the measurement mode the device gets initialized for with :meth:`snAPI.initDevice<snAPI.Main.snAPI.initDevice>`.

In histogram mode, the photon arrival time data is instantly processed to calculate the time differences 
between sync events and events on the input channels. These get then accumulated in a set of histograms,
one for each input channel. This is typically used for classic fluorescence lifetime measurements with
TCSPC and requires very little data processing effort by the user. As opposed to this, the time tagging 
modes T2 and T3 are designed to stream the raw photon arrival time data to the host PC where the data
can be processed and analyzed with ultimate flexibility for a huge range of more advanced applications.
This processing can be carried out "on the fly" while the measurement is running, alternatively the data 
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
    
    In T2 mode all timing inputs and the sync input are functionally identical. There is no dedication
    of the sync input channel to a sync signal from a laser. It may be left unconnected or can be used
    for an additional detector signal. Usually all regular inputs are used to connect photon detectors.
    The events from all channels are recorded independently and treated equally. In each case an event
    record is generated that contains information about the channel it came from and the arrival time
    of the event with respect to the overall measurement start. The timing is recorded with the highest
    resolution the hardware supports. 
    Dead-times exist only within each channel but not across the channels.
    
    """

    T3 = 3
    """
**T3 Mode**

.. image:: _static/T3_mode.jpg
    :class: p-2

In T3 mode the sync input is dedicated to a periodic sync signal, typically from a laser. As far as
the experimental setup is concerned, this is similar to histogram mode. The main objective is to
allow high sync rates which could not be handled in T2 mode due to deadtime and USB bandwith limits. 
Accommodating the high sync rates in T3 mode is achieved as follows: 
First, a sync divider is employed (as in histogram mode). 
This reduces the sync rate so that the channel dead-time is no longer a problem. The remaining
problem is that even with the divider the sync rate may still be too high for collecting all
individual sync events like ordinary T2 mode events. Considering that sync events are not of primary
interest, the solution is to record them only if they arrive in the context of a photon event on any
of the input channels. The event record is then composed of two timing figures:

- the start stop timing difference between the photon event and the last sync event, and
- the arrival time of the event pair on the overall experiment time scale (the time tag).

The latter is obtained by simply counting sync pulses. From the T3 mode event records it is therefore
possible to precisely determine which sync period a photon event belongs to. Since the sync period
is also known precisely, this furthermore allows to reconstruct the arrival time of the photon with
respect to the overall experiment time.
    
    """

class MeasControl(Enum):
    """this constant is for software or hardware starting and stopping (triggered) measurements in :meth:`Device.setMeasControl<snAPI.Main.Device.setMeasControl>`."""

    SingleShotCTC = 0
    """
    
Supported devices [MH150/160 | HH400]
        
Acquisition starts by software command and runs until CTC expires. The duration is set by the
aqcTime parameter (>0).
    
    """
    
    C1Gated = 1
    """
Supported devices [MH150/160 | HH400]

Data is collected for the period where C1 is active. This can be the logical high or low period
dependent on the value supplied to the parameter startEdge.
    
    """
    
    C1StartCtcStop = 2
    """
Supported devices [MH150/160 | HH400]

Data collection is started by a transition on C1 and stopped by expiration of the internal CTC.
Which transition actually triggers the start is given by the value supplied to the parameter startEdge.
The duration is set by the aqcTime parameter (>0).
    
    """
    
    C1StartC2Stop = 3
    """
Supported devices [MH150/160 | HH400]

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
Supported devices [MH150/160]

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
The Harp devices can use their internal crystal clock but alternatively they can be synchronized
to an external reference clock. The latter is important when clock drift between multiple instruments in
an experiment must be avoided. The constants defined here specify the reference clock to use.

    """

    Internal = 0
    """
Supported devices [MH150/160]
    
| **Internal clock**
| This is the default and normally what most users would select when only one device is being used. 

    """
    External_10MHZ = 1
    """
Supported devices [MH150/160 | HH400]
        
| **(10MHz) external clock**
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
    Wr_Salve_Mharp = 8
    """
Supported devices [MH150/160]
        
**White Rabbit slave with the Harp as partner**
    
    """
    Wr_Grandm_Mharp = 9
    """
Supported devices [MH150/160]

**White Rabbit grand master with the Harp as partner**
    
    """
