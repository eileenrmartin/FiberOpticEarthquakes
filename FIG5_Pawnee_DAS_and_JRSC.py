import numpy as np
import matplotlib.pyplot as plt
import obspy
import datetime as dt
from readers import *
from STFT import STFT
import os
from Fig5params import *
from readers import readTrace, getDataFromFiles
from obspy.clients.fdsn import Client

# info to use from the parameter file
timeWindowMin = intervalWidthSec*0.5
totalSeconds = (endTimeObspy-obspy.core.utcdatetime.UTCDateTime(startPlotTime))
timeWindowMax = totalSeconds - intervalWidthSec*0.5
nChannels = endCh-startCh+1





# read DASdata from files of interest
(data, samplesPerSecond) = getDataFromFiles(myFileSet, startTime, endTime, nChannelsTotal, startCh, endCh, secondsPerFile, ignoreChannels)  

# take time derivative, bandpass, remove laser drift then average the DAS signal
vel = (data[:,1:] - data[:,:-1])*samplesPerSecond 
minFrq = 0.02
maxFrq = 2.0
for ch in range(startCh,endCh+1):
	velTr = obspy.core.trace.Trace(data=vel[ch-startCh,:],header={'delta':1.0/float(samplesPerSecond),'sampling_rate':samplesPerSecond})
	velTr.filter('bandpass',freqmin=minFrq,freqmax=maxFrq,corners=4,zerophase=True)
	vel[ch-startCh,:] = velTr.data
vel = vel - np.median(vel,axis=0)# remove laser drift 
vel = vel[startCh-startCh:endCh-startCh+1,:] # cut down to channels not in the IU building

# get DAS spectrum (averaged over channels)
(HzPerBin,DASSpec,midSamples) = STFT(vel[0,:],1.0/float(samplesPerSecond),vel.shape[1], intervalWidthSec,intervalStartSpaceSec)
for ch in channelsSpec:
	(HzPerBin,thisSpec,midSamples) = STFT(vel[ch-startCh,:],1.0/float(samplesPerSecond),vel.shape[1],intervalWidthSec,intervalStartSpaceSec)
	DASSpec = DASSpec + thisSpec
DASSpec = DASSpec/len(channelsSpec) # average spectrum of DAS chanels

# plot average DAS spectrum (short time fourier)
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
plt.savefig('figs/Fig5Partial_Pawnee_DAS_STFT.pdf')
plt.clf()






# grab data from JRSC long period station, info about station can be found at: http://ds.iris.edu/mda/BK/JRSC
client = Client("NCEDC")
stE = client.get_waveforms('BK','JRSC','00','LHE',startTimeObspy,endTimeObspy, attach_response=True)
trE = stE.traces[0]
stN = client.get_waveforms('BK','JRSC','00','LHN',startTimeObspy,endTimeObspy,attach_response=True)
trN = stN.traces[0]
stZ = client.get_waveforms('BK','JRSC','00','LHZ',startTimeObspy,endTimeObspy,attach_response=True)
trZ = stZ.traces[0]


# get JRSC spectrum for vertical component and horizontal inline with some DAS channels
# calculate angle of the fiber line from East using UTM coords of a couple points along the line
(EastStart,NorthStart) = (572830.00,4142556.00) # (meters North, meters East)
(EastEnd,NorthEnd) = (572922.00, 4142826.00)
(directionEast,directionNorth) = (EastEnd-EastStart,NorthEnd-NorthStart)
rotationAngle = np.arctan(directionNorth/directionEast) # radians measured with 0 being due East
# rotate East and North components into direction of fiber channels and get amplitude spec
rotData = (stE.traces[0]).data*np.cos(rotationAngle) + (stN.traces[0]).data*np.sin(rotationAngle)
sampling_rate = (stE.traces[0]).stats['sampling_rate']
npts = (stE.traces[0]).stats['npts']
(HzPerBinJRSC,jrscSpec,middleSamplesJRSC) = STFT(rotData,1.0/sampling_rate,npts,intervalWidthSec,intervalStartSpaceSec)
(HzPerBinJRSC,jrscSpecZ,middleSamplesJRSC) = STFT((stZ.traces[0]).data,1.0/sampling_rate,npts,intervalWidthSec,intervalStartSpaceSec)

# plot JRSC spectra for both a horizontal (rotated inline with DAS array ch 50-100) and vertical component
startIdx = int(((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)-(0.5*intervalWidthSec))/float(intervalStartSpaceSec))
if(startIdx < 0):
	startIdx = 0
clipVal = np.percentile(np.log(np.concatenate((jrscSpec[:,startIdx:],jrscSpecZ[:,startIdx:]),axis=0)),99)
minClip = np.percentile(np.log(np.concatenate((jrscSpec[:,startIdx:],jrscSpecZ[:,startIdx:]),axis=0)),1)
nBinsFrq = jrscSpec.shape[0]-1
plt.imshow(np.log(jrscSpec[:,startIdx:]),aspect='auto',interpolation='nearest',vmax=clipVal,vmin=minClip,extent=[timeWindowMin,timeWindowMax,HzPerBinJRSC*nBinsFrq,HzPerBinJRSC],cmap=plt.get_cmap('jet')) # need to replace with spec imshow
plt.title('STFT of JRSC in-line with DAS')
plt.xlabel('seconds after start of event')
plt.ylabel('frequency (Hz)')
plt.colorbar()
plt.tight_layout()
plt.savefig('figs/Fig5Partial_Pawnee_JRSC_Horiz_STFT.pdf')
plt.clf()

nBinsFrq = jrscSpecZ.shape[0]-1
plt.imshow(np.log(jrscSpecZ[:,startIdx:]),aspect='auto',interpolation='nearest',vmax=clipVal,vmin=minClip,extent=[timeWindowMin,timeWindowMax,HzPerBinJRSC*nBinsFrq,HzPerBinJRSC],cmap=plt.get_cmap('jet')) # need to replace with spec imshow
plt.title('STFT of JRSC vertical')
plt.xlabel('seconds after start of event')
plt.ylabel('frequency (Hz)')
plt.colorbar()
plt.tight_layout()
plt.savefig('figs/Fig5Partial_Pawnee_JRSC_Z_STFT.pdf')
plt.clf()



# plot of JRSC overlaid on DAS array recording
startIdx = int(samplesPerSecond*(startPlotTime - startTime).total_seconds())
clipVal = np.percentile(np.absolute(vel[:,startIdx:]),99.7)
plt.imshow(vel[:,startIdx:],aspect='auto',interpolation='nearest',vmax=clipVal,vmin=-clipVal,cmap=plt.get_cmap('seismic'),extent=[0,(endTime-startPlotTime).total_seconds(),endCh,startCh]) 
scaleFactor=0.0002
startIdx = int((obspy.core.utcdatetime.UTCDateTime(startPlotTime)-startTimeObspy)) # 1 sample per second
plt.plot(scaleFactor*rotData[startIdx:]+(startCh+endCh)*0.5,'k',linewidth=1) # rotated from east and north data
plt.xlabel('seconds after start of event')
plt.ylabel('channel (8 m/channel)')
plt.title('DAS channel-wise recording overlaid with JRSC recording')
plt.colorbar()
plt.tight_layout()
plt.savefig('figs/Fig5Partial_Pawnee_DAS_and_JRSC_time.pdf')
plt.clf()


