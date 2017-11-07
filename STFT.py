import numpy as np
import scipy.fftpack as ft

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