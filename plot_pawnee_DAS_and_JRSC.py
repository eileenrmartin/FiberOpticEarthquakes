import numpy as np
import matplotlib.pyplot as plt
import obspy
import scipy.fftpack as ft
from numpy import linalg as la
import sys
sys.path.append('/home/ermartin/FileSetObjects')
import fileSet as fs
import regularFileSet as rfs
import datetime as dt
import struct


# function to calculate short time fourier transfor
def STFT(data,samplingDT,npts,intervalWidthSec,intervalStartSpaceSec):
	samplesPerInterval = int(intervalWidthSec/samplingDT)
	intervalStartIdx = np.arange(0,npts-1-samplesPerInterval,int(intervalStartSpaceSec/samplingDT))
        middleSamples = intervalStartIdx + samplesPerInterval/2
	nIntervals = intervalStartIdx.size
	HzPerBin = (1.0/samplingDT)/samplesPerInterval
	stft = np.zeros((samplesPerInterval,nIntervals))
	for i in range(nIntervals):
		startIdx = intervalStartIdx[i]
		stopIdx = intervalStartIdx[i]+samplesPerInterval
		stft[:,i] = np.absolute(ft.fft(data[startIdx:stopIdx]))
	return (HzPerBin, stft[:samplesPerInterval/2,:], middleSamples)


# coefficients for spectrum and times of interest and channels of interest
secondsPerFile = 60
intervalWidthSec = 50 # 50 second intervals
intervalStartSpaceSec = 10 # new interval starts every 10 seconds
startTimeObspy = obspy.UTCDateTime("2016-09-03T12:00:54.932000Z")
startTime = dt.datetime(2016,9,3,12,0,54,932*1000)
endTimeObspy = obspy.UTCDateTime("2016-09-03T12:21:54.932000Z")
endTime = dt.datetime(2016,9,3,12,21,54,932*1000)
startPlotTime = dt.datetime(2016,9,3,12,2,44)
startCh = 15
endCh =305
ignoreChannels = [107,280,285]
startChRead = 15
endChRead = 305
# setup spectrum channel list
channelsSpec = range(30,55)
for ch in range(80,100):
	channelsSpec.append(ch)
for ch in range(165,305):
	channelsSpec.append(ch)
# file naming convention
parts = ['data/Pawnee/','year4','/','month','/','day','/cbt_processed_','year4','month','day','_','hour24start0','minute','second','.','millisecond','+0000.sgy']
nFiles = int((endTime-startTime).seconds/secondsPerFile)
myFileSet = rfs.regularFileSet(parts,startTime.year,startTime.month,startTime.day,startTime.hour,startTime.minute,startTime.second,int(0.001*startTime.microsecond),secondsPerFile,nFiles)

# grab data from JRSC broadband
from obspy.clients.fdsn import Client
client = Client("NCEDC")
stE = client.get_waveforms('BK','JRSC','00','LHE',startTimeObspy,endTimeObspy, attach_response=True)
trE = stE.traces[0]
stN = client.get_waveforms('BK','JRSC','00','LHN',startTimeObspy,endTimeObspy,attach_response=True)
trN = stN.traces[0]
stZ = client.get_waveforms('BK','JRSC','00','LHZ',startTimeObspy,endTimeObspy,attach_response=True)
trZ = stZ.traces[0]

# returns a stream object with 3 traces
# info about station can be found at: http://ds.iris.edu/mda/BK/JRSC
# "BK" is Berkeley Digital Seismic Network
# "JRSC" is Jasper Ridge Seismic Station in Stanford, CA
# "00" the location 
# "LH*" grabs the LHE, LHN, LHZ seismometer long period channels

# get UTM coordinates for channels of interest
ChEastUTMNorthUTM = np.load('../../inter_results/PassiveChEastUTMNorthUTM.npz')
Channels = ChEastUTMNorthUTM['arr_0']
EastUTM = ChEastUTMNorthUTM['arr_1']
NorthUTM = ChEastUTMNorthUTM['arr_2'] 


nTxtFileHeader = 3200
nBinFileHeader = 400
nTraceHeader = 240
def readTrace(infile,nSamples,dataLen,traceNumber,endian,startSample):
    '''infile is .sgy, nSamples is the number of samples per sensor, and traceNumber is the sensor number (start with 1),dataLen is number of bytes per data sample'''

    fin = open(infile, 'rb') # open file for reading binary mode
    startData = nTxtFileHeader+nBinFileHeader+nTraceHeader+(traceNumber-1)*(nTraceHeader+dataLen*nSamples)+startSample*dataLen
    fin.seek(startData)
    thisTrace = np.zeros(nSamples)
    for i in range(nSamples):
       	# was >f before
       	thisTrace[i] = struct.unpack(endian+'f',fin.read(dataLen))[0]
    fin.close()
    return thisTrace

# read fiber data for channels of interest
import os
fileList = myFileSet.getFileNamesInRange(startTime,endTime)
nBytesPerFile = os.path.getsize(fileList[0])
nChannels = 620
bytesPerChannel = (nBytesPerFile-nTxtFileHeader-nBinFileHeader-240*nChannels)/nChannels
samplesPerChannel = bytesPerChannel/4
samplesPerSecond = samplesPerChannel/secondsPerFile 
NyquistFrq = float(samplesPerSecond)/2.0
samplesPerFile = samplesPerSecond*secondsPerFile
nChannels = endChRead-startChRead+1
data = np.zeros((nChannels,int(samplesPerSecond*(endTime-startTime).total_seconds())))
currentIdx = 0
for i,f in enumerate(fileList):
	startSample = 0
	nSamplesToRead = samplesPerFile
	if(i==0): # first file, get start sample
		startFileTime = myFileSet.getTimeFromFilename(f)
		startSample = samplesPerSecond*(startFileTime-startTime).total_seconds()
	if(i == len(fileList)-1): # last file, calculate how many samples are left
		nSamplesToRead = data.shape[1] - currentIdx
	for ch in range(startChRead,endChRead+1):
		data[ch-startChRead,currentIdx:currentIdx+nSamplesToRead] = readTrace(f,nSamplesToRead,4,ch,'>',startSample)
		if(ch in ignoreChannels): # if its a channel to ignore (weird noise spike, divide by 10^6)
			data[ch-startChRead,currentIdx:currentIdx+nSamplesToRead] = data[ch-startChRead,currentIdx:currentIdx+nSamplesToRead]*0.000001 

	currentIdx = currentIdx+nSamplesToRead

# take time derivative, bandpass, then average the DAS signal
vel = (data[:,1:] - data[:,:-1])*samplesPerSecond 
minFrq = 0.02
maxFrq = 2.0
for ch in range(startChRead,endChRead+1):
	velTr = obspy.core.trace.Trace(data=vel[ch-startChRead,:],header={'delta':1.0/float(samplesPerSecond),'sampling_rate':samplesPerSecond})
	velTr.filter('bandpass',freqmin=minFrq,freqmax=maxFrq,corners=4,zerophase=True)
	vel[ch-startChRead,:] = velTr.data
# remove laser drift 
vel = vel - np.median(vel,axis=0)
# go down to just the part with no cars that we're visualizing and calculating spectra with
vel = vel[startCh-startChRead:endCh-startChRead+1,:]
nChannels = endCh-startCh+1


(HzPerBin,DASSpec,midSamples) = STFT(vel[0,:],1.0/float(samplesPerSecond),vel.shape[1], intervalWidthSec,intervalStartSpaceSec)
for ch in channelsSpec:
	(HzPerBin,thisSpec,midSamples) = STFT(vel[ch-startCh,:],1.0/float(samplesPerSecond),vel.shape[1],intervalWidthSec,intervalStartSpaceSec)
	DASSpec = DASSpec + thisSpec
DASSpec = DASSpec/len(channelsSpec) # average spectrum of DAS chanels
velAvg = np.sum(vel,axis=0)/nChannels

# calculate angle of the fiber line from East using UTM coords of a couple points along the line
(EastStart,NorthStart) = (572830.00,4142556.00) #m N, m E
(EastEnd,NorthEnd) = (572922.00, 4142826.00)
(directionEast,directionNorth) = (EastEnd-EastStart,NorthEnd-NorthStart)
rotationAngle = np.arctan(directionNorth/directionEast) # radians measured with 0 being due East

# rotate East and North components into direction of fiber channels and get amplitude spec
#stE.remove_response(output="VEL") # get rid of instrument response
#stN.remove_response(output="VEL") # get rid of instrument response
rotData = (stE.traces[0]).data*np.cos(rotationAngle) + (stN.traces[0]).data*np.sin(rotationAngle)
sampling_rate = (stE.traces[0]).stats['sampling_rate']
npts = (stE.traces[0]).stats['npts']
(HzPerBinJRSC,jrscSpec,middleSamplesJRSC) = STFT(rotData,1.0/sampling_rate,npts,intervalWidthSec,intervalStartSpaceSec)
(HzPerBinJRSC,jrscSpecZ,middleSamplesJRSC) = STFT((stZ.traces[0]).data,1.0/sampling_rate,npts,intervalWidthSec,intervalStartSpaceSec)



print('hz per bin')
print(HzPerBinJRSC)

print(HzPerBin)
startIdx = int((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)) # 1 sample per second
plt.plot(rotData[startIdx:]) # rotated from east and north data
plt.title('JRSC rotated in-line with DAS')
plt.xlabel('seconds after start of event')
plt.savefig('Pawnee_JRSC_time.pdf')
plt.clf()

startIdx = int(((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)-(0.5*intervalWidthSec))/float(intervalStartSpaceSec))
if(startIdx < 0):
	startIdx = 0
timeWindowMin = intervalWidthSec*0.5
totalSeconds = (endTimeObspy-obspy.core.utcdatetime.UTCDateTime(startPlotTime))
timeWindowMax = totalSeconds - intervalWidthSec*0.5
clipVal = np.percentile(np.log(np.concatenate((jrscSpec[:,startIdx:],jrscSpecZ[:,startIdx:]),axis=0)),99)
minClip = np.percentile(np.log(np.concatenate((jrscSpec[:,startIdx:],jrscSpecZ[:,startIdx:]),axis=0)),1)
nBinsFrq = jrscSpec.shape[0]-1
plt.imshow(np.log(jrscSpec[:,startIdx:]),aspect='auto',interpolation='nearest',vmax=clipVal,vmin=minClip,extent=[timeWindowMin,timeWindowMax,HzPerBinJRSC*nBinsFrq,HzPerBinJRSC],cmap=plt.get_cmap('jet')) # need to replace with spec imshow
plt.title('STFT of JRSC in-line with DAS')
plt.xlabel('seconds after start of event')
plt.ylabel('frequency (Hz)')
plt.colorbar()
plt.tight_layout()
plt.savefig('Pawnee_JRSC_Horiz_STFT.pdf')
plt.clf()

#clipVal = np.percentile(np.log(jrscSpecZ[:,startIdx:]),99)
nBinsFrq = jrscSpecZ.shape[0]-1
plt.imshow(np.log(jrscSpecZ[:,startIdx:]),aspect='auto',interpolation='nearest',vmax=clipVal,vmin=minClip,extent=[timeWindowMin,timeWindowMax,HzPerBinJRSC*nBinsFrq,HzPerBinJRSC],cmap=plt.get_cmap('jet')) # need to replace with spec imshow
plt.title('STFT of JRSC vertical')
plt.xlabel('seconds after start of event')
plt.ylabel('frequency (Hz)')
plt.colorbar()
plt.tight_layout()
plt.savefig('Pawnee_JRSC_Z_STFT.pdf')
plt.clf()



# plot of JRSC overlaid on DAS array recording
startIdx = int(samplesPerSecond*(startPlotTime - startTime).total_seconds())
#vel[:,startIdx:] = vel[:,startIdx:] / np.median(np.absolute(vel[:,startIdx:]))
clipVal = np.percentile(np.absolute(vel[:,startIdx:]),99.7)
plt.imshow(vel[:,startIdx:],aspect='auto',interpolation='nearest',vmax=clipVal,vmin=-clipVal,cmap=plt.get_cmap('seismic'),extent=[0,(endTime-startPlotTime).total_seconds(),endCh,startCh]) # need to replace with DAS
scaleFactor=0.0002
startIdx = int((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)) # 1 sample per second
plt.plot(scaleFactor*rotData[startIdx:]+(startCh+endCh)*0.5,'k',linewidth=1) # rotated from east and north data
plt.xlabel('seconds after start of event')
plt.ylabel('channel (8 m/channel)')
plt.title('DAS channel-wise recording overlaid with JRSC recording')
plt.colorbar()
plt.tight_layout()
#plt.show()
plt.savefig('Pawnee_DAS_and_JRSC_time.pdf')
plt.clf()

# zero out small amount of data around P and S arrivals to make it obvious where those are
PTime = startTimeObspy + dt.timedelta(seconds=270)
PIdx = int(((obspy.core.utcdatetime.UTCDateTime(PTime)-startTimeObspy)-(0.5*intervalWidthSec))/float(intervalStartSpaceSec))
STime = startTimeObspy + dt.timedelta(seconds=495)
SIdx =  int(((obspy.core.utcdatetime.UTCDateTime(STime)-startTimeObspy)-(0.5*intervalWidthSec))/float(intervalStartSpaceSec))
y = np.array([25,25])
x = np.array([270,495])
plt.imshow(vel[:,startIdx:],aspect='auto',interpolation='nearest',vmax=clipVal,vmin=-clipVal,cmap=plt.get_cmap('seismic'),extent=[0,(endTime-startPlotTime).total_seconds(),endCh,startCh]) # need to replace with DAS
plt.scatter(x,y)
scaleFactor=0.0002
startIdx = int((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)) # 1 sample per second
plt.plot(scaleFactor*rotData[startIdx:]+(startCh+endCh)*0.5,'k',linewidth=1) # rotated from east and north data
plt.xlabel('seconds after start of event')
plt.ylabel('channel (8 m/channel)')
plt.title('DAS channel-wise recording overlaid with JRSC recording')
#plt.colorbar()
#plt.tight_layout()
#plt.show()
plt.savefig('Pawnee_DAS_and_JRSC_time_with_P_S_picks.pdf')
plt.clf()



startIdx =  int(((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)-(0.5*intervalWidthSec))/float(intervalStartSpaceSec))
if(startIdx < 0):
	startIdx = 0
nBinsDASFrq = 50
specSubset = DASSpec[1:nBinsDASFrq,startIdx:]
clipVal = np.percentile(np.log(specSubset),99)
minClip = np.percentile(np.log(specSubset),1)
plt.imshow(np.log(specSubset),aspect='auto',interpolation='nearest',vmax=clipVal,vmin=minClip,extent=[timeWindowMin,timeWindowMax,HzPerBin*nBinsDASFrq,HzPerBin],cmap=plt.get_cmap('jet')) # need to replace with spec imshow of DAS
plt.xlabel('seconds after start of event')
plt.colorbar()
plt.ylabel('frequency (Hz)')
plt.title('STFT of DAS')
plt.tight_layout()
plt.savefig('Pawnee_DAS_STFT.pdf')
plt.clf()

