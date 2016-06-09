#!/usr/bin/python 

#
# Copyright 2015, Plymouth Marine Laboratory
#
# This file is part of the bgc-val library.
#
# bgc-val is free software: you can redistribute it and/or modify it
# under the terms of the Revised Berkeley Software Distribution (BSD) 3-clause license. 

# bgc-val is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the revised BSD license for more details.
# You should have received a copy of the revised BSD license along with bgc-val.
# If not, see <http://opensource.org/licenses/BSD-3-Clause>.
#
# Address:
# Plymouth Marine Laboratory
# Prospect Place, The Hoe
# Plymouth, PL1 3DH, UK
#
# Email:
# ledm@pml.ac.uk

from sys import argv 
import subprocess
from socket import gethostname
import os
from glob import glob
from re import findall

def getYearFromFile(fn):
	a = findall(r'\d\d\d\d\d\d\d\d',fn)
	for i in a:
	    if i[-4:] == '1130': 
	    	yr = i[:4]
	      	return yr
			      
	return False
	
	
def findLastFinishedYear(jobID):
	"""
		command:
		downloadMass jobID options.
		options:
			anymachine : skip check.
	"""
	if jobID == '': return
	
	machine = gethostname()
	if machine.find('ceda')>-1:
		outputFold = "/group_workspaces/jasmin2/ukesm/BGC_data/"+jobID+'/'

	if machine.find('monsoon')>-1:
                outputFold = "/projects/ukesm/ldmora/UKESM/"+jobID+'/'
                        
	if gethostname().find('pmpc')>-1:	
                outputFold = "/data/euryale7/scratch/ledm/UKESM/MEDUSA/"+jobID+'/'		
		                        
	fnDict = {}	
	files = sorted(glob(outputFold+jobID+'o_1y_????1201_????1130_????_?.nc'))
	suffixes = ['diad_T.nc', 'grid_T.nc','grid_U.nc','grid_V.nc','grid_W.nc','ptrc_T.nc']
	for fn in files:
		yr = getYearFromFile(fn)
		print fn, yr
		try: 	fnDict[yr]+=1
		except:	fnDict[yr] =1
	
	years = sorted(fnDict.keys())
	years.reverse()
	
	print years, fnDict
	for y in years:
		print y,':', fnDict[y]
		if fnDict[y] == len(suffixes): return y
		
	print "No correct year, there's probably a problem here findLastFinishedYear(",jobID,")"
	print "Machine", machine
	print "outputFold:", outputFold
	assert 0	


def downloadMass(jobID,):
	"""
		command:
		downloadMass jobID options.
		options:
			anymachine : skip check.
	"""
	if jobID == '': return
	
	machine = gethostname()
	knownmachine = False	
	if machine.find('ceda')>-1:
		knownmachine = True
		outputFold = "/group_workspaces/jasmin2/ukesm/BGC_data/"+jobID
		if not os.path.exists(outputFold):
			print "Making ",outputFold
    			os.makedirs(outputFold)

	if machine.find('monsoon')>-1:
		knownmachine = True
                outputFold = "/projects/ukesm/ldmora/UKESM/"+jobID
                if not os.path.exists(outputFold):
                        print "Making ",outputFold
                        os.makedirs(outputFold)

		
	if not knownmachine :
		print "Are you running this on the correct machine?"
		print "\tYou should be on mass-cli1.ceda.ac.uk at jasmin or on monsoon at the MO"
		print "\tBut you're at",machine
		print "\tTo skip this warning, use the \"anymachine\" option at the command line"
		return
	
	

	
	
	print "Looking at the following files:"
	
	bashCommand = "moo ls moose:/crum/"+jobID+"/ony.nc.file/*.nc "
	print "running the command:",bashCommand
		
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]



	print "Downloading at the following files:"
	
	bashCommand = "moo get --fill-gaps moose:/crum/"+jobID+"/ony.nc.file/*.nc "+outputFold
	print "running the command:",bashCommand
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]





if __name__=="__main__":	
	
	try:	jobID = argv[1]
	except:	
		print "Please provide a jobID"
		jobID = ''
	downloadMass(jobID)
	
	
	
	
	
	
	
	
