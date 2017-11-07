import obspy
import sys
sys.path.append('FileSetObjects')
import fileSet as fs
import regularFileSet as rfs
import datetime as dt

# coefficients for spectrum and times of interest and channels of interest
secondsPerFile = 60
intervalWidthSec = 50 # 50 second intervals
intervalStartSpaceSec = 10 # new interval starts every 10 seconds
startTimeObspy = obspy.UTCDateTime("2016-09-03T12:00:54.932000Z")
startTime = dt.datetime(2016,9,3,12,0,54,932*1000)
endTimeObspy = obspy.UTCDateTime("2016-09-03T12:21:54.932000Z")
endTime = dt.datetime(2016,9,3,12,21,54,932*1000)
startPlotTime = dt.datetime(2016,9,3,12,2,44)


# coefficients for channels of interest
nChannelsTotal = 620
startCh = 15
endCh =305
ignoreChannels = [107,280,285]
# setup spectrum channel list with three sections of channels that don't have loud noises during any part of the earthquake record time
channelsSpec = range(30,55) 
for ch in range(80,100): 
	channelsSpec.append(ch)
for ch in range(165,305):
	channelsSpec.append(ch)

# setup of filenames 
parts = ['data/Pawnee/cbt_processed_','year4','month','day','_','hour24start0','minute','second','.','millisecond','+0000.sgy']
nFiles = int((endTime-startTime).seconds/secondsPerFile)
myFileSet = rfs.regularFileSet(parts,startTime.year,startTime.month,startTime.day,startTime.hour,startTime.minute,startTime.second,int(0.001*startTime.microsecond),secondsPerFile,nFiles)