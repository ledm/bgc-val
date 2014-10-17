#!/usr/bin/ipython 
#Standard Python modules:
from sys import argv

#Specific local code:
from UKESMpython import folder,getFileList
from cchl import cchl
from cchlvsIrradiance import cchlvsIrradiance
from communityfit import communityfit

"""
	This is the hold all for the analyses. 
	It can be used to run each of the analyses in series, for any number of input files.
	As more analsyes are added to the package, please copy the template and add more.
	/data/euryale7/scratch/ledm/UKESM/MEDUSA/medusa_bio_1998.nc

"""




def main():
	try:
		filesIn = getFileList(argv[1:])
		print "Using command line arguments:", filesIn	
		
	except:
		print "testsuite:\tERROR:\tSomething wrong with file specified", argv[1:]
		return
	
	if not len(filesIn):
		print "testsuite:\tERROR:\tNo files specified, try:"
		print "./testsuite.py /data/euryale7/scratch/ledm/UKESM/MEDUSA/medusa_bio_1998.nc"
	
	for fn in filesIn:
		print "testsuite:\tINFO:\t",fn	
		a = cchlvsIrradiance(fn)
		a = cchl(fn)
		a = communityfit(fn)









	
if __name__=="__main__":
	main() 
	print 'The end.'
