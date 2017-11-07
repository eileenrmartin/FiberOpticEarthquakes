import copy
import datetime
from namePart import * # note that dictionary nCharsPerType is defined in namePart

class fileSet:
	def __init__(self,listOfPartTypes):
		# names of classes of different parts, anything that's not one of these is assumed to be a string
		self.OKPartNames = ['year2','year4','month','day','hour24start0','hour24start1','minute','second','millisecond','microsecond']
		self.listOfPartTypes = copy.deepcopy(listOfPartTypes)


	
	def generateFilename(self, yearVal, monthVal, dayVal, hourVal, minuteVal, secondVal, millisecVal=0, microsecVal=0):
		'''Using your naming convention specified by the listOfPartTypes, create a name for a file starting at this time, just use millisecond or microsecond'''
		# a mapping of going from the part of the name to the string that should go to that part
		getNamePart = { 'year2': str(year2(yearVal)), 'year4': str(year4(yearVal)), 'month': str(month(monthVal)), 'day': str(day(dayVal,monthVal,yearVal)), 'hour24start0': str(hour24start0(hourVal)), 'hour24start1': str(hour24start1(hourVal)), 'minute': str(minute(minuteVal)), 'second':str(second(secondVal)) , 'millisecond':str(millisecond(millisecVal)) , 'microsecond':str(microsecond(microsecVal))}
		# generate the filename
		filename = ''
		for part in self.listOfPartTypes:
			if(part in self.OKPartNames):
				filename = filename + getNamePart[part]
			else: # otherwise it's a string that's exactly preserved
				filename = filename+part
		return filename	



	def generateFilenameDTObj(self, dateTimeObj):
		'''same as generateFilename except it takes a datetime object instead of year,month,day,hour,minut,second'''
		if('millisecond' in self.OKPartNames):
			return self.generateFilename(dateTimeObj.year, dateTimeObj.month, dateTimeObj.day, dateTimeObj.hour, dateTimeObj.minute, dateTimeObj.second, millisecVal = dateTimeObj.microsecond/1000)
		else: # use microsecond
			return self.generateFilename(dateTimeObj.year, dateTimeObj.month, dateTimeObj.day, dateTimeObj.hour, dateTimeObj.minute, dateTimeObj.second, millisecVal = 0, microsecVal = dateTimeObj.microsecond)
			


	def getValuePart(self,part,startindex,filename):
		'''This is a helper function used by getTimeFromFilename'''
		if(part == 'year2'):
			return 2000+int(filename[startindex:startindex+nCharsPerType['year2']])
		elif(part == 'hour24start1'):
			return -1+int(filename[startindex:startindex+nCharsPerType['hour24start1']])
		else:
			return int(filename[startindex:startindex+nCharsPerType[part]])



	def getTimeFromFilename(self, myFilename):
		'''Take a file name that follows this naming convention and return a datetime object with the right time set for that name'''
		currentIndex = 0
		# if any of these arent filled in, give a reasonable default
		myTime = {'year': 2016, 'month': 1, 'day': 1, 'hour': 0, 'minute': 0, 'second': 0, 'millisecond': 0}
		# how to set the variable that goes into the datetime constructor for each part
		getValueVariable = {'year2': 'year' , 'year4': 'year', 'month': 'month', 'day': 'day' , 'hour24start0': 'hour' , 'hour24start1': 'hour' , 'minute': 'minute', 'second': 'second', 'millisecond':'millisecond', 'microsecond':'microsecond'}
		
		for part in self.listOfPartTypes:
			if(part in self.OKPartNames):
				myTime[getValueVariable[part]] = self.getValuePart(part,currentIndex,myFilename) # set the time value for this part of the name
				currentIndex = currentIndex + nCharsPerType[part]
			else: # its a string thats exactly preserved so skip ahead that many characters
				nChars = len(part)
				if(myFilename[currentIndex:currentIndex+nChars] != part): # check that the filename includes this string
					print("Warning: characters "+str(currentIndex)+" to "+str(currentIndex+nChars-1)+" should be "+part+" but are really "+myFilename[currentIndex:currentIndex+nChars])
				currentIndex += nChars # go ahead to next part of name
		if('millisecond' in self.listOfPartTypes):
			return datetime.datetime(myTime['year'],myTime['month'],myTime['day'],myTime['hour'],myTime['minute'],myTime['second'],1000*myTime['millisecond'])
		elif('microsecond' in self.listOfPartTypes):
			return datetime.datetime(myTime['year'],myTime['month'],myTime['day'],myTime['hour'],myTime['minute'],myTime['second'],myTime['microsecond'])
		else: 
			return datetime.datetime(myTime['year'],myTime['month'],myTime['day'],myTime['hour'],myTime['minute'],myTime['second'])

