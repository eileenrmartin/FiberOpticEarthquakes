
##### main class for getting various parts of a file name ######

class namePart:
	def __init__(self,nChars):
		self.nChars = nChars

nCharsPerType = { 'year2': 2, 'year4':4, 'month':2, 'day':2, 'hour24start0':2, 'hour24start1':2, 'minute':2, 'second':2, 'millisecond':3, 'microsecond':6 }

##### below, lots of classes for dealing with all the parts of a file name #####
class presetString:
	''' Use this for any preset strings that are part of the file name, same for all times'''
	def __init__(self,whichString):
		namePart.__init__(self,len(whichString))
		self.whichString = whichString

	def __str__(self):
		return self.whichString

class year2(namePart):
	def __init__(self,whichYear):
		namePart.__init__(self,nCharsPerType['year2'])
		self.whichYear = whichYear % 100
	
	def __str__(self):
		secondDig = self.whichYear % 10
		firstDig = ((self.whichYear-secondDig) % 100)/10
		return(str(firstDig)+str(secondDig))

class year4(namePart):
	def __init__(self,whichYear):
		namePart.__init__(self,nCharsPerType['year4'])
		self.whichYear = whichYear
	
	def __str__(self):
		fourthDig = self.whichYear % 10
		thirdDig = ((self.whichYear-fourthDig) % 100)/10
		secondDig = ((self.whichYear-thirdDig*10-fourthDig) % 1000)/100
		firstDig = (self.whichYear-secondDig*100-thirdDig*10-fourthDig)/1000 
		return(str(firstDig)+str(secondDig)+str(thirdDig)+str(fourthDig))

class month(namePart):
	''' month should be specified as 1 through 12 for January through December'''
	def __init__(self,whichMonth,verbose=False):
		namePart.__init__(self,nCharsPerType['month'])
		if(verbose): 
			if(whichMonth < 1 or whichMonth > 12): print("Warning month shoudl be 1 to 12, but is "+str(whichMonth))
		self.whichMonth = whichMonth
	
	def __str__(self):
		if(self.whichMonth < 10): 
			return "0"+str(self.whichMonth)
		else: 
			return str(self.whichMonth)

class day(namePart):
	def __init__(self,whichDay, whichMonth, whichYear,verbose=False):
		'''The definition of the day actually needs a month and year specification so its next method works'''
		namePart.__init__(self,nCharsPerType['day'])
		self.whichMonth = whichMonth
		self.DaysPerMonth = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
		if(whichYear % 4 == 0 and whichYear % 100 != 0): self.DaysPerMonth[2] = 29 # leap years
		if(whichYear % 400 == 0): self.DaysPerMonth[2] = 29 # weird exception
		if(verbose): 
			if(whichDay < 1 or whichDay > self.DaysPerMonth[self.whichMonth]): print("Warning day should be 1 to "+str(self.DaysPerMonth[self.whichMonth])+ "for this month, but it is "+str(whichDay))
		self.whichDay = whichDay
	
	def __str__(self):
		if(self.whichDay < 10): 
			return "0"+str(self.whichDay)
		else: 
			return str(self.whichDay)


class hour24start0(namePart):
	''' hour should be specified as 0 to 23'''
	def __init__(self,whichHr, verbose=False):
		namePart.__init__(self,nCharsPerType['hour24start0'])
		if(verbose): 
			if(whichHr < 0 or whichHr > 23): print("Warning: hour24start0 should be 0 to 23, but is "+str(whichHr))
		self.whichHr = whichHr

	def __str__(self):
		if(self.whichHr < 10):
			return "0"+str(self.whichHr)
		else:
			return str(self.whichHr)

class hour24start1(namePart):
	''' hour should be specified as 1 to 24'''
	def __init__(self,whichHr,verbose=False):
		namePart.__init__(self,nCharsPerType['hour24start1'])
		if(verbose): 
			if(whichHr < 1 or whichHr > 24): print("Warning: hour24start1 should be 1 to 24, but is "+str(whichHr))
		self.whichHr = whichHr

	def __str__(self):
		if(self.whichHr < 10):
			return "0"+str(self.whichHr)
		else:
			return str(self.whichHr)

class minute(namePart):
	''' minute should be specified as 0 through 59'''
	def __init__(self,whichMin,verbose=False):
		namePart.__init__(self,nCharsPerType['minute'])
		if(verbose): 
			if(whichMin < 0 or whichMin > 59): print("Warning minute shoudl be 0 to 59, but is "+str(whichMin))
		self.whichMin = whichMin
	
	def __str__(self):
		if(self.whichMin < 10): 
			return "0"+str(self.whichMin)
		else: 
			return str(self.whichMin)

class second(namePart):
	''' second should be specified as 0 through 59'''
	def __init__(self,whichSec,verbose=False):
		namePart.__init__(self,nCharsPerType['second'])
		if(verbose): 
			if(whichSec < 0 or whichSec > 59): print("Warning second shoudl be 0 to 59, but is "+str(whichSec))
		self.whichSec = whichSec
	
	def __str__(self):
		if(self.whichSec < 10): 
			return "0"+str(self.whichSec)
		else: 
			return str(self.whichSec)

class millisecond(namePart):
	'''millisecond should be specified as 0 through 999'''
	def __init__(self,whichMillisec,verbose=False):
		namePart.__init__(self,nCharsPerType['millisecond'])
		if(verbose):
			if(whichMillisec < 0 or whichMillisec > 999): print("Warning millisecond should be 0 to 999, but is "+str(whichMillisec))
		self.whichMillisec = whichMillisec

	def __str__(self):
		if(self.whichMillisec < 10):
			return "00"+str(self.whichMillisec)
		else:
			if(self.whichMillisec < 100):
				return "0"+str(self.whichMillisec)
			else: # 100 to 999 milliseconds
				return str(self.whichMillisec)

class microsecond(namePart):
	'''microsecond should be specified as 0 to 999999, and you probably wouldnt us it along wiht millisecond'''
	def __init__(self,whichMicrosec,verbose=False):
		namePart.__init__(self,nCharsPerType['microsecond'])
		if(verbose):
			if(whichMicrosec < 0 or whichMicrosec > 999999): print("Warning microsecond should be 0 to 999999, but is "+str(whichMicrosec))
		self.whichMicrosec = whichMicrosec

	def __str__(self):
		currentStr = str(self.whichMicrosec)
		if(self.whichMicrosec < 100000):
			currentStr = '0'+currentStr
			if(self.whichMicrosec < 10000):
				currentStr = '0'+currentStr
				if(self.whichMicrosec < 1000):
					currentStr = '0'+currentStr
					if(self.whichMicrosec < 100):
						currentStr = '0'+currentStr
						if(self.whichMicrosec < 10):
							currentStr = '0'+currentStr
		return currentStr
