import struct
import numpy as np
import sys
sys.path.append('FileSetObjects')
import fileSet as fs
import regularFileSet as rfs
import os

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


def getDataFromFiles(theFileSet, startTime, endTime, nChannelsTotal, startCh, endCh, secondsPerFile, ignoreChannels):
    fileList = theFileSet.getFileNamesInRange(startTime,endTime)    
    nBytesPerFile = os.path.getsize(fileList[0])
    bytesPerChannel = (nBytesPerFile-nTxtFileHeader-nBinFileHeader-240*nChannelsTotal)/nChannelsTotal
    samplesPerChannel = bytesPerChannel/4
    samplesPerSecond = samplesPerChannel/secondsPerFile 
    NyquistFrq = float(samplesPerSecond)/2.0
    samplesPerFile = samplesPerSecond*secondsPerFile

    data = np.zeros((endCh-startCh+1,int(samplesPerSecond*(endTime-startTime).total_seconds())))
    currentIdx = 0
    for i,f in enumerate(fileList):
        startSample = 0
        nSamplesToRead = samplesPerFile
        if(i==0): # first file, get start sample
            startFileTime = theFileSet.getTimeFromFilename(f)
            startSample = samplesPerSecond*(startFileTime-startTime).total_seconds()
        if(i == len(fileList)-1): # last file, calculate how many samples are left
            nSamplesToRead = data.shape[1] - currentIdx
        for ch in range(startCh,endCh+1):
            data[ch-startCh,currentIdx:currentIdx+nSamplesToRead] = readTrace(f,nSamplesToRead,4,ch,'>',startSample)
            if(ch in ignoreChannels): # if its a channel to ignore (weird noise spike, divide by 10^6)
                data[ch-startCh,currentIdx:currentIdx+nSamplesToRead] = data[ch-startCh,currentIdx:currentIdx+nSamplesToRead]*0.000001 
        currentIdx = currentIdx+nSamplesToRead
        
    return (data, samplesPerSecond)