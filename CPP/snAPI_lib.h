#ifndef _WIN32
#define _stdcall
#endif
#include "snapi.h"

/********** snAPI **********/
extern bool _stdcall initAPI(char* systemIni);
extern void _stdcall exitAPI();
extern void _stdcall setLogLevel(int logLevel, bool onOff);
extern void _stdcall logExternal(char* message);
extern void _stdcall logError(char* message);
extern bool _stdcall getDeviceIDs(char* names);
extern bool _stdcall getDevice(char* name);
extern void _stdcall closeDevice(bool all);
extern bool _stdcall getFileDevice(char* path);
extern bool _stdcall initDevice(int mode, int refsource);
extern bool _stdcall loadIniConfig(char* fileName);
extern void _stdcall setPTUFilePath(char* filePath);
extern void _stdcall setIniConfig(char* iniData);
extern int _stdcall getDeviceConfig(char* conf);
extern int _stdcall getManisConfig(char* conf);
extern int _stdcall getMeasDescription(char* conf);

/********** Device **********/
extern bool _stdcall setInputHysteresis(int hystCode);
extern bool _stdcall setTimingMode(int timingMode);
extern bool _stdcall setStopOverflow(unsigned int stopCount);
extern bool _stdcall setBinning(int binning);
extern bool _stdcall setOffset(int offset);
extern bool _stdcall setHistoLength(int lengthCode);
extern bool _stdcall clearHistMem();
extern bool _stdcall setMeasControl(int measControl, int startEdge, int stopEdge);
extern bool _stdcall setTriggerOutput(int trigOutput);

// Sync
extern bool _stdcall setSyncDiv(int div);
extern bool _stdcall setSyncTrigMode(int syncTrigMode);
extern bool _stdcall setSyncEdgeTrig(int trigLvlSync, int trigEdgeSync);
extern bool _stdcall setSyncCFD(int discrLvlSync, int zeroXLvlSync);
extern bool _stdcall setSyncChannelOffset(int syncChannelOffset);
extern bool _stdcall setSyncChannelEnable(int syncChannelEnable);
extern bool _stdcall setSyncDeadTime(int syncChannelEnable);

// Channel
extern bool _stdcall setInputTrigMode(int iChan, int trigMode);
extern bool _stdcall setInputEdgeTrig(int iChan, int trigLvl, int trigEdge);
extern bool _stdcall setInputCFD(int iChan, int discrLvl, int zeroXLvl);
extern bool _stdcall setInputChannelOffset(int iChan, int chanOffs);
extern bool _stdcall setInputChannelEnable(int iChan, int chanEna);
extern bool _stdcall setInputDeadTime(int iChan, int deadTime);

/********** Measurements **********/
extern void _stdcall getCountRates(int* syncRate, int* cntRates);
extern void _stdcall getSyncPeriod(double* syncPeriod);
extern bool _stdcall getHistogram(int tAcq, bool waitFinished, bool savePTU, unsigned int* data, bool* finished);
extern void _stdcall setHistoT2RefChan(uint8_t iChan);
extern void _stdcall setHistoT2BinWidth(uint64_t numBins);
extern void _stdcall setHistoT2NumBins(uint64_t numBins);
extern bool _stdcall getTimeTrace(int tAcq, bool waitFinished, bool savePTU, unsigned int* data, uint64_t* t0, bool* finished);
extern void _stdcall setTimeTraceNumBins(int numBins);
extern void _stdcall setTimeTraceHistorySize(double historySize);
extern void _stdcall setG2Params(uint64_t startChannel, uint64_t clickChannel, double windowSize, double binWidth);
extern void _stdcall setFCSParams(uint64_t startChannel, uint64_t clickChannel, uint64_t* numTaus, double startTime, double stopTime, uint64_t numBins);
extern void _stdcall setFFCSParams(uint64_t startChannel, uint64_t clickChannel, uint64_t* numTaus, double startTime, double stopTime, uint64_t numBins);
extern bool _stdcall getCorrelation(int tAcq, bool waitFinished, bool savePTU, double* data, double* bins, bool* finished);
extern bool _stdcall rawMeasure(int tAcq, bool waitFinished, bool savePTU, unsigned int* data, unsigned long long* dataIdx, unsigned long long dataSize, bool* finished);
extern bool _stdcall rawStartBlock(int tAcq, bool savePTU, unsigned int* data, unsigned long long dataSize, bool* finished);
extern bool _stdcall rawGetBlock(unsigned int* data, unsigned long long* size);
extern bool _stdcall stopMeasure();
extern bool _stdcall clearMeasure();
extern bool _stdcall ufMeasure(int tAcq, bool waitFinished, bool savePTU, unsigned long long* times, unsigned char* chans, unsigned long long* idx, unsigned long long dataSize, bool* finished);
extern bool _stdcall ufStartBlock(int tAcq, bool savePTU, unsigned long long* time, unsigned char* chan, unsigned long long dataSize, bool* finished);
extern bool _stdcall ufGetBlock(uint64_t* times, unsigned char* chans, unsigned long long* size);
extern bool _stdcall getTimesFromChannelUF(unsigned char* channels, uint64_t* times, uint64_t* timesOut, int channel, size_t* size);

/********** Manipulators **********/
extern int _stdcall getNumAllChans(void);
extern void _stdcall clearManis(void);
extern int _stdcall addMCoincidence(int* chans, int numChans, double windowTime, int mode, int time, bool keepChannels);
extern int _stdcall addMMerge(int* chans, int numChans, bool keepChannels);
extern int _stdcall addMDelay(int chan, double delayTime, bool keepChannel);
extern int _stdcall addMHerald(uint8_t herald, int* chans, int32_t numChans, int32_t delayTime, int32_t windowTime, bool inverted, bool keepChannels);
extern int _stdcall addMCountRate(double windowTime);
extern bool _stdcall getMCountRates(int manisIdx, int* countRatess);

/********** Marker **********/
extern bool _stdcall setMarkerEdges(int edge1, int edge2, int edge3, int edge4);
extern bool _stdcall setMarkerEnable(int ena1, int ena2, int ena3, int ena4);
extern bool _stdcall setMarkerHoldoffTime(int holdofftime);
extern bool _stdcall setOflCompression(int holdtime);

/********** HW-Filter **********/
extern bool _stdcall setRowEventFilter(int iRow, int timeRange, int matchCount, bool inverse, int useChans, int passChans);
extern bool _stdcall enableRowEventFilter(int iRow, bool enable);
extern bool _stdcall setMainEventFilterParams(int timeRange, int matchCount, bool inverse);
extern bool _stdcall setMainEventFilterChannels(int iRow, int useChans, int passChans);
extern bool _stdcall enableMainEventFilter(bool enable);
extern bool _stdcall setFilterTestMode(bool testMode);
extern bool _stdcall getRowFilteredRates(int* syncRate, int* countRates);
extern bool _stdcall getMainFilteredRates(int* syncRate, int* countRates);

/********** White Rabbit **********/
extern bool _stdcall WRabbitGetMAC(char* macAddr);
extern bool _stdcall WRabbitSetMAC(char* macAddr);
extern bool _stdcall WRabbitGetInitScript(char* script);
extern bool _stdcall WRabbitSetInitScript(char* script);
extern bool _stdcall WRabbitGetSFPData(char* sfpNames, int* dTxs, int* dRxs, int* alphas);
extern bool _stdcall WRabbitSetSFPData(char* sfpNames, int* dTxs, int* dRxs, int* alphas);
extern bool _stdcall WRabbitSetMode(int bootFromScript, int reinitWithMode, int mode);
extern bool _stdcall WRabbitSetTime(uint64_t time);
extern bool _stdcall WRabbitGetTime(uint64_t* time, uint32_t* subSec16ns);
extern bool _stdcall WRabbitGetStatus(uint32_t* status);
extern bool _stdcall WRabbitGetTermOutput(char* termOutput);
extern bool _stdcall WRabbitInitLink(int onOff);