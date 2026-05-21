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
extern void _stdcall setMeasSubMode(int32_t val);
extern void _stdcall addBoolTag(char* name, bool val, int32_t idx);
extern void _stdcall addIntTag(char* name, int64_t val, int32_t idx);
extern void _stdcall addDblTag(char* name, double val, int32_t idx);
extern void _stdcall addStringTag(char* name, char* val, int32_t idx);
extern void _stdcall addWStringTag(char* name, wchar_t* val, int32_t idx);
extern void _stdcall addBBTag(char* name, int64_t* val, int numVals, int32_t idx);
extern void _stdcall addFloatArrayTag(char* name, double* val, int numVals, int32_t idx);
extern void _stdcall clearTags();
extern void _stdcall setIniConfig(char* iniData);
extern int _stdcall getDeviceConfig(char* conf);
extern int _stdcall getManisConfig(const wchar_t* ID, char* conf);
extern int _stdcall getMeasDescription(char* conf);

/********** Device **********/
extern bool _stdcall setInputHysteresis(const wchar_t* ID, int hystCode);
extern bool _stdcall setTimingMode(const wchar_t* ID, int timingMode);
extern bool _stdcall setStopOverflow(const wchar_t* ID, unsigned int stopCount);
extern bool _stdcall setBinning(const wchar_t* ID, int binning);
extern bool _stdcall setOffset(const wchar_t* ID, int offset);
extern bool _stdcall setHistoLength(const wchar_t* ID, int lengthCode);
extern bool _stdcall clearHistMem(const wchar_t* ID);
extern bool _stdcall setMeasControl(const wchar_t* ID, int measControl, int startEdge, int stopEdge);
extern bool _stdcall setTriggerOutput(const wchar_t* ID, int trigOutput);

// Sync
extern bool _stdcall setSyncDiv(const wchar_t* ID, int div);
extern bool _stdcall setSyncTrigMode(const wchar_t* ID, int syncTrigMode);
extern bool _stdcall setSyncEdgeTrig(const wchar_t* ID, int trigLvlSync, int trigEdgeSync);
extern bool _stdcall setSyncCFD(const wchar_t* ID, int discrLvlSync, int zeroXLvlSync);
extern bool _stdcall setSyncChannelOffset(const wchar_t* ID, int syncChannelOffset);
extern bool _stdcall setSyncChannelEnable(const wchar_t* ID, int syncChannelEnable);
extern bool _stdcall setSyncDeadTime(const wchar_t* ID, int syncChannelEnable);

// Channel
extern bool _stdcall setInputTrigMode(const wchar_t* ID, int iChan, int trigMode);
extern bool _stdcall setInputEdgeTrig(const wchar_t* ID, int iChan, int trigLvl, int trigEdge);
extern bool _stdcall setInputCFD(const wchar_t* ID, int iChan, int discrLvl, int zeroXLvl);
extern bool _stdcall setInputChannelOffset(const wchar_t* ID, int iChan, int chanOffs);
extern bool _stdcall setInputChannelEnable(const wchar_t* ID, int iChan, int chanEna);
extern bool _stdcall setInputDeadTime(const wchar_t* ID, int iChan, int deadTime);

/********** Measurements **********/
extern void _stdcall getCountRates(int* syncRate, int* cntRates);
extern void _stdcall getSyncPeriod(double* syncPeriod);
extern void _stdcall setSequenceMode(int mode, bool wait4newData, double param);
extern bool _stdcall waitNewData(const wchar_t* ID);
extern bool _stdcall gotNewData(const wchar_t* ID);
extern bool _stdcall getHistogram(int tAcq, bool waitFinished, bool savePTU, unsigned int* data, bool* finished);
extern void _stdcall setHistoT2RefChan(const wchar_t* ID, uint8_t iChan);
extern void _stdcall setHistoT2BinWidth(const wchar_t* ID, uint64_t binWidth);
extern void _stdcall setHistoT2NumBins(const wchar_t* ID, uint64_t numBins);
extern void _stdcall setHisto2dParams(const wchar_t* ID, uint64_t refChannel, uint64_t channelX, uint64_t channelY, uint64_t offsetX, uint64_t offsetY, uint64_t binWidthX, uint64_t binWidthY, uint64_t numBinsX, uint64_t numBinsY);
extern void _stdcall setHisto2dTotMode(const wchar_t* ID, bool totMode, double timewalkFactor);
extern void _stdcall setHisto2dRecoveryTimingCorrection(const wchar_t* ID, uint64_t diffTimeMin, uint64_t diffTimeMax, uint64_t xCorr, uint64_t yCorr, double timewalkCorrFactor);
extern void _stdcall get2dHistogram(int tAcq, bool waitFinished, bool savePTU, unsigned int* data, bool* finished);
extern bool _stdcall getTimeTrace(const wchar_t* ID, int tAcq, bool waitFinished, bool savePTU, unsigned int* data, uint64_t* t0, bool* finished);
extern void _stdcall setTimeTraceNumBins(const wchar_t* ID, int numBins);
extern void _stdcall setTimeTraceHistorySize(const wchar_t* ID, double historySize);
extern void _stdcall setG2Params(const wchar_t* ID, uint64_t startChannel, uint64_t clickChannel, double windowSize, double binWidth);
extern void _stdcall setFCSParams(const wchar_t* ID, uint64_t startChannel, uint64_t clickChannel, uint64_t* numTaus, double startTime, double stopTime, uint64_t numBins);
extern void _stdcall setFFCSParams(const wchar_t* ID, uint64_t startChannel, uint64_t clickChannel, uint64_t* numTaus, double startTime, double stopTime, uint64_t numBins);
extern bool _stdcall getCorrelation(const wchar_t* ID, int tAcq, bool waitFinished, bool savePTU, double* data, double* bins, bool* finished);
extern bool _stdcall exportStreamMeasure(const wchar_t* ID, int tAcq, bool waitFinished, bool savePTU, bool* finished);
extern bool _stdcall rawMeasure(const wchar_t* ID, int tAcq, bool waitFinished, bool savePTU, unsigned int* data, unsigned long long* dataIdx, unsigned long long dataSize, bool* finished);
extern bool _stdcall rawStartBlock(const wchar_t* ID, int tAcq, bool savePTU, unsigned int* data, unsigned long long dataSize, bool* finished);
extern bool _stdcall rawGetBlock(const wchar_t* ID, unsigned int* data, unsigned long long* size);
extern bool _stdcall stopMeasure();
extern bool _stdcall clearMeasure();
extern bool _stdcall ufMeasure(const wchar_t* ID, int tAcq, bool waitFinished, bool savePTU, unsigned long long* times, unsigned char* chans, unsigned long long* idx, unsigned long long dataSize, bool* finished);
extern bool _stdcall ufStartBlock(const wchar_t* ID, int tAcq, bool savePTU, unsigned long long* time, unsigned char* chan, unsigned long long dataSize, bool* finished);
extern bool _stdcall ufGetBlock(const wchar_t* ID, uint64_t* times, unsigned char* chans, unsigned long long* size);
extern bool _stdcall getTimesFromChannelUF(unsigned char* channels, uint64_t* times, uint64_t* timesOut, int channel, size_t* size);

/********** Manipulators **********/
extern int _stdcall getNumAllChans(const wchar_t* ID);
extern void _stdcall clearManis(const wchar_t* ID);
extern void _stdcall deleteMani(const wchar_t* ID, int manisIdx);
extern int _stdcall addMCoincidence(const wchar_t* ID, int* chans, int numChans, double windowTime, int mode, int time, bool keepChannels);
extern int _stdcall addMMerge(const wchar_t* ID, int* chans, int numChans, bool keepChannels);
extern int _stdcall addMSubStream(const wchar_t* ID, uint64_t startTime, uint64_t stopTime);
extern int _stdcall addMDelay(const wchar_t* ID, int chan, double delayTime, bool keepChannel);
extern int _stdcall addMHerald(const wchar_t* ID, uint8_t herald, int* chans, int32_t numChans, int32_t delayTime, int32_t windowTime, bool inverted, bool keepChannels);
extern int _stdcall addMCountRate(const wchar_t* ID, double windowTime);
extern int _stdcall addMImportStream(const wchar_t* ID, char* deviceName, bool remoteStartStop, int* chans, int numChans, uint64_t delayTime);
extern bool _stdcall getMCountRates(const wchar_t* ID, int manisIdx, int* countRates);

/********** Marker **********/
extern bool _stdcall setMarkerEdges(const wchar_t* ID, int edge1, int edge2, int edge3, int edge4);
extern bool _stdcall setMarkerEnable(const wchar_t* ID, int ena1, int ena2, int ena3, int ena4);
extern bool _stdcall setMarkerHoldoffTime(const wchar_t* ID, int holdofftime);
extern bool _stdcall setOflCompression(const wchar_t* ID, int holdtime);

/********** HW-Filter **********/
extern bool _stdcall setRowEventFilter(const wchar_t* ID, int iRow, int timeRange, int matchCount, bool inverse, int useChans, int passChans);
extern bool _stdcall enableRowEventFilter(const wchar_t* ID, int iRow, bool enable);
extern bool _stdcall setMainEventFilterParams(const wchar_t* ID, int timeRange, int matchCount, bool inverse);
extern bool _stdcall setMainEventFilterChannels(const wchar_t* ID, int iRow, int useChans, int passChans);
extern bool _stdcall enableMainEventFilter(const wchar_t* ID, bool enable);
extern bool _stdcall setFilterTestMode(const wchar_t* ID, bool testMode);
extern bool _stdcall getRowFilteredRates(const wchar_t* ID, int* syncRate, int* countRates);
extern bool _stdcall getMainFilteredRates(const wchar_t* ID, int* syncRate, int* countRates);

/********** White Rabbit **********/
extern bool _stdcall WRabbitGetMAC(const wchar_t* ID, char* macAddr);
extern bool _stdcall WRabbitSetMAC(const wchar_t* ID, char* macAddr);
extern bool _stdcall WRabbitGetInitScript(const wchar_t* ID, char* script);
extern bool _stdcall WRabbitSetInitScript(const wchar_t* ID, char* script);
extern bool _stdcall WRabbitGetSFPData(const wchar_t* ID, char* sfpNames, int* dTxs, int* dRxs, int* alphas);
extern bool _stdcall WRabbitSetSFPData(const wchar_t* ID, char* sfpNames, int* dTxs, int* dRxs, int* alphas);
extern bool _stdcall WRabbitSetMode(const wchar_t* ID, int bootFromScript, int reinitWithMode, int mode);
extern bool _stdcall WRabbitSetTime(const wchar_t* ID, uint64_t time);
extern bool _stdcall WRabbitGetTime(const wchar_t* ID, uint64_t* time, uint32_t* subSec16ns);
extern bool _stdcall WRabbitGetStatus(const wchar_t* ID, uint32_t* status);
extern bool _stdcall WRabbitGetTermOutput(const wchar_t* ID, char* termOutput);
extern bool _stdcall WRabbitInitLink(const wchar_t* ID, int onOff);