from namePart import *
from fileSet import *
import math
import datetime

class regularFileSet(fileSet):
	'''This is a set of files that starts with a particular file time and includes many files that are evenly spaced by some number of seconds. If files in set are still being recorded nFiles -1 is the flag for that'''
	def __init__(self,listOfPartTypes,startYear,startMonth,startDay,startHour,startMin,startSec,startMillisec,secondsPerFile,nFiles=-1):
		fileSet.__init__(self,listOfPartTypes)
		self.startTime = datetime.datetime(startYear,startMonth,startDay,startHour,startMin,startSec,startMillisec*1000)
		self.secondsBetweenFiles = secondsPerFile
		self.nFiles = nFiles # if nFiles = -1 it treats it as though the number of files is unknown and goes up until the current time possibly (this can be risky)
		self.endTime = self.startTime+datetime.timedelta(seconds=self.nFiles*self.secondsBetweenFiles) # typical case with a specified number of files in this range
		if(self.nFiles == 0): # if number of files=-1 assume it goes until now
			self.endTime = datetime.now()

	def addFilesToEnd(self,nFilesToAdd=1):
		'''Add a file to the end of the regularFileSet by adjusting the endTime and nFiles'''
		self.nFiles = self.nFiles + nFilesToAdd
		self.endTime = self.startTime + datetime.timedelta(seconds=self.nFiles*self.secondsBetweenFiles)

	def addFilesToStart(self,nFilesToAdd=1):
		'''Add a file to the start of the regularFileSet by adjusting the startTime and nFiles'''
		self.nFiles = self.nFiles + nFilesToAdd
		self.startTime = self.startTime - datetime.timedelta(seconds=self.nFilesToAdd*self.secondsBetweenFiles)
		

	def getFileNameIncludingTime(self,dateTimeObjectRequested):
		'''Based on the datetime.datetime object representing the time you want to grab, this generates the file name in this file set'''
		if((dateTimeObjectRequested < self.startTime) or (dateTimeObjectRequested > self.endTime)):
			return "ERROR file not in this fileSet"
		else:
			timeIntoFileSet = dateTimeObjectRequested - self.startTime #timedelta object
			numberOfFilesIntoFileSet = math.floor(timeIntoFileSet.total_seconds()/self.secondsBetweenFiles)
			fileTime = self.startTime + datetime.timedelta(seconds=self.secondsBetweenFiles*numberOfFilesIntoFileSet)
			return self.generateFilenameDTObj(fileTime)



	def getFileNamesInRange(self,dateTimeObjectStart,dateTimeObjectEnd):
		'''Returns a list in order of all files in this fileSet that are between the start and end datetime datetime.datetime objects.''' 		
		if(dateTimeObjectStart > dateTimeObjectEnd):
			print("ERROR in fileSet.py getFileNamesInRange: make sure start is before end")
			return ([],[],[])
		else:
			# return empty set of there's definitely no overlap of these times and the fileset
			if((dateTimeObjectStart > self.endTime) or (dateTimeObjectEnd < self.startTime)):
				return []
			else:
				fileList = []
				# calculate the first time these ranges have in common
				firstTime = self.startTime
				if(self.startTime < dateTimeObjectStart): # if this file set starts before the requested range
					timeDiff = dateTimeObjectStart-self.startTime
					firstTime = self.startTime + datetime.timedelta(seconds = self.secondsBetweenFiles*(int(timeDiff.total_seconds())/int(self.secondsBetweenFiles)))
				
				# until you get to the last time these ranges have in common, continue generating the file names
				currentTime = firstTime
				timeToNextFile = datetime.timedelta(seconds=self.secondsBetweenFiles)
				lastCommonTime = min(dateTimeObjectEnd,self.endTime)
				while(currentTime < lastCommonTime):
					fileList.append(self.generateFilenameDTObj(currentTime))
					currentTime = currentTime + timeToNextFile
				return fileList
					
	def checkUnion(self, otherRFS):
		'''Checks if this RFS and another RFS are contiguous neighbors or overlapping. Returns False if they are not, and a regular file set made up of their union if they are.'''
		# Check if their start and end times line up and they have the same number of seconds per file
		theUnion = False
		timesOverlap = ((self.startTime <= otherRFS.startTime <=  self.endTime) or (self.startTime <= otherRFS.endTime <= self.endTime))
		sameFileLengths = (self.secondsBetweenFiles == otherRFS.secondsBetweenFiles)
		if timesOverlap and sameFileLengths:
			theUnion = True			

		# if they should be combined, do it!
		if theUnion:
			minStartTime = min(self.startTime, otherRFS.startTime)
			maxEndTime = max(self.endTime, otherRFS.endTime)
			nFilesTotal = int((maxEndTime-minStartTime).total_seconds()/self.secondsBetweenFiles)
			theUnion = regularFileSet(self.listOfPartTypes,minStartTime.year, minStartTime.month, minStartTime.day, minStartTime.hour, minStartTime.minute, minStartTime.second, int(0.001*minStartTime.microsecond),self.secondsBetweenFiles, nFilesTotal)

		return theUnion
