from calendar import month_name

"""	This is a dictionary of all the terms that you'd need to pick out.
	pftnames['Model Name']['Functional type']['currency']

"""


class AutoVivification(dict):
    """Implementation of perl's autovivification feature.
    	This class allows you to automate the creating of layered dictionaries.
    """
    def __getitem__(self, item):
        try: return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
            
            
pftnames = AutoVivification()
pftnames['ERSEM']['diatoms']['c'] = 'P1c'
pftnames['ERSEM']['diatoms']['n'] = 'P1n'
pftnames['ERSEM']['diatoms']['p'] = 'P1p'
pftnames['ERSEM']['diatoms']['f'] = 'P1f'
pftnames['ERSEM']['diatoms']['s'] = 'P1s'
pftnames['ERSEM']['diatoms']['chl'] = 'Chl1'

pftnames['ERSEM' ]['total']['chl'] = 'chl'
pftnames['MEDUSA']['total']['chl'] = 'CHL'

pftnames['MEDUSA']['diatoms']['n'] = ['']
pftnames['MEDUSA']['diatoms']['f'] = ['']
pftnames['MEDUSA']['diatoms']['s'] = ['']


# overloading different names with the same dict.
pftnames['E'] = pftnames['ERSEM']
pftnames['e'] = pftnames['ERSEM']
pftnames['ersem'] = pftnames['ERSEM']
pftnames['M'] = pftnames['MEDUSA']
pftnames['m'] = pftnames['MEDUSA']
pftnames['medusa'] = pftnames['MEDUSA']






def getLongName(text):
	if type(text) in [type(['a','b',]),type(('a','b',))]:
		out = ''
		for t in text:out+=getLongName(t)+' '
		return out

			 		
  	if text == 'tempTransect':	return "Pacific Transect Temperature"
  	if text == 'tempSurface':	return "Surface Temperature"
  	if text == 'tempAll':		return "Temperature"  	
  	if text == 'temp100m':		return "Temperature (100m deep)"  	
  	if text == 'temp200m':		return "Temperature (200m deep)"  
  	if text == 'temp500m':		return "Temperature (500m deep)"  	
  	if text == 'temp1000m':		return "Temperature (1000m deep)"  	  		  	  	

  	if text == 'salTransect':	return "Pacific Transect Salinity"
  	if text == 'salSurface':	return "Surface Salinity"
  	if text == 'salAll':		return "Salinity"  	
  	if text == 'sal100m':		return "Salinity (100m deep)"  	
  	if text == 'sal200m':		return "Salinity (200m deep)"  	  	  	
  	if text == 'sal500m':		return "Salinity (500m deep)"  	
  	if text == 'sal1000m':		return "Salinity (1000m deep)"  	  	  	
  	
  	if text == 'nitrateTransect':	return "Pacific Transect Nitrate (WOA14)"
  	if text == 'nitrateSurface':	return "Surface Nitrate (WOA14)"
  	if text == 'nitrateAll':	return "Nitrate (WOA14)"  	
  	if text == 'nitrate100m':	return "Nitrate (100m deep)"  	  	
  	if text == 'nitrate200m':	return "Nitrate (200m deep)"  
  	if text == 'nitrate500m':	return "Nitrate (500m deep)"  	  	
  	  		  	  	
  	if text == 'phosphateTransect':	return "Pacific Transect Phosphate"
  	if text == 'phosphateSurface':	return "Surface Phosphate"
  	if text == 'phosphateAll':	return "Phosphate"  	
  	if text == 'phosphate100m':	return "Phosphate (100m deep)"  	  	
  	if text == 'phosphate200m':	return "Phosphate (200m deep)"    	
  	if text == 'phosphate500m':	return "Phosphate (500m deep)"    	  	
  	if text == 'silicateTransect':	return "Pacific Transect Silicate"
  	if text == 'silicateSurface':	return "Surface Silicate"
  	if text == 'silicateAll':	return "Silicate"  	
  	if text == 'silicate100m':	return "Silicate (100m deep)"  	  	
  	if text == 'silicate200m':	return "Silicate (200m deep)"    	
  	if text == 'silicate500m':	return "Silicate (500m deep)"    	
  	  	
  	if text == 'nitTransect': return "Pacific Transect Nitrate (WOA40)"
  	if text == 'nitSurface': return "Surface Nitrate (WOA40)"
    	if text == 'GEOTRACES':	return "GEOTRACES"  		
  	if text == 'iron':	return "Iron"  	
  	
     	if text == 'IFREMER-MLD':	return "IFREMER MLD"
  	if text == 'mld_DT02':		return 'MLD: Fixed Threshold Temperature '
  	if text == 'mld_DR003':		return 'MLD: Fixed Threshold Density'
  	if text == 'mld_DReqDTm02':	return 'MLD: Variable Threshold Density'  	  	
 
  	if text == 'All':	return 'Global'
  	if text == 'Best':	return 'Best'  	
  	if text == 'Standard':	return 'Standard'  	  	
  	if text =='SalArtifact':return 'Salinity Artifact (<15psu)'
  	if text =='NitArtifact':return 'Nitrogen Artifact'  	
  	if text =='OffAxis':	return 'Off Axis'  	
  	if text =='Depth':	return 'Depth >200m'  	
  	if text =='Shallow':	return 'Depth <200m'
  	
  	if text =='Depth_0-10m':	return 'Depth <10m'
  	if text =='Depth_10-20m':	return '10m <= Depth < 20m'
  	if text =='Depth_20-50m':	return '20m <= Depth < 50m'
  	if text =='Depth_50-100m':	return '50m <= Depth < 100m'
  	if text =='Depth_100-500m':	return '100m <= Depth < 500m'
  	if text =='Depth_500m':		return 'Depth > 500m'  	  	
  	
   	if text =='maskBelowBathy':	return 'Masked Below Bathymetery' 
   	if text =='OnShelf':		return 'On Shelf'
   	if text =='OffShelf':		return 'Off Shelf'    	   	  	
  	  	
   	if text =='nonZero':	return 'Non zero' 
   	if text =='aboveZero':	return ''#> zero'    	
   	if text =='1-99pc':	return '1-99 percentiles' 
   	if text =='5-95pc':	return '5-95 percentiles' 
   	if text =='0-99pc':	return 'up to 99th percentile' 
   
   	if text =='TypicalIron':	return 'Iron < 4 umol m^-3' 
   	   	
   	if text =='0-1pc':	return '0-1 percentiles' 
   	if text =='1-5pc':	return '1-5 percentiles' 
   	if text =='5-25pc':	return '5-25 percentiles' 
   	if text =='25-40pc':	return '25-40 percentiles' 
   	if text =='40-60pc':	return '40-60 percentiles' 
   	if text =='60-75pc':	return '60-75 percentiles' 
   	if text =='75-95pc':	return '75-95 percentiles' 
   	if text =='95-99pc':	return '95-99 percentiles' 
   	if text =='99-100pc':	return '99-100 percentiles' 

	if text =='Overestimate_2sig': return "Overestimate 2 sigma"
	if text =='Overestimate_3sig': return "Overestimate 3 sigma"
	if text =='Underestimate_2sig': return "Overestimate 2 sigma"
	if text =='Underestimate_3sig': return "Overestimate 3 sigma"			
	   	
  	if text in ['Tropics','Temperate','Arctic','Surface','Depth', 'SalArtifact','OffAxis','pCO2',]:return text
	if text in ['Overestimate','Underestimate','Matched', 'Arctic','Tropics','Temperate', 'Surface',]:return text
	
  	if text == 'SurfaceNoArtics':	return ""
	
  	if text == 'NorthTemperate':	return "North Temperate"
  	if text == 'SouthTemperate':	return "South Temperate"  	
  	if text == 'NorthTropics':	return "North Tropics"
  	if text == 'SouthTropics':	return "South Tropics"  	
  	if text == 'NorthArctic':	return "North Arctic"
  	if text == 'Antarctic':		return "Antarctic"  	
  	if text == 'Equatorial':	return "Equatorial"  	
  	if text == 'AMT':		return "AMT"  	  	
  	if text == 'AMTTop40m':		return "AMT (Top 40m)"  	  	
   	if text == 'AMTTop200m':	return "AMT (Top 200m)"  	  	 	
   	
  	if text == 'BlackSea':		return "Black Sea"  
  	if text == 'RedSea':		return "Red Sea"  
  	if text == 'BalticSea':		return "Baltic Sea"  
   	if text == 'PersianGulf':	return "Persian Gulf"   	
  	  	  	 		
  	if text == 'ignoreBlackSea':	return "No Black Sea"  	  	
  	if text == 'ignoreRedSea':	return "No Red Sea"  	  	
  	if text == 'ignoreBalticSea':	return "No Baltic Sea"  
   	if text == 'ignorePersianGulf':	return "No Persian Gulf"   	  		  	
  	if text == 'ignoreInlandSeas':	return "No Inland Seas"
  	if text == 'ignoreMediteranean':return "No Mediteranean"  	


  	if text == 'ArcticOcean':	return "Arctic Ocean"	  		  	
  	if text == 'AntarcticOcean':	return "Antarctic Ocean" 		  	
  	if text == 'NorthAtlanticOcean':return "North Atlantic Ocean"
  	if text == 'SouthAtlanticOcean':return "South Atlantic Ocean"	  		  	
  	if text == 'NorthPacificOcean':	return "North Pacific Ocean"		  	
  	if text == 'SouthPacificOcean':	return "South Pacific Ocean"	  		  	
  	if text == 'IndianOcean':	return "Indian Ocean"
  	if text == 'ignoreExtraArtics':	return "No Arctic Oceans (50 degrees)"  	
  	if text == 'ignoreMoreArtics':	return "No Arctic Oceans (60 degrees)"
  	if text == 'ignoreMidArtics':	return "No Arctic Oceans (65 degrees)"  
  	if text == 'ignoreArtics':	return "No Arctic Oceans (70 degrees)" 
  	
  	if text == 'Top40m':	return "Top 40m"
  	if text == 'Top200m':	return "Top 200m"
  	if text == 'Top40mNoArtics':	return "Top 40m (No Arctics)"
  	if text == 'Top200mNoArtics':	return "Top 200m  (No Arctics)"

  	if text == 'Transect':	return "Pacifc Transect"  	
  	if text == 'AtlanticTransect':	return "Atlantic Transect"  
  		  	
  	if text == 'NoShelf':	return "No Shelf"  
  	if text == 'NoShelfTop40':	return "No Shelf (Top 40m)"    	
  	if text == 'NoShelfSurface':	return "No Shelf (Surface)"    	  	

  	  		  	
  	if text == 'picophyto':	return 'Picophytoplankton'
  	if text == 'microzoo':	return 'Microzooplankton'
  	if text == 'mesozoo':	return 'Mesozooplankton'
  	if text == 'diatoms':	return 'Diatoms'
  	if text ==  'bac': 	return 'Bacteria'
  	if text ==  'chl': 	return 'Chlorophyll'  	
  	if text ==  'nitrate': 	return 'WOA nitrate'  	

  	if text ==  'Ersem': 	return 'ERSEM'  	  	
  	if text ==  'Ersem-1891': return 'ERSEM (1891)'    	  	
  	if text ==  'Ersem-1893': return 'ERSEM (1893)'  	
  	if text ==  'Ersem-1894': return 'ERSEM (1894)'
  	if text ==  'Ersem-1895': return 'ERSEM (1895)'  	
  	if text ==  'Ersem-1899': return 'ERSEM (1899)'  	  	
  	if text ==  'Ersem-1909': return 'ERSEM (1909)'
  	if text ==  'Ersem-1948': return 'ERSEM (1948)'  
  	if text ==  'Ersem-1982': return 'ERSEM (1982)'    	
  	if text ==  'Ersem-2001': return 'ERSEM (2001)'    		  	
  	if text ==  'Ersem-2006': return 'ERSEM (2006)'    		
  	if text ==  'Ersem-clim': return 'ERSEM'  	
  	if text ==  'Ersem-clim_97-07': return 'ERSEM (\'97-\'07)'
  	if text ==  'Ersem-2001': return 'ERSEM (2001)'    	  	
  	if text ==  'Ersem-HighResp': return 'ERSEM (High Respiration)'  	  	   	  	 
  	if text ==  'Maredat': 	return 'Maredat'  	  	
  	if text ==  'WOA': 	return 'WOA'  	  	
  	if text ==  'Takahashi': 	return 'Takahashi 2009'  	  	  	
  	if text ==  'Seawifs': 		return 'Seawifs'  	  	
  	if text ==  'Seawifs-micro': 	return 'Seawifs Microphyto. chl.'  	  	
  	if text ==  'Seawifs-nano': 	return 'Seawifs Nanophyto. chl.'  	  	
  	if text ==  'Seawifs-pico': 	return 'Seawifs Picophyto. chl.'  
  	if text ==  'SeawifsBM-micro': 	return 'Seawifs Microphyto. Biomass'  	  	
  	if text ==  'SeawifsBM-nano': 	return 'Seawifs Nanophyto. Biomass'  	  	
  	if text ==  'SeawifsBM-pico': 	return 'Seawifs Picophyto. Biomass'    		  	
  	if text ==  'Seawifs-biomass': 	return 'Phytoplankton Biomass'
  	if text ==  'intPP': 	return 'WOA Integrated PP'  	  	  	
   	if text ==  'PP': 	return 'MareDat PP'

  	if text ==  'medusa_1998': 	return 'MEDUSA (1998)'  
  	if text ==  'MEDUSA': 		return 'MEDUSA'    

  	if text ==  'InitialConditions': return 'Initial Conditions'    
  	  		 	  	  	  	
  	if text in month_name: return text
  	#if text in ['picophyto','microzoo','mesozoo','diatoms', 'bac', ]:
  	#	print "need to add ",text,"to get longname"
  	print "getLongName:\tERROR:\tCould not find Longname for ",text

	assert False



def getkd():
	kd = AutoVivification() # key dict
	#kd['Ersem']['t'] = 'time_counter'
	kd['Ersem']['t'] = 'index_t'	
	kd['Ersem']['z'] = 'deptht'
	kd['Ersem']['lat'] = 'nav_lat'
	kd['Ersem']['lon'] = 'nav_lon'
	kd['Ersem']['cal'] = '365_day'

	#kd['Ersem-1891'] 	= kd['Ersem']	
	#kd['Ersem-1893'] 	= kd['Ersem']			
	#kd['Ersem-1894'] 	= kd['Ersem']	
	#kd['Ersem-1895'] 	= kd['Ersem']		
	#kd['Ersem-1899'] 	= kd['Ersem']			
	#kd['Ersem-1909'] 	= kd['Ersem']				
	#kd['Ersem-1948'] 	= kd['Ersem']		
	#kd['Ersem-1982'] 	= kd['Ersem']			
	#kd['Ersem-2006'] 	= kd['Ersem']				
	#kd['Ersem-2001'] 	= kd['Ersem']				
	#kd['Ersem-clim'] 	= kd['Ersem']					
	#kd['Ersem-HighResp'] 	= kd['Ersem']		
	#kd['InitialConditions'] = kd['Ersem']		
	
	#kd['Maredat']['t'] = 'TIME'	

	#kd['Ersem']['t'] = 'time_counter'
	kd['MEDUSA']['t'] = 'index_t'	
	kd['MEDUSA']['z'] = 'deptht'
	kd['MEDUSA']['lat'] = 'nav_lat'
	kd['MEDUSA']['lon'] = 'nav_lon'
	kd['MEDUSA']['cal'] = '365_day'
	kd['Medusa'] =kd['MEDUSA']

	

	kd['Maredat']['t'] = 'index_t'
	kd['Maredat']['z'] = 'DEPTH'
	kd['Maredat']['lat'] = 'LATITUDE'
	kd['Maredat']['lon'] = 'LONGITUDE'
	kd['Maredat']['cal'] = 'standard'

	kd['WOA']['t'] = 'index_t'
	kd['WOA']['z'] = 'depth'
	kd['WOA']['lat'] = 'lat'
	kd['WOA']['lon'] = 'lon'
	kd['WOA']['cal'] = 'standard'

	kd['Takahashi']['t'] = 'index_t'
	kd['Takahashi']['z'] = 'index_z'
	kd['Takahashi']['lat'] = 'LAT'
	kd['Takahashi']['lon'] = 'LON'
	kd['Takahashi']['cal'] = 'standard'	

	kd['Seawifs']['t'] 	= 'month'
	kd['Seawifs']['z'] 	= 'deptht'
	kd['Seawifs']['lat'] 	= 'latitude'
	kd['Seawifs']['lon'] 	= 'longitude'
	kd['Seawifs']['cal'] 	= 'standard'	

	kd['Seawifs-nano'] 	= kd['Seawifs']
	kd['Seawifs-pico'] 	= kd['Seawifs']
	kd['Seawifs-micro'] 	= kd['Seawifs']
	kd['SeawifsBM-nano'] 	= kd['Seawifs']
	kd['SeawifsBM-pico'] 	= kd['Seawifs']
	kd['SeawifsBM-micro'] 	= kd['Seawifs']	
	kd['Seawifs-biomass'] 	= kd['Seawifs']	
			
	kd['nit']['t'] = 'index_t'
	kd['nit']['z'] = 'index_z'
	kd['nit']['lat'] = 'latitude'
	kd['nit']['lon'] = 'longitude'
	kd['nit']['cal'] = 'standard'

	kd['intPP']['t'] = 'index_t'
	kd['intPP']['z'] = 'index_z'
	kd['intPP']['lat'] = 'LATITUDE'
	kd['intPP']['lon'] = 'LONGITUDE'
	kd['intPP']['cal'] = 'standard'

	kd['GEOTRACES']['t'] = 'MONTH'
	kd['GEOTRACES']['z'] = 'DEPTH'
	kd['GEOTRACES']['lat'] = 'Latitude'
	kd['GEOTRACES']['lon'] = 'Longitude'
	kd['GEOTRACES']['cal'] = 'standard'
	
	kd['IFREMER-MLD']['t'] = 'index_t'
	kd['IFREMER-MLD']['z'] = 'index_z'
	kd['IFREMER-MLD']['lat'] = 'lat'
	kd['IFREMER-MLD']['lon'] = 'lon'
	kd['IFREMER-MLD']['cal'] = 'standard'	
		
	return kd
def getmt(): # Match Type
	#mt: [data type][name] = [what to plot, ]
	
	mt = AutoVivification() # match type
	mt['Ersem']['bac'] 		= ['B1c',]
	mt['Ersem']['mesozoo'] 		= ['Z4c',]
	mt['Ersem']['diatoms'] 		= ['P1c',]
	mt['Ersem']['picophyto'] 	= ['P3c',]
	mt['Ersem']['microzoo'] 	= ['Z5c',]
	mt['Ersem']['tempTransect'] 	= ['votemper',]
	mt['Ersem']['tempSurface'] 	= ['votemper',]
	mt['Ersem']['tempAll'] 		= ['votemper',]	
	mt['Ersem']['temp100m']		= ['votemper',]	
	mt['Ersem']['temp200m']		= ['votemper',]			
	mt['Ersem']['temp500m']		= ['votemper',]			
	mt['Ersem']['temp1000m']		= ['votemper',]					
	mt['Ersem']['salTransect'] 	=  ['vosaline',]	
	mt['Ersem']['salSurface'] 	=  ['vosaline',]
	mt['Ersem']['salAll'] 		=  ['vosaline',]
	mt['Ersem']['sal100m'] 		=  ['vosaline',]
	mt['Ersem']['sal200m'] 		=  ['vosaline',]		
	
	mt['Ersem']['sal500m'] 		= mt['Ersem']['sal200m']
	mt['Ersem']['sal1000m'] 	= mt['Ersem']['sal200m']	
			 	
	mt['Ersem']['nitrateTransect'] 	=  ['N3n',]
	mt['Ersem']['nitrateSurface'] 	=  ['N3n',]
	mt['Ersem']['nitrateAll'] 	=  ['N3n',]	
	mt['Ersem']['nitrate200m'] 	=  ['N3n',]	
	mt['Ersem']['nitrate100m'] 	=  ['N3n',]			
	mt['Ersem']['nitrate500m'] 	=  ['N3n',]			
	mt['Ersem']['phosphateTransect'] =  ['N1p',]	
	mt['Ersem']['phosphateSurface'] =  ['N1p',]
	mt['Ersem']['phosphateAll'] 	=  ['N1p',]	
	mt['Ersem']['phosphate100m'] 	=  ['N1p',]		
	mt['Ersem']['phosphate200m'] 	=  ['N1p',]	
	mt['Ersem']['phosphate500m'] 	=  ['N1p',]		
	mt['Ersem']['silicateTransect'] =  ['N5s',]	
	mt['Ersem']['silicateSurface']  =  ['N5s',]
	mt['Ersem']['silicateAll']  	=  ['N5s',]	
	mt['Ersem']['silicate100m']  	=  ['N5s',]		
	mt['Ersem']['silicate200m']  	=  ['N5s',]		
	mt['Ersem']['silicate500m']  	=  ['N5s',]			

	mt['Ersem-1891'] = mt['Ersem']
	mt['Ersem-1893'] = mt['Ersem']	
	mt['Ersem-1894'] = mt['Ersem']
	mt['Ersem-1895'] = mt['Ersem']	
	mt['Ersem-1899'] = mt['Ersem']
	mt['Ersem-1948'] = mt['Ersem']	
	mt['Ersem-1982'] = mt['Ersem']
	mt['Ersem-2001'] = mt['Ersem']	
	mt['Ersem-2006'] = mt['Ersem']
	mt['Ersem-clim'] = mt['Ersem']	
	mt['Ersem-HighResp'] = mt['Ersem']	


	mt['Ersem']['pCO2'] 			=  ['pCO2w',]#'fAirSeaC',]
	mt['Ersem']['chl'] 			=  ['chl',]	
	mt['Ersem']['Seawifs'] 			=  ['chl',]
	#biomass:		
	mt['Ersem']['Seawifs-nano'] 		=  ['Chl2']
	mt['Ersem']['Seawifs-pico'] 		=  ['Chl3',]
	mt['Ersem']['Seawifs-micro']['sum']	=  ['Chl1','Chl4',]
	mt['Ersem']['Seawifs-micro']['name']	=  'Chl1Chl4'
	mt['Ersem']['SeawifsBM-nano'] 		=  ['P2c',]
	mt['Ersem']['SeawifsBM-pico'] 		=  ['P3c',]
	mt['Ersem']['SeawifsBM-micro']['sum']	=  ['P1c','P4c',]
	mt['Ersem']['SeawifsBM-micro']['name']	=  'P1cP4c'		
	mt['Ersem']['Seawifs-biomass']['sum'] 	=  ['P1c','P2c','P3c','P4c']
	mt['Ersem']['Seawifs-biomass']['name'] 	= 'T_phyot_biomass'
	
	mt['Ersem']['intPP'] 		=  ['netPP'] #'intPP',
	mt['Ersem']['PP'] 		=  ['netPP',]#'intPP','netPP']	
	mt['Ersem']['nitSurface']  	=  ['N3n',]	
	mt['Ersem']['nitTransect'] 	=  ['N3n',]	
	mt['Ersem']['iron'] 		=  ['N7f',]

	mt['Ersem']['mld_DT02'] 	=  ['somxl010',]
	mt['Ersem']['mld_DR003'] 	=  ['somxl010',]
	mt['Ersem']['mld_DReqDTm02'] 	=  ['somxl010',]		

	mt['InitialConditions'] = mt['Ersem']
	
	mt['MEDUSA']['iron'] 		=  ['FER',]
	mt['MEDUSA']['chl'] 		=  ['CHL',]	
	mt['MEDUSA']['diatoms']['N2Biomass'] 	=  ['PHD',]		
	mt['MEDUSA']['diatoms']['name'] 	=  'PHD'
	mt['MEDUSA']['diatoms']['units'] 	=  'mg C/m^3'	
	mt['MEDUSA']['mesozoo']['N2Biomass'] 	=  ['ZME',]			
	mt['MEDUSA']['mesozoo']['name'] 	=  'ZME'
	mt['MEDUSA']['mesozoo']['units'] 	=  'mg C/m^3'		
	mt['MEDUSA']['microzoo']['N2Biomass'] 	=  ['ZMI',]				
	mt['MEDUSA']['microzoo']['name'] 	=  'ZMI'
	mt['MEDUSA']['microzoo']['units'] 	=  'mg C/m^3'		
	mt['MEDUSA']['silicateTransect'] =  ['SIL',]	
	mt['MEDUSA']['silicateSurface']  =  ['SIL',]
	mt['MEDUSA']['silicateAll']  	=  ['SIL',]	
	mt['MEDUSA']['silicate100m']  	=  ['SIL',]		
	mt['MEDUSA']['silicate200m']  	=  ['SIL',]		
	mt['MEDUSA']['silicate500m']  	=  ['SIL',]	
	
	mt['MEDUSA']['nitrateTransect'] =  ['DIN',]
	mt['MEDUSA']['nitrateSurface'] 	=  ['DIN',]
	mt['MEDUSA']['nitrateAll'] 	=  ['DIN',]	
	mt['MEDUSA']['nitrate200m'] 	=  ['DIN',]	
	mt['MEDUSA']['nitrate100m'] 	=  ['DIN',]			
	mt['MEDUSA']['nitrate500m'] 	=  ['DIN',]	
	mt['Medusa'] = mt['MEDUSA']
		
	mt['Maredat']['bac'] 		= ['BIOMASS',]
	mt['Maredat']['mesozoo'] 	= ['BIOMASS',]
	mt['Maredat']['diatoms'] 	= ['BIOMASS',]
	mt['Maredat']['picophyto'] 	= ['BIOMASS',]
	mt['Maredat']['microzoo'] 	= ['BIOMASS',]
	mt['Maredat']['PP'] 		= ['PP',]
	#mt['Maredat']['chl']
	mt['Maredat']['chl']	= ['Chlorophylla',]	
	
	mt['WOA']['tempTransect'] 	= ['t_mn',]	
	mt['WOA']['tempSurface'] 	= ['t_mn',]	
	mt['WOA']['tempAll'] 		= ['t_mn',]		
	mt['WOA']['temp100m'] 		= ['t_mn',]		
	mt['WOA']['temp200m'] 		= ['t_mn',]				
	mt['WOA']['temp500m'] 		= ['t_mn',]				
	mt['WOA']['temp1000m'] 		= ['t_mn',]
							
	mt['WOA']['salTransect'] 	= ['s_mn',]
	mt['WOA']['salSurface'] 	= ['s_mn',]
	mt['WOA']['salAll'] 		= ['s_mn',]
	mt['WOA']['sal100m'] 		= ['s_mn',]
	mt['WOA']['sal200m'] 		= ['s_mn',]	
	mt['WOA']['sal500m'] 		= ['s_mn',]	
	mt['WOA']['sal1000m'] 		= ['s_mn',]
			 	
	mt['WOA']['nitrateTransect'] 	= ['n_mn',]
	mt['WOA']['nitrateSurface']	= ['n_mn',]
	mt['WOA']['nitrateAll'] 	= ['n_mn',]	
	mt['WOA']['nitrate100m'] 	= ['n_mn',]	
	mt['WOA']['nitrate200m'] 	= ['n_mn',]			
	mt['WOA']['nitrate500m'] 	= ['n_mn',]				
	
	mt['WOA']['phosphateTransect'] 	= ['p_mn',]
	mt['WOA']['phosphateSurface'] 	= ['p_mn',]
	mt['WOA']['phosphateAll'] 	= ['p_mn',]	
	mt['WOA']['phosphate100m'] 	= ['p_mn',]	
	mt['WOA']['phosphate200m'] 	= ['p_mn',]			
	mt['WOA']['phosphate500m'] 	= ['p_mn',]			
		
	mt['WOA']['silicateTransect'] 	= ['i_mn',]
	mt['WOA']['silicateSurface'] 	= ['i_mn',]		
	mt['WOA']['silicateAll'] 	= ['i_mn',]			
	mt['WOA']['silicate100m'] 	= ['i_mn',]			
	mt['WOA']['silicate200m'] 	= ['i_mn',]		
	mt['WOA']['silicate500m'] 	= ['i_mn',]			
		 
	mt['Takahashi']['pCO2'] 		= ['PCO2_SW',]#'DELTA_PCO2',]	'TFLUXSW06',
	mt['Seawifs']['chl'] 			= ['chl',]	# Lester's Seawifs
	mt['Seawifs']['Seawifs'] 		= ['Tchl',]	# Bob's Seawifs
	mt['Seawifs']['Seawifs-nano']['productPC']	= ['Nano_percent_Tchl','Tchl']
	mt['Seawifs']['Seawifs-pico']['productPC'] 	= ['Pico_percent_Tchl','Tchl']
	mt['Seawifs']['Seawifs-micro']['productPC'] 	= ['Micro_percent_Tchl','Tchl']
	mt['Seawifs']['Seawifs-nano']['name']		= 'Nano_Tchl'
	mt['Seawifs']['Seawifs-pico']['name']		= 'Pico_Tchl'
	mt['Seawifs']['Seawifs-micro']['name']		= 'Micro_Tchl'		
	mt['Seawifs']['SeawifsBM-nano']['SWtoBmass']	= ['Nano_percent_Tchl','Tchl']
	mt['Seawifs']['SeawifsBM-pico']['SWtoBmass'] 	= ['Pico_percent_Tchl','Tchl']
	mt['Seawifs']['SeawifsBM-micro']['SWtoBmass'] 	= ['Micro_percent_Tchl','Tchl']
	mt['Seawifs']['SeawifsBM-nano']['name']		= 'Nano_Tchl'
	mt['Seawifs']['SeawifsBM-pico']['name']		= 'Pico_Tchl'
	mt['Seawifs']['SeawifsBM-micro']['name']	= 'Micro_Tchl'	
	
	mt['Seawifs']['Seawifs-biomass']['Chl2BM']	= ['Tchl',]
	mt['Seawifs']['Seawifs-biomass']['name']	= 'seawifsBiomass'
		
	mt['nitrate']['nitSurface'] 	= ['nitrate',]	
	mt['nitrate']['nitTransect'] 	= ['nitrate',]	
	mt['intPP']['intPP']		= ['PPint',]								
	mt['GEOTRACES']['iron']		= ['Fe_D_CONC_BOTTLE',]#'Fe_D_CONC_BOTTLE_FIA','Fe_S_CONC_BOTTLE',]
	mt['IFREMER-MLD']['mld_DT02']	= ['mld',]
	mt['IFREMER-MLD']['mld_DR003']	= ['mld',]
	mt['IFREMER-MLD']['mld_DReqDTm02']	= ['mld',]		

		
	#mt['PP']['PP'] 		= ['PP',]
	return mt	
	
def fancyUnits(units,debug=False):#'mg C/m^2',
  	#if units in ['mg C/m^3','mg C/m^2',]:		return 'mg C m'+r'$^{-3}$'
  	if units in ['umol/l, uM, mo/l, ug/l, ',]:	return 'mg m'+r'$^{-3}$' # silly nitrates multi units
  	if units in ['mg C/m^3',]:			return 'mg C m'+r'$^{-3}$'
  	if units in ['mg Chl/m3','ng/L',]:		return 'mg Chl m'+r'$^{-3}$'  	
  	if units in ['mg C/m^3/d',]:			return 'mg C m'+r'$^{-3}$/day'
  	if units in ['mg N/m^3',]:			return 'mg N m'+r'$^{-3}$'  
  	if units in ['mg P/m^3',]:			return 'mg P m'+r'$^{-3}$'
  	if units in ['mmol N/m^3', 'mmol-N/m3' ]: 	return 'mmol N m'+r'$^{-3}$'
  	if units in ['mmol P/m^3', ]: 			return 'mmol P m'+r'$^{-3}$'
  	if units in ['mmol C/m^3', ]: 			return 'mmol C m'+r'$^{-3}$'
  	if units in ['umol F/m^3',]:			return r'$\mu$'+'mol m'+r'$^{-3}$'
  	if units in ['mmol S/m^3', ]: 			return 'mmol S m'+r'$^{-3}$'  	
	if units in ['ug/l','mg/m^3','ug/L',]:  	return 'mg m'+r'$^{-3}$'
	if units in ['10^12 g Carbon year^-1',]:	return r'$10^{12}$'+' g Carbon/year'
	if units in ['mol C/m^',]:			return 'mol C/m'+r'$^{2}$'
  	if units in ['mmmol/m^3', 'mmol/m^3','umol/l','micromoles/l',]:
  		return 'mmol m'+r'$^{-3}$'
	if units in ['mmol/m^2']:			return 'mmol m'+r'$^{-2}$' 
	#if units in ['mmol/m^3']:			return 'mmol m'+r'$^{-3}$' 	
	if units in ['degrees Celsius', 'degreesC', 'C',]:
		return r'$\,^{\circ}\mathrm{C}$'
	if units in ['psu','PSU',]:			return 'psu'
	#if units in ['umol/l',]:return r'$\mu$'+'mol/l'
	if units in ['m',]:				return 'm'	
	if units in ['1/m',]:				return r'$\mathrm{m}^{-1}$'
	#if units in ['ug/l']:			#	return 'mg m'+r'$^{-3}$'
	if units in ['W/m^2']:				return 'W m'+r'$^{-2}$'
	if units in ['umol/kg',]:			return r'$\mu$'+'mol kg'+r'$^{-1}$'
	if units in ['nmol/kg',]:			return 'nmol kg'+r'$^{-1}$'
	if units in ['tons C/d',]:			return 'tons C/day'
	if units in ['ug/L/d','ug                  ']:	return 'mg m'+r'$^{-3}$'+'/day'#yes, there are lots of spaces
	if units.replace(' ','') in ['ug',]:		return r'$\mu$'+'g' #r'$\mu$'+	
	if units in ['1',]:			
		print 'fancyUnits:\tWarning:\tStrange units:',units
		return ''
	if units in ['uatm',]:				return r'$\mu$'+'atm'
	print 'fancyUnits:\tERROR:\t',units,' not found in fancyUnits.'
	if debug:assert False
	return units 		
		
	
