TTTR Record Format
==================

Basic record format
---------------------

This page describes the format of the TTTR data named as raw data in ptu files.

Due to performance reasons the TTTR data are saved exactly as received from TCSPC device, hence the format of the TTTR records depends on the kind of TCSPC device and the type of measurement. The record format used in a particular file is denoted in the mandatory tag TTResultFormat_TTTRRecType.

Even though the record formats differ, the formal algorithms for the calculations on them don't: To get the global arrival time of a photon or a marker in seconds, count the overflows until the current position and multiply with the overflow period, then add the timetag (for T2) or nSync (for T3) and multiply with the MeasDesc_GlobalResolution.

The arrival time since the last sync event in T3 measurements is denoted in dTime. To get the time in seconds multiply dTime with MeasDesc_Resolution.

Images
""""""
(all Formats)
To reconstruct the image one needs marker defined as a line start, line stop and frame trigger. The corresponding header entries are ImgHdr_LineStart, ImgHdr_LineStop and ImgHdr_Frame. The line start and line stop markers mark the real start and stop of image line, a frame marker define a change of the frame.

The default setting is a linear movement of the scanner between line start and line stop marker, the length of one pixel in this case is given by the length of line (arrival time of line stop marker - arrival time of line start marker) divided by the number of pixels in the line.
Some scanner have a sinusoidal movement, such files have the header entry ImgHdr_SinCorrection which defines the percentage of a sinus curve is covered by the line and must be used to calculate the length of every pixel.
The number of pixels in a line is defined by ImgHdr_PixX. The number of lines is given by ImgHdr_PixY. Attention, in some images one will find a different number of lines than defined by PixY (less or more, even different in every frame), so do not trust this value.
Notice 1: The markers are bit coded in the TTTR records (see below), multiple markers can appear at once; Especially the frame marker often overlay with a line start or line stop marker.
Notice 2: The marker positions in MicroTime200 images are different than before in the SymPhoTime 32. When a MicroTime200 image is converted for the new software the markers are relocated to match the real line start, line stop position.

TCSPC specific record formats
-----------------------------

Currently the following formats are defined:

| PicoHarp T3: 0x00010303
| PicoHarp T2: 0x00010203
| HydraHarp V1.x T3: 0x00010304
| HydraHarp V1.x T2: 0x00010204
| HydraHarp V2.x T3: 0x01010304
| HydraHarp V2.x T2: 0x01010204
| TimeHarp 260N T2: 0x00010205
| TimeHarp 260N T3: 0x00010305
| TimeHarp 260P T2: 0x00010206
| TimeHarp 260P T3: 0x00010306
| MultiHarp T2: 0x00010207
| MultiHarp T3: 0x00010307

HydraHarp, MultiHarp and TimeHarp260 T2 Format
""""""""""""""""""""""""""""""""""""""""""""""

| RecType: 0x00010204 (not supported)
| Overflow period: 33552000  (0x1FFF680)
| Record Size: 32 Bit = 4 Byte

| RecTypes:	0x01010204, 0x01010205, 0x01010206, 0x01010207
| Overflow period: 33554432 (0x2000000)
| Record Size: 32 Bit = 4 Byte

The bit allocation in the record is, starting from the MSB:

- special: 1
- channel: 6
- timetag: 25

If the special bit is clear, it's a regular event record.
If the special bit is set, the following interpretation of the channel code is given:

channel code 63 (0x3F) identifies a timetag overflow, increment the overflow timetag accumulator. For HydraHarp V1 (0x00010204) it always means one overflow. For all other types the number of overflows can be read from timetag value.
channel code 0 (0x00) identifies a sync event,
channel codes from 1 to 15 (4 bit = 4 marker) identify markers, the individual bits are external markers.

HydraHarp, MultiHarp and TimeHarp260 T3 Format
""""""""""""""""""""""""""""""""""""""""""""""

| RecType: 0x00010304, 0x01010304, 0x00010305, 0x00010306, 0x00010307
| Overflow period: 1024
| Record Size: 32 Bit = 4 Byte

The bit allocation in the record is, starting from the MSB:

- special: 1
- channel: 6
- dTime: 15
- nSync: 10

If the special bit is clear, it's a regular event record.
If the special bit is set, the following interpretation of the channel code is given:
channel code 63 (0x3F) identifies a sync count overflow, increment the sync count overflow accumulator.
For HydraHarp V1 (0x00010304) it means always one overflow. For all other types the number of overflows can be read from nSync value.
channel codes from 1 to 15 (4 bit = 4 marker) identify markers, the individual bits are external markers.

PicoHarp T2 Format (not supported)
""""""""""""""""""""""""""""""""""

| RecType: 0x00010203
| Overflow period: 210698240 (0xC8F0000)
| Record Size: 32 Bit = 4 Byte

The bit allocation in the record is, starting from the MSB:

- channel: 4
- timetag: 28

The channel code 15 (0xF) marks a special record.
Special records can be overflows or external markers. To differentiate this, the lower 4 bits of timetag must be checked.

If they are all zero, the record marks an overflow.
If they are >=1 the individual bits are external markers.

PicoHarp T3 Format (not supported)
""""""""""""""""""""""""""""""""""

| RecType: 0x00010303
| Overflow period: 65536 (0x10000)
| Record Size: 32 Bit = 4 Byte

The bit allocation in the record is, starting from the MSB:

- channel: 4
- dTime: 12
- nSync: 16

The channel code 15 (0xF) marks a special record.
Special records can be overflows or external markers. To differentiate this, dTime must be checked.

If it is zero, the record marks an overflow.
If it is >=1 the individual bits are external markers.