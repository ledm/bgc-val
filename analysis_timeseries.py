#!/usr/bin/ipython 

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
#


#####	
# Load Standard Python modules:
from sys import argv,exit
from os.path import exists
from calendar import month_name
from socket import gethostname
from netCDF4 import Dataset
from glob import glob
from scipy.interpolate import interp1d
import numpy as np
import os,sys
from getpass import getuser

#####	
# Load specific local code:
import UKESMpython as ukp
from timeseries import timeseriesAnalysis
from timeseries import profileAnalysis

timeseriesKeys = ['T','S','MLD', 'Chl_pig','Chl_CCI',
		  'N','Si','O2','Alk','DIC','AirSeaFlux','Iron',
		  'TotalAirSeaFlux','IntPP_iMarNet','IntPP_OSU',
		  'PP_OSU','LocalExportRatio','GlobalExportRatio',
		  'OMZThickness', 'TotalOMZVolume',		  
		  ]
timeseriesDict = {i:n for i,n in enumerate(timeseriesKeys)}
level1Keys = ['N', 'Si','O2','Alk','DIC','AirSeaFlux','TotalAirSeaFlux','IntPP_OSU','PP_OSU' ,'LocalExportRatio','GlobalExportRatio' ,'TotalOMZVolume','OMZThickness' ,'Iron']
level1KeysDict = {i:n for i,n in enumerate(level1Keys)}	

def analysis_timeseries(jobID = "u-ab671",
			clean = 0,
			annual = True,
			strictFileCheck = True,
			analysisSuite = 'all',
			regions = 'all',
			):

	"""
		The role of this code is to produce time series analysis.
		The jobID is the monsoon/UM job id and it looks for files with a specific format
		
		The clean flag allows you to start the analysis without loading previous data.
		
		The annual flag means that we look at annual (True) or monthly (False) data.
		
		The strictFileCheck switch checks that the data/model netcdf files exist.
			It fails if the switch is on and the files no not exist.
			
		analysisSuite chooses a set of fields to look at.
		
		
		regions selects a list of regions, default is 'all', which is the list supplied by Andy Yool. 
		
	"""	

	#print "analysis_p2p:",	jobID,clean, annual,strictFileCheck,analysisSuite,regions
	#assert 0
	
	#####
	# Switches:
	# These are some booleans that allow us to choose which analysis to run. 
	# This lets up give a list of keys one at a time, or in parrallel.
	if type(analysisSuite) == type(['Its','A','list!']):
		analysisKeys = analysisSuite

	#####
	# Switches:
	# These are some preset switches to run in series. 
	if type(analysisSuite) == type('Its_A_string'):
		analysisKeys = []
		if analysisSuite.lower() in ['all',]:	
			analysisKeys.append('Chl_CCI')			# CCI Chlorophyll	
			analysisKeys.append('Chl_pig')			# Chlorophyll from pigments (MAREDAT)
			analysisKeys.append('N')			# WOA Nitrate
			analysisKeys.append('Si')			# WOA Siliate
			analysisKeys.append('O2')			# WOA Oxygen
			analysisKeys.append('Alk')			# Glodap Alkalinity
			analysisKeys.append('DIC')			# Globap tCO2
			analysisKeys.append('AirSeaFlux')		# work in progress
			analysisKeys.append('TotalAirSeaFlux')		# work in progress		
			analysisKeys.append('IntPP_iMarNet')		# Integrated primpary production from iMarNEt
			analysisKeys.append('IntPP_OSU')		# OSU Integrated primpary production	
			analysisKeys.append('PP_OSU')			# OSU Integrated primpary production			
			analysisKeys.append('LocalExportRatio')		# Export ratio (no data)
			analysisKeys.append('GlobalExportRatio')	# Export ratio (no data)
			analysisKeys.append('TotalOMZVolume')		# Total OMZ Volume
			analysisKeys.append('OMZThickness')		# Total OMZ Volume
                        analysisKeys.append('Iron') 	            	# Iron
									
			#####	
			# Physics switches:
			analysisKeys.append('T')			# WOA Temperature
			analysisKeys.append('S')			# WOA Salinity
			analysisKeys.append('MLD')			# iFERMER Mixed Layer Depth - work in prgress

			#####
			# Switched Off

                if analysisSuite.lower() in ['level1',]:
                        analysisKeys.append('N')                        # WOA Nitrate
                        analysisKeys.append('Si')                       # WOA Siliate
                        analysisKeys.append('O2')                       # WOA Oxygen
                        analysisKeys.append('Alk')                      # Glodap Alkalinity
                        analysisKeys.append('DIC')                      # Globap tCO2
                        analysisKeys.append('AirSeaFlux')               # work in progress
                        analysisKeys.append('TotalAirSeaFlux')          # work in progress              
                        analysisKeys.append('IntPP_OSU')                # OSU Integrated primpary production    
                        analysisKeys.append('PP_OSU')                   # OSU Integrated primpary production                    
                        analysisKeys.append('LocalExportRatio')         # Export ratio (no data)
                        analysisKeys.append('GlobalExportRatio')        # Export ratio (no data)
                        analysisKeys.append('TotalOMZVolume')           # Total OMZ Volume
                        analysisKeys.append('OMZThickness')             # Total OMZ Volume
                        analysisKeys.append('Iron')                     # Iron

		
		if analysisSuite.lower() in ['debug',]:	
			#analysisKeys.append('AirSeaFlux')		# work in progress
			#analysisKeys.append('TotalAirSeaFlux')		# work in progress
			#analysisKeys.append('TotalOMZVolume')		# work in progress
			#analysisKeys.append('TotalOMZVolume50')	# work in progress			
			#analysisKeys.append('OMZThickness')		# work in progress						
			analysisKeys.append('DIC')			# work in progress									
			#analysisKeys.append('O2')			# work in progress
			#analysisKeys.append('Iron')			# work in progress	
                        #analysisKeys.append('IntPP_OSU')                # OSU Integrated primpary production    
			
		if analysisSuite.lower() in ['FullDepth',]:
			#Skip 2D fields
			#analysisKeys.append('Chl_CCI')			# CCI Chlorophyll	
			analysisKeys.append('Chl_pig')			# Chlorophyll from pigments (MAREDAT)
			analysisKeys.append('N')			# WOA Nitrate
			analysisKeys.append('Si')			# WOA Siliate
			analysisKeys.append('O2')			# WOA Oxygen
			analysisKeys.append('Alk')			# Glodap Alkalinity
			analysisKeys.append('DIC')			# Globap tCO2
			#analysisKeys.append('AirSeaFlux')		# work in progress
			#analysisKeys.append('TotalAirSeaFlux')		# work in progress		
			#analysisKeys.append('IntPP_iMarNet')		# Integrated primpary production from iMarNEt
			#analysisKeys.append('IntPP_OSU')		# OSU Integrated primpary production	
			#analysisKeys.append('PP_OSU')			# OSU Integrated primpary production			
		
			#analysisKeys.append('LocalExportRatio')		# Export ratio (no data)
			#analysisKeys.append('GlobalExportRatio')	# Export ratio (no data)
			
			#####	
			# Physics switches:
			analysisKeys.append('T')			# WOA Temperature
			analysisKeys.append('S')			# WOA Salinity
			#analysisKeys.append('MLD')			# iFERMER Mixed Layer Depth - work in prgress
		
 	
	#####
	# Some lists of region.
	# This are pre-made lists of regions that can be investigated.
	# Note that each analysis below can be given its own set of regions.	
	if regions == 'all':
  		regionList	= ['Global', 'ignoreInlandSeas',
		  		'SouthernOcean','ArcticOcean',
				'Equator10', 'Remainder',
  				'NorthernSubpolarAtlantic','NorthernSubpolarPacific',
  				]
	if regions == 'short':  	
		regionList 	= ['Global','SouthernHemisphere','NorthernHemisphere',]


	#####
	# The z_component custom command:
	# This flag sets a list of layers and metrics.
	# It's not advised to run all the metrics and all the layers, as it'll slow down the analysis.
	#if z_component in ['SurfaceOnly',]:
	layerList = ['Surface','500m','1000m',]
	metricList = ['mean','median', '10pc','20pc','30pc','40pc','50pc','60pc','70pc','80pc','90pc','min','max']

#	if z_component in ['FullDepth',]:
#		layerList = [0,2,5,10,15,20,25,30,35,40,45,50,55,60,70,]
#		metricList = ['mean','median',]
	
  	
  	



	#####
	# Location of images directory
	# the imagedir is where the analysis images will be saved.
	imagedir	 = ukp.folder('images/'+jobID+'/timeseries')
	
	#####
	# Location of shelves folder
	# The shelve directory is where the intermediate processing files are saved in python's shelve format.
	# This allows us to put away a python open to be re-opened later.
	# This means that we can interupt the analysis without loosing lots of data and processing time, 
	# or we can append new simulation years to the end of the analysis without starting from scratch each time.
	#shelvedir 	= ukp.folder('shelves/timeseries/'+jobID)

	

	#####
	# Location of data files.
	# The first thing that this function does is to check which machine it is being run. 
	# This is we can run the same code on multiple machines withouht having to make many copies of this file.
	# So far, this has been run on the following machines:
	#	PML
	#	JASMIN
	#	Charybdis (Julien's machine at NOCS)
	#
	# Feel free to add other macihines onto this list, if need be.
	machinelocation = ''
	
	#####
	# PML
	if gethostname().find('pmpc')>-1:	
		print "analysis-timeseries.py:\tBeing run at PML on ",gethostname()
		machinelocation = 'PML'
		MEDUSAFolder_pref	= "/data/euryale7/scratch/ledm/UKESM/MEDUSA/"
		NEMOFolder_pref		= "/data/euryale7/scratch/ledm/UKESM/MEDUSA/"
	
		if annual:	WOAFolder 	= "/data/euryale7/backup/ledm/Observations/WOA/annual/"
		else:		WOAFolder 	= "/data/euryale7/backup/ledm/Observations/WOA/"
		
		ObsFolder = "/data/euryale7/backup/ledm/Observations/"
		MAREDATFolder 	= ObsFolder+"/MAREDAT/MAREDAT/"
		GEOTRACESFolder = ObsFolder+"/GEOTRACES/GEOTRACES_PostProccessed/"
		TakahashiFolder = ObsFolder+"/Takahashi2009_pCO2/"
		MLDFolder	= ObsFolder+"/IFREMER-MLD/"
		iMarNetFolder	= ObsFolder+"/LestersReportData/"
		GlodapDir	= ObsFolder+"/GLODAP/"
		GLODAPv2Dir	= ObsFolder+"/GLODAPv2/GLODAPv2_Mapped_Climatologies/"
		OSUDir		= ObsFolder+"OSU/"
		CCIDir		= ObsFolder+"CCI/"
		orcaGridfn 	= '/data/euryale7/scratch/ledm/UKESM/MEDUSA/mesh_mask_eORCA1_wrk.nc'
		shelvedir 	= ukp.folder('shelves/timeseries/'+jobID)		
	#####
	# JASMIN		
	if gethostname().find('ceda.ac.uk')>-1:
		print "analysis-timeseries.py:\tBeing run at CEDA on ",gethostname()
		machinelocation = 'JASMIN'	
				
		ObsFolder 	= "/group_workspaces/jasmin/esmeval/example_data/bgc/"
		esmvalFolder 	= "/group_workspaces/jasmin2/ukesm/BGC_data/"
		shelvedir 	= ukp.folder("/group_workspaces/jasmin2/ukesm/BGC_data/"+getuser()+"/shelves/timeseries/"+jobID)
			
		#####
		# Location of model files.	
		MEDUSAFolder_pref	= ukp.folder(esmvalFolder)
		NEMOFolder_pref		= ukp.folder(esmvalFolder)
		
		#####
		# Location of data files.
		if annual:	WOAFolder 	= ukp.folder(ObsFolder+"WOA/annual")
		else:		WOAFolder 	= ukp.folder(ObsFolder+"WOA/")
		
		MAREDATFolder 	= ObsFolder+"/MAREDAT/MAREDAT/"
		GEOTRACESFolder = ObsFolder+"/GEOTRACES/GEOTRACES_PostProccessed/"
		TakahashiFolder = ObsFolder+"/Takahashi2009_pCO2/"
		MLDFolder	= ObsFolder+"/IFREMER-MLD/"
		iMarNetFolder	= ObsFolder+"/LestersReportData/"
		GlodapDir	= ObsFolder+"/GLODAP/"
		GLODAPv2Dir	= ObsFolder+"/GLODAPv2/GLODAPv2_Mapped_Climatologies/"
		OSUDir		= ObsFolder+"OSU/"
		CCIDir		= ObsFolder+"CCI/"				
		if jobID in ["xkrus",]:
			# Old school ORCA1 grid
			orcaGridfn 	='/group_workspaces/jasmin/esmeval/example_data/bgc/mesh_mask_ORCA1_75.nc'
		else:
			# New eORCA1 grid		
			orcaGridfn 	= '/group_workspaces/jasmin/esmeval/example_data/bgc/mesh_mask_eORCA1_wrk.nc'
        # MONSOON                 
        if gethostname().find('monsoon')>-1:
                print "analysis-timeseries.py:\tBeing run at the Met Office on ",gethostname()
                machinelocation = 'MONSOON'

                ObsFolder       = "/projects/ukesm/ldmora/BGC-data/"
                ModelFolder       = "/projects/ukesm/ldmora/UKESM"
                #####
                # Location of model files.      
                MEDUSAFolder_pref       = ukp.folder(ModelFolder)
                NEMOFolder_pref         = ukp.folder(ModelFolder)

                #####
                # Location of data files.
                if annual:      WOAFolder       = ukp.folder(ObsFolder+"WOA/annual")
                else:           WOAFolder       = ukp.folder(ObsFolder+"WOA/")

                MAREDATFolder   = ObsFolder+"/MAREDAT/MAREDAT/"
                GEOTRACESFolder = ObsFolder+"/GEOTRACES/GEOTRACES_PostProccessed/"
                TakahashiFolder = ObsFolder+"/Takahashi2009_pCO2/"
                MLDFolder       = ObsFolder+"/IFREMER-MLD/"
                iMarNetFolder   = ObsFolder+"/LestersReportData/"
                GlodapDir       = ObsFolder+"/GLODAP/"
                GLODAPv2Dir     = ObsFolder+"/GLODAPv2/GLODAPv2_Mapped_Climatologies/"
                OSUDir          = ObsFolder+"OSU/"
                CCIDir          = ObsFolder+"CCI/"
                if jobID in ["xkrus",]:
                        # Old school ORCA1 grid
                        orcaGridfn      =ModelFolder+'/mesh_mask_ORCA1_75.nc'
                else:
                        # New eORCA1 grid               
                        orcaGridfn      = ModelFolder+'/mesh_mask_eORCA1_wrk.nc'


	#####
	# NOC		
	if gethostname().find('charybdis')>-1:	
		print "analysis-timeseries.py:\tBeing run at NOC on ",gethostname()
		machinelocation = 'NOC'
		
		MEDUSAFolder_pref	= "/home/jpp1m13/Documents/WORKING/UKESM/Compar_Atm_forcings/netcdf_files/"
		NEMOFolder_pref		="/home/jpp1m13/Documents/WORKING/UKESM/Compar_Atm_forcings/netcdf_files/" 
	
		if annual:	WOAFolder 	= "/home/jpp1m13/Documents/WORKING/UKESM/Compar_Atm_forcings/netcdf_files/"
		else:		WOAFolder 	= "/data/euryale7/scratch/ledm/WOA/"
		
		MAREDATFolder 	= ObsFolder+"/MAREDAT/MAREDAT/"
		GEOTRACESFolder = ObsFolder+"/GEOTRACES/GEOTRACES_PostProccessed/"
		TakahashiFolder = ObsFolder+"/Takahashi2009_pCO2/"
		MLDFolder	= ObsFolder+"/IFREMER-MLD/"
		iMarNetFolder	= ObsFolder+"/LestersReportData/"
		GlodapDir	= ObsFolder+"/GLODAP/"
		GLODAPv2Dir	= ObsFolder+"/GLODAPv2/GLODAPv2_Mapped_Climatologies/"		

	#####
	# Unable to find location of files/data.	
	if not machinelocation:
		print "analysis-timeseries.py:\tFATAL:\tWas unable to determine location of host: ",gethostname()
		assert False
		


	#####
	# Coordinate dictionairy
	# These are python dictionairies, one for each data source and model.
	# This is because each data provider seems to use a different set of standard names for dimensions and time.
	# The 'tdict' field is short for "time-dictionary". 
	#	This is a dictionary who's indices are the values on the netcdf time dimension.
	#	The tdict indices point to a month number in python numbering (ie January = 0)
	# 	An example would be, if a netcdf uses the middle day of the month as it's time value:
	#		tdict = {15:0, 45:1 ...}	
	
	
	medusaCoords 	= {'t':'time_counter', 'z':'deptht', 'lat': 'nav_lat',  'lon': 'nav_lon',   'cal': '360_day',}	# model doesn't need time dict.
	maredatCoords 	= {'t':'index_t', 'z':'DEPTH',  'lat': 'LATITUDE', 'lon': 'LONGITUDE', 'cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	takahashiCoords	= {'t':'index_t', 'z':'index_z','lat': 'LAT', 'lon': 'LON', 'cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}	
	woaCoords 	= {'t':'index_t', 'z':'depth',  'lat': 'lat', 	   'lon': 'lon',       'cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}	
	glodapCoords	= {'t':'index_t', 'z':'depth',  'lat': 'latitude', 'lon': 'longitude', 'cal': 'standard','tdict':[] }
	glodapv2Coords	= {'t':'time',    'z':'Pressure','lat':'lat',      'lon':'lon',        'cal': '',        'tdict':{0:0,} }
	mldCoords	= {'t':'index_t', 'z':'index_z','lat':'lat','lon': 'lon','cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	cciCoords	= {'t':'index_t', 'z':'index_z','lat': 'lat',      'lon': 'lon', 'cal': 'standard','tdict':['ZeroToZero'] }


	def listModelDataFiles(jobID, filekey, datafolder, annual):
		if annual:
			return sorted(glob(datafolder+jobID+"/"+jobID+"o_1y_*_"+filekey+".nc"))
		else:
			return sorted(glob(datafolder+jobID+"/"+jobID+"o_1m_*_"+filekey+".nc"))

	#	if z_comp == 'FullDepth':
	#		if annual:
	#			files = sorted(glob(datafolder+jobID+"/"+jobID+"o_1y_????????_*[0,5]????_"+filekey+".nc"))
	#			if len(files)==0:
	#				files = sorted(glob(datafolder+jobID+"/"+jobID+"o_1y_????????_*????_"+filekey+".nc"))
	#			return files
	#		else:
	#			print "need to figoure out how to implement this."
	#			assert 0
#	#			return sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1m_*_"+filekey+".nc"))		
		


  	
  	#####
  	# The analysis settings:
  	# Below here is a list of analysis settings.
  	# The settings are passed to timeseriesAnalysis using a nested dictionary (called an autovivification, here).
  	# 
  	# These analysis were switched on or off at the start of the function.
  	# Each analysis requires:
  	#	model files
  	#	data files
  	#	model and data coordinate dictionaries, (defines above)
  	#	model and data details (a set of instructions of what to analyse:
  	#		name: 		field name
  	#		vars:		variable names in the netcdf
  	#		convert: 	a function to manipuate the data (ie change units, or add two fields together.
  	#				There are some standard ones in UKESMPython.py, but you can write your own here.
  	#		units: 		the units after the convert function has been applied.
  	#		layers:		which vertical layers to look at (ie, surface, 100m etc...)
  	#		regions:	which regions to look at. Can be speficied here, or use a pre-defined list (from above)
  	#		metrics:	what metric to look at:  mean, median or sum
  	#		model and data source: 	the name of source of the model/data (for plotting)
  	#		model grid: 	the model grid, usually eORCA1
  	#		the model grid file: 	the file path for the model mesh file (contains cell area/volume/masks, etc)
  	#
  	#	Note that the analysis can be run with just the model, it doesn't require a data file.
  	#	If so, just set to data file to an empty string:
  	#		av[name]['dataFile']  = ''
  	
	av = ukp.AutoVivification()
	if 'Chl_pig' in analysisKeys:
		name = 'Chlorophyll_pig'
		av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
		av[name]['dataFile'] 		= MAREDATFolder+"MarEDat20121001Pigments.nc"	
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= maredatCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['CHN','CHD'], 'convert': ukp.sums,'units':'mg C/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['Chlorophylla',], 'convert': ukp.div1000,'units':'ug/L'}
	
		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= regionList 
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'MAREDAT'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3

	if 'Chl_CCI' in analysisKeys:
		name = 'Chlorophyll_cci'
		#####
		# Not that this is the 1 degree resolution dataset, but higher resolution data are also available.
		
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)		
		if annual:	
			av[name]['dataFile'] 	= CCIDir+"ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-annual-fv2.0.nc"	
			print MEDUSAFolder_pref+"/"+jobID+"o_1y_*_ptrc_T.nc"
		else:	av[name]['dataFile'] 	= CCIDir+'ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-all-fv2.0.nc'
			
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= cciCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['CHN','CHD'], 'convert': ukp.sums,'units':'mg C/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['chlor_a',], 'convert':  ukp.NoChange,'units':'mg C/m^3'}
	
		av[name]['layers'] 		= ['Surface',] 	# CCI is surface only, it's a satellite product.
		av[name]['regions'] 		= regionList 
		av[name]['metrics']		= metricList	#['mean','median', ]

		av[name]['datasource'] 		= 'CCI'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 2		





	if 'N' in analysisKeys:
		name = 'Nitrate'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)				
		if annual:
			av[name]['dataFile'] 		=  WOAFolder+'/woa13_all_n00_01.nc'
		else:
			av[name]['dataFile'] 		=  WOAFolder+'/nitrate_monthly_1deg.nc'
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['DIN',], 'convert': ukp.NoChange,'units':'mmol N/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['n_an',], 'convert': ukp.NoChange,'units':'mmol N/m^3'}
	
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		
		#av[name]['layers'] 		= ['Surface','300m',]#'1000m',]#'Surface - 300m',]'100m',
		#av[name]['regions'] 		= regionList#['Global',]#'NorthAtlanticOcean','SouthAtlanticOcean',]#'NorthAtlantic']
		av[name]['metrics']		= metricList #['mean','median', ]

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3
		
	if 'Si' in analysisKeys:
		name = 'Silicate'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)				
		if annual:	
			av[name]['dataFile'] 		= WOAFolder+'woa13_all_i00_01.nc'
		else:
			av[name]['dataFile'] 		= WOAFolder+'wsilicate_monthly_1deg.nc'
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['SIL',],  'convert': ukp.NoChange,'units':'mmol Si/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['i_an',], 'convert': ukp.NoChange,'units':'mmol Si/m^3'}
		
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3		
	
	if 'O2' in analysisKeys:
		name = 'Oxygen'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)		
			av[name]['dataFile'] 		=  WOAFolder+'woa13_all_o00_01.nc'
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['OXY',], 'convert': ukp.NoChange,'units':'mmol O2/m^3'}	
		av[name]['datadetails']  	= {'name': name, 'vars':['o_an',], 'convert': ukp.oxconvert,'units':'mmol O2/m^3'}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3


 
	if 'OMZThickness' in analysisKeys:
		name = 'OMZThickness'
		
		if annual:
			av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
			av[name]['dataFile'] 		=  WOAFolder+'woa13_all_o00_01.nc'
		else:
			print "OMZ Thickness not implemented for monthly data"
			assert 0
			
		nc = Dataset(orcaGridfn,'r')
		thickness   = nc.variables['e3t' ][:]
		nc.close()			

		if name == 'OMZThickness':	omzthreshold = 20.
		if name == 'OMZThickness50':	omzthreshold = 50.		
		def modelOMZthickness(nc,keys):
			o2 = nc.variables[keys[0]][:].squeeze()
			totalthick = np.ma.masked_where((o2>omzthreshold)+o2[0].mask,thickness).sum(0).data
			if totalthick.max() in [0.,0]: return np.array([0.,])
			
			return np.ma.masked_where(totalthick==0., totalthick)
			#return np.ma.masked_where((arr>omzthreshold) + (arr <0.) + arr.mask,thickness).sum(0)
	

			
		def woaOMZthickness(nc,keys):
			o2 = nc.variables[keys[0]][:].squeeze() *44.661
			pthick = np.zeros_like(o2) 
			lons = nc.variables['lon'][:]
			lats = nc.variables['lat'][:]			
			zthick  = np.abs(nc.variables['depth_bnds'][:,0] - nc.variables['depth_bnds'][:,1])

			for y,lat in enumerate(lats):
			    for x,lon in enumerate(lons):			  
				pthick[:,y,x] = zthick
			totalthick = np.ma.masked_where((o2>omzthreshold)+o2[0].mask,pthick).sum(0).data
			
			if totalthick.max() in [0.,0]: return np.array([0.,])
			return np.ma.masked_where(totalthick==0., totalthick)
						
			#np.ma.masked_where(o2[0].mask, totalthick)							
			#return np.ma.masked_where(arr.mask + (arr >omzthreshold)+(arr <0.),pthick).sum(0)
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['OXY',], 'convert': modelOMZthickness,'units':'m'}
		av[name]['datadetails']  	= {'name': name, 'vars':['o_an',], 'convert': woaOMZthickness,'units':'m'}
	
		av[name]['layers'] 		= ['Surface',] 
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn	
		av[name]['Dimensions']		= 2		
		
		
		

	if 'TotalOMZVolume' in analysisKeys or 'TotalOMZVolume50' in analysisKeys:
	    for name in ['TotalOMZVolume','TotalOMZVolume50']:
	        if name not in analysisKeys: continue
		if annual:
			av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
			av[name]['dataFile'] 		=  WOAFolder+'woa13_all_o00_01.nc'
		else:
			print "OMZ volume not implemented for monthly data"
			assert 0
			
		nc = Dataset(orcaGridfn,'r')
		try:	
			vol   = nc.variables['pvol' ][:]
			tmask = nc.variables['tmask'][:]
		except:
			tmask = nc.variables['tmask'][:]			
			area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
			pvol = nc.variables['e3t'][:] *area			
			pvol = np.ma.masked_where(tmask==0,pvol)
		nc.close()			

		if name == 'TotalOMZVolume':	omzthreshold = 20.
		if name == 'TotalOMZVolume50':	omzthreshold = 50.		
		def modelTotalOMZvol(nc,keys):
			arr = nc.variables[keys[0]][:].squeeze()
			return np.ma.masked_where((arr>omzthreshold) + pvol.mask,pvol).sum()
	

			
		def woaTotalOMZvol(nc,keys):
			arr = nc.variables[keys[0]][:].squeeze() *44.661
			#area = np.zeros_like(arr[0])
			pvol = np.zeros_like(arr) 
			#np.ma.masked_wjhere(arr.mask + (arr <0.)+(arr >1E10),np.zeros_like(arr))
			lons = nc.variables['lon'][:]
			lats = nc.variables['lat'][:]			
			#lonbnds = nc.variables['lon_bnds'][:]
			latbnds = nc.variables['lat_bnds'][:]
			zthick  = np.abs(nc.variables['depth_bnds'][:,0] - nc.variables['depth_bnds'][:,1])
			
			for y,lat in enumerate(lats):
				area = ukp.Area([latbnds[y,0],0.],[latbnds[y,1],1.])
				for z,thick in enumerate(zthick):
					pvol[z,y,:] = np.ones_like(lons)*area*thick
					
			return np.ma.masked_where(arr.mask + (arr >omzthreshold)+(arr <0.),pvol).sum()
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['OXY',], 'convert': modelTotalOMZvol,'units':'m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['o_an',], 'convert': woaTotalOMZvol,'units':'m^3'}
	
		av[name]['layers'] 		= ['Surface',] 
		av[name]['regions'] 		= ['Global',]
		av[name]['metrics']		= ['sum', ]

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn	
		av[name]['Dimensions']		= 1	
	
	if 'DIC' in analysisKeys:
	
		def convertkgToM3(nc,keys):
			return nc.variables[keys[0]][:]* 1.027
				
		name = 'DIC'
		
		av[name]['modelFiles'] 		= listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)				
		av[name]['dataFile'] 		= GLODAPv2Dir+ 'GLODAPv2.tco2.historic.nc'
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= glodapv2Coords
	
		av[name]['modeldetails'] 	= {'name': 'DIC', 'vars':['DIC',],  'convert': ukp.NoChange,'units':'mmol C/m^3'}
		av[name]['datadetails']  	= {'name': 'DIC', 'vars':['tco2',], 'convert': ukp.convertkgToM3,'units':'mmol C/m^3'}
	
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GLODAP'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn		
		av[name]['Dimensions']		= 3
		
	if 'Alk' in analysisKeys:
		def convertmeqm3TOumolkg(nc,keys):
			return nc.variables[keys[0]][:]* 1.027
		
		name = 'Alkalinity'
		if annual:		
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)		
			av[name]['dataFile'] 	=  GlodapDir+'Alk.nc'
		else:
			print "Alkalinity data not available for monthly Analysis"
			assert 0
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= glodapCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['ALK',], 'convert': ukp.NoChange,'units':'meq/m^3',}
		av[name]['datadetails']  	= {'name': name, 'vars':['Alk',], 'convert': convertmeqm3TOumolkg,'units':'meq/m^3',}
	
	#	av[name]['layers'] 		=  ['Surface','100m','300m','1000m',]
	#	av[name]['regions'] 		= regionList
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList		
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GLODAP'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3					


	if 'AirSeaFlux' in analysisKeys:
	
		#nc = Dataset(orcaGridfn,'r')
		#area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		#nc.close()
		
		def eOrcaTotal(nc,keys):
			factor =  12./1000. #/ 1.E12
			arr = nc.variables['CO2FLUX'][:].squeeze()	# mmolC/m2/d
			#if arr.ndim ==3:
			#	for i in np.arange(arr.shape[0]):
			#		arr[i] = arr[i]*area
			#elif arr.ndim ==2: arr = arr*area
			#else: assert 0
			return arr * factor
					
		def takaTotal(nc,keys):
			arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
			arr = -1.E12* arr / 365.				#g Carbon/day
			area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
			fluxperarea = arr/area
			#arr = arr*area #* 1.E24 	# converts area into m^2
			#print arr.sum(), arr.sum()*factor
			return fluxperarea
			# area 10^6 km^2
			# flux:  10^15 g Carbon month^-1. (GT)/m2/month

			
		name = 'AirSeaFluxCO2'

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)								
		if annual:
			av[name]['dataFile'] 		=  TakahashiFolder+'takahashi_2009_Anual_sumflux_2006c_noHead.nc'		
		else:	
			av[name]['dataFile'] 		=  TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'				
			print "Air Sea Flux CO2 monthly not implemented"
			assert 0
			#av[name]['dataFile'] 		=  TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= takahashiCoords
		av[name]['modeldetails'] 	= {'name': 'AirSeaFluxCO2', 'vars':['CO2FLUX',], 'convert': eOrcaTotal,'units':'g C/m2/day'}
		av[name]['datadetails']  	= {'name': 'AirSeaFluxCO2', 'vars':['TFLUXSW06','AREA_MKM2'], 'convert': takaTotal,'units':'g C/m2/day'}
		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 2
							
	if 'TotalAirSeaFlux' in analysisKeys:
		name = 'TotalAirSeaFluxCO2'	
		nc = Dataset(orcaGridfn,'r')
		area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		nc.close()
		
		def eOrcaTotal(nc,keys):
			factor =  365.25 * 12./1000. #/ 1.E12
			arr = nc.variables['CO2FLUX'][:].squeeze() * factor	# mmolC/m2/d
			if arr.ndim ==3:
				for i in np.arange(arr.shape[0]):
					arr[i] = arr[i]*area
			elif arr.ndim ==2: arr = arr*area
			else: assert 0
			return arr.sum()
					
		def takaTotal(nc,keys):
			arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
			arr = -1.E12* arr #/ 365.				#g Carbon/day
			#area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
			#fluxperarea = arr/area
			return arr.sum()
			# area 10^6 km^2
			# flux:  10^15 g Carbon month^-1. (GT)/m2/month

			


		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)								
		if annual:
			av[name]['dataFile'] 		=  TakahashiFolder+'takahashi_2009_Anual_sumflux_2006c_noHead.nc'		
		else:	
			av[name]['dataFile'] 		=  TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'				
			print "Air Sea Flux CO2 monthly not implemented"
			assert 0
			#av[name]['dataFile'] 		=  TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= takahashiCoords
		av[name]['modeldetails'] 	= {'name': 'AirSeaFluxCO2', 'vars':['CO2FLUX',], 'convert': eOrcaTotal,'units':'g C/yr'}
		av[name]['datadetails']  	= {'name': 'AirSeaFluxCO2', 'vars':['TFLUXSW06','AREA_MKM2'], 'convert': takaTotal,'units':'g C/yr'}
		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= ['Global',]
		av[name]['metrics']		= ['sum',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 2					
										
					

	if 'IntPP_iMarNet' in analysisKeys:
		name = 'IntegratedPrimaryProduction_1x1'		
		
		def medusadepthInt(nc,keys):
			return (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:])* 6.625 * 12.011 / 1000.	

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)										
		#av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_diad_T.nc"))
		av[name]['dataFile'] 		= iMarNetFolder+"/PPint_1deg.nc"

				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= maredatCoords
	
		av[name]['modeldetails'] 	= {'name': 'IntPP', 'vars':['PRN' ,'PRD'], 'convert': medusadepthInt,'units':'mg C/m^3'}
		#av[name]['datadetails']  	= {'name': 'IntPP', 'vars':['Chlorophylla',], 'convert': ukp.div1000,'units':'ug/L'}
		av[name]['datadetails']  	= {'name': 'IntPP', 'vars':['PPint',], 'convert': ukp.div1000,'units':'[ug/L/d'}		

	
		av[name]['layers'] 		= ['Surface',]#'100m','200m','Surface - 1000m','Surface - 300m',]#'depthint']
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'MAREDAT'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 2		
		
	if 'PP_OSU' in analysisKeys:
		nc = Dataset(orcaGridfn,'r')
		area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		nc.close()
		def medusadepthInt(nc,keys):
			#	 mmolN/m2/d        [mg C /m2/d]   [mgC/m2/yr] [gC/m2/yr]     Gt/m2/yr
			factor = 1.		* 6.625 * 12.011 #* 365.	      / 1000.   /     1E15
			arr = (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:]).squeeze()*factor
			#if arr.ndim ==3:
			#	for i in np.arange(arr.shape[0]):
			#		arr[i] = arr[i]*area
			#elif arr.ndim ==2: arr = arr*area
			#else: assert 0
			return arr
			
		
				
		name = 'IntegratedPrimaryProduction_OSU'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)								
			av[name]['dataFile'] 		= OSUDir +"/standard_VGPM.SeaWIFS.global.average.nc"
#		else:
#			print "" 
			
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= glodapCoords



		nc = Dataset(av[name]['dataFile'] ,'r')
		lats = nc.variables['latitude'][:]
		osuareas = np.zeros((1080, 2160))
		osuarea = (111100. / 6.)**2. # area of a pixel at equator. in m2
		for a in np.arange(1080):osuareas[a] = np.ones((2160,))*osuarea*np.cos(np.deg2rad(lats[a]))
		
		
		def osuconvert(nc,keys):
			arr = nc.variables[keys[0]][:,:,:] 
			#tlen = arr.shape[0]
			
			#arr  = arr.sum(0)/tlen * 365.	/ 1000. /     1E15
			#if arr.ndim ==3:
			#	for i in np.arange(arr.shape[0]):
			#		arr[i] = arr[i]*osuarea
			#elif arr.ndim ==2: arr = arr*osuarea
			#else: assert 0
			return arr
						
			

	
		av[name]['modeldetails'] 	= {'name': 'IntPP', 'vars':['PRN' ,'PRD'], 'convert': medusadepthInt,'units':'mgC/m^2/day'}
		av[name]['datadetails']  	= {'name': 'IntPP', 'vars':['NPP',], 'convert': osuconvert,'units':'mgC/m^2/day'}
	
		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= 'OSU'
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 2

	#####
	# Total 
	if 'IntPP_OSU' in analysisKeys:
		noOSU = True
		nc = Dataset(orcaGridfn,'r')
		area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		nc.close()
		def medusadepthInt(nc,keys):
			#	 mmolN/m2/d        [mg C /m2/d]   [mgC/m2/yr] [gC/m2/yr]     Gt/m2/yr
			factor = 1.		* 6.625 * 12.011 * 365.	      / 1000.   /     1E15
			arr = (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:]).squeeze()*factor
			if arr.ndim ==3:
				for i in np.arange(arr.shape[0]):
					arr[i] = arr[i]*area
			elif arr.ndim ==2: arr = arr*area
			else: assert 0
			return arr
			
		name = 'TotalIntegratedPrimaryProduction'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)							
			if noOSU:	av[name]['dataFile']            = ''
			else:		av[name]['dataFile'] 		= OSUDir +"/standard_VGPM.SeaWIFS.global.average.nc"
			
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= glodapCoords

                av[name]['modeldetails']        = {'name': 'IntPP', 'vars':['PRN' ,'PRD'], 'convert': medusadepthInt,'units':'Gt/m2/yr'}
		if noOSU: 
	                av[name]['datadetails']         = {'name': '', 'units':''}

		else:
			nc = Dataset(av[name]['dataFile'] ,'r')
			lats = nc.variables['latitude'][:]
			osuareas = np.zeros((1080, 2160))
			osuarea = (111100. / 6.)**2. # area of a pixel at equator. in m2
			for a in np.arange(1080):osuareas[a] = np.ones((2160,))*osuarea*np.cos(np.deg2rad(lats[a]))
		
		
			def osuconvert(nc,keys):
				arr = nc.variables[keys[0]][:,:,:] 
				tlen = arr.shape[0]
				arr  = arr.sum(0)/tlen * 365.	/ 1000. /     1E15
				if arr.ndim ==3:
					for i in np.arange(arr.shape[0]):
						arr[i] = arr[i]*osuarea
				elif arr.ndim ==2: arr = arr*osuarea
				else: assert 0
				return arr
	               	av[name]['datadetails']         = {'name': 'IntPP', 'vars':['NPP',], 'convert': osuconvert,'units':'Gt/m2/yr'}

		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= ['sum',]
		if noOSU:	av[name]['datasource']          = ''
		else:		av[name]['datasource'] 		= 'OSU'
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn		
		av[name]['Dimensions']		= 1
				
	if 'GlobalExportRatio' in analysisKeys:
		
		def calcExportRatio(nc,keys):
			a = (nc.variables['SDT__100'][:] +nc.variables['FDT__100'][:]).sum()/ (nc.variables['PRD'][:] +nc.variables['PRN'][:] ).sum()
			#a = np.ma.masked_where(a>1.01, a)
			return 	a
			
		name = 'ExportRatio'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)								
				
		av[name]['dataFile'] 		= ""
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= maredatCoords
		av[name]['modeldetails'] 	= {'name': name, 'vars':['SDT__100','FDT__100' ,'PRD','PRN',], 'convert': calcExportRatio,'units':''}
		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= ['Global',]
		av[name]['metrics']		= ['sum',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn		
		av[name]['Dimensions']		= 1
		
	if  'LocalExportRatio' in analysisKeys:
		
		def calcExportRatio(nc,keys):
			a = (nc.variables['SDT__100'][:] +nc.variables['FDT__100'][:])/ (nc.variables['PRD'][:] +nc.variables['PRN'][:] )
			a = np.ma.masked_where(a>1.01, a)
			return 	a
			
		name = 'LocalExportRatio'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', MEDUSAFolder_pref, annual)								
				
		av[name]['dataFile'] 		= ""
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= maredatCoords
		av[name]['modeldetails'] 	= {'name': name, 'vars':['SDT__100','FDT__100' ,'PRD','PRN',], 'convert': calcExportRatio,'units':''}
		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		= ['Surface',]#'100m','200m','Surface - 1000m','Surface - 300m',]#'depthint']
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn	
		av[name]['Dimensions']		= 2
		
	if  'Iron' in analysisKeys:
		
		name = 'Iron'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', MEDUSAFolder_pref, annual)								
				
		av[name]['dataFile'] 		= ""
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= maredatCoords
		av[name]['modeldetails']	= {'name': name, 'vars':['FER',], 'convert': ukp.NoChange, 'units':'mmolFe/m3'}
		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3
						
	if 'T' in analysisKeys:
		name = 'Temperature'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', MEDUSAFolder_pref, annual)										
		if annual:		
			#av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'woa13_decav_t00_01v2.nc'
		else:
			#av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1m_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'temperature_monthly_1deg.nc'
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['votemper',], 'convert': ukp.NoChange,'units':'degrees C'}
		av[name]['datadetails']  	= {'name': name, 'vars':['t_an',], 'convert': ukp.NoChange,'units':'degrees C'}
	
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList	
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3
					
	if 'S' in analysisKeys:
		name = 'Salinity'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', MEDUSAFolder_pref, annual)												
		if annual:
			#av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'woa13_decav_s00_01v2.nc'
		else:
			#av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1m_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'salinity_monthly_1deg.nc'
			
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= woaCoords
	
		av[name]['modeldetails'] 	= {'name': name, 'vars':['vosaline',], 'convert': ukp.NoChange,'units':'PSU'}	
		av[name]['datadetails']  	= {'name': name, 'vars':['s_an',], 'convert': ukp.NoChange,'units':'PSU'}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList		
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 3
		
	if 'MLD' in analysisKeys:
		
		def mldapplymask(nc,keys):
			mld = nc.variables[keys[0]][:]
			return np.ma.masked_where((np.tile(nc.variables[keys[1]][:],(12,1,1))==0.)+mld.mask+(mld==1.E9),mld)	
		nc = Dataset(orcaGridfn,'r')
		depth = nc.variables['nav_lev'][:]#
		nc.close()
		
	#	depth10 = x
	#	ndepth = range(0,50,1)
	#	ndepth.extend(range(50,80,2))
	#	ndepth.extend(range(80,110,3))
	#	ndepth.extend(range(110,200,5))
	#	ndepth.extend(range(200,500,10))
	#	ndepth.extend(range(500,1000,50))
	#	ndepth.extend(range(1000,2000,100))
	#	ndepth.extend(range(2000,6000,200))

		def calcMLD(nc,keys):
			#mlds = np.arange(nc.zeros_like(nc.variables[keys[0]][)

			temp = nc.variables[keys[0]][:,:,:,:]
			f_out = interp1d(depth[7:9],temp[7:9], axis=1)
			tcrit = 0.2
			t10m =  f_out(10.) 
			t10m = np.ma.masked_where(t10m>1E20, t10m) - tcrit
			
			#nc.variables[keys[0]][:,depth10,:,:]
			# linear regression to extrapolate below this level to find the first? 
			f_out = interp1d(temp, depth, axis=1)
			#t_out = f_out(newdepth)

			

			
		name = 'MLD'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', MEDUSAFolder_pref, annual)												
		#av[name]['modelFiles']  	= sorted(glob(MEDUSAFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
		av[name]['dataFile'] 		= MLDFolder+"mld_DT02_c1m_reg2.0.nc"
			#MLD_DT02 = depth where (T = T_10m +/- 0.2 degC)
 	
				
		av[name]['modelcoords'] 	= medusaCoords 	
		av[name]['datacoords'] 		= mldCoords
	
		av[name]['modeldetails'] 	= {'name': 'mld', 'vars':['somxl010',],   'convert': ukp.NoChange,'units':'m'}	
		#av[name]['modeldetails'] 	= {'name': 'mld', 'vars':['votemper',],   'convert': calcMLD,'units':'m'}	
		av[name]['datadetails']  	= {'name': 'mld', 'vars':['mld','mask',], 'convert': mldapplymask,'units':'m'}
	
		av[name]['layers'] 		= ['Surface',]#'Surface - 1000m','Surface - 300m',]#'depthint']
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'IFREMER'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= orcaGridfn
		av[name]['Dimensions']		= 2		
			
				

  	#####
  	# Calling timeseriesAnalysis
	# This is where the above settings is passed to timeseriesAnalysis, for the actual work to begin.
	# We loop over all fiels in the first layer dictionary in the autovificiation, av.
	#	
	# Once the timeseriesAnalysis has completed, we save all the output shelves in a dictionairy.
	# At the moment, this dictioary is not used, but we could for instance open the shelve to highlight specific data,
	#	(ie, andy asked to produce a table showing the final year of data.
	
	shelves = {}
	shelves_insitu={}
	for name in av.keys():
		print "------------------------------------------------------------------"	
		print "analysis-Timeseries.py:\tBeginning to call timeseriesAnalysis for ", name

		if len(av[name]['modelFiles']) == 0:
			print "analysis-Timeseries.py:\tWARNING:\tmodel files are not found:",av[name]['modelFiles'] 
			if strictFileCheck: assert 0		

		modelfilesexists = [os.path.exists(f) for f in av[name]['modelFiles'] ]
		if False in modelfilesexists:
			print "analysis-Timeseries.py:\tWARNING:\tnot model files do not all exist:",av[name]['modelFiles'] 
			if strictFileCheck: assert 0
			
			
		if av[name]['dataFile']!='':
		   if not os.path.exists(av[name]['dataFile']):
			print "analysis-Timeseries.py:\tWARNING:\tdata file is not found:",av[name]['dataFile']
			if strictFileCheck: assert 0

#		profa = profileAnalysis(
#			av[name]['modelFiles'], 
#			av[name]['dataFile'],
#			dataType	= name,
 # 			modelcoords 	= av[name]['modelcoords'],
  #			modeldetails 	= av[name]['modeldetails'],
  #			datacoords 	= av[name]['datacoords'],
  #			datadetails 	= av[name]['datadetails'],								
#			datasource	= av[name]['datasource'],
#			model 		= av[name]['model'],
#			jobID		= jobID,
#			layers	 	= list(np.arange(102)),	# 102 because that is the number of layers in WOA Oxygen
#			regions	 	= av[name]['regions'],			
#			metrics	 	= ['mean',],
#			workingDir	= shelvedir,
#			imageDir	= imagedir,					
#			grid		= av[name]['modelgrid'],
#			gridFile	= av[name]['gridFile'],
#			clean 		= clean,
#		)
			#shelves[name] = profa.shelvefn
			#shelves_insitu[name] = profa.shelvefn_insitu				
		
		if av[name]['Dimensions'] == 3:
			profa = profileAnalysis(
				av[name]['modelFiles'], 
				av[name]['dataFile'],
				dataType	= name,
	  			modelcoords 	= av[name]['modelcoords'],
	  			modeldetails 	= av[name]['modeldetails'],
	  			datacoords 	= av[name]['datacoords'],
	  			datadetails 	= av[name]['datadetails'],								
				datasource	= av[name]['datasource'],
				model 		= av[name]['model'],
				jobID		= jobID,
				layers	 	= list(np.arange(102)),	# 102 because that is the number of layers in WOA Oxygen
				regions	 	= av[name]['regions'],			
				metrics	 	= ['mean',],
				workingDir	= shelvedir,
				imageDir	= imagedir,					
				grid		= av[name]['modelgrid'],
				gridFile	= av[name]['gridFile'],
				clean 		= clean,
			)
			#shelves[name] = profa.shelvefn
			#shelves_insitu[name] = profa.shelvefn_insitu
			
		tsa = timeseriesAnalysis(
			av[name]['modelFiles'], 
			av[name]['dataFile'],
			dataType	= name,
  			modelcoords 	= av[name]['modelcoords'],
  			modeldetails 	= av[name]['modeldetails'],
  			datacoords 	= av[name]['datacoords'],
  			datadetails 	= av[name]['datadetails'],								
			datasource	= av[name]['datasource'],
			model 		= av[name]['model'],
			jobID		= jobID,
			layers	 	= av[name]['layers'],
			regions	 	= av[name]['regions'],			
			metrics	 	= av[name]['metrics'],
			workingDir	= shelvedir,
			imageDir	= imagedir,					
			grid		= av[name]['modelgrid'],
			gridFile	= av[name]['gridFile'],
			clean 		= clean,
		)
		
		#shelves[name] = tsa.shelvefn
		#shelves_insitu[name] = tsa.shelvefn_insitu


		

def singleTimeSeriesProfile(jobID,key):
	
	FullDepths = ['T','S', 'Chl_pig','N','Si','O2','Alk','DIC','Iron',]
	if key in FullDepths:
		analysis_timeseries(jobID =jobID,analysisSuite=[key,], )

def singleTimeSeries(jobID,key,):
#	try:
		analysis_timeseries(jobID =jobID,analysisSuite=[key,], )#clean=1)
#	except:
#		print "Failed singleTimeSeries",(jobID,key)
#		print "Error: %s" % sys.exc_info()[0]	
		
				

def main():
	try:	jobID = argv[1]
	except:	
		jobID = "u-ab749"

	if 'debug' in argv[1:]:	suite = 'debug'
	elif 'all' in argv[1:]:	suite = 'all'
	elif 'level1' in argv[1:]:suite='level1'
	else:			suite = 'all'
		
	
	analysis_timeseries(jobID =jobID,analysisSuite=suite, )#clean=1)			
	#if suite == 'all':
	#analysis_timeseries(jobID =jobID,analysisSuite='FullDepth', z_component = 'FullDepth',)#clean=1)  

if __name__=="__main__":
	main()	
                    

		
	
	
	
	
	 
