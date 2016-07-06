#
# Copyright 2014, Plymouth Marine Laboratory
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

from sys import argv
from string import join
from netCDF4 import Dataset
from os.path  import exists,getmtime
from os import mkdir, makedirs
from glob import glob
from itertools import product,izip
import numpy as np
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import LogNorm
try:
	import cartopy.crs as ccrs
	import cartopy.io.shapereader as shapereader
	from cartopy import img_transform, feature as cfeature	
except:
	print "Unable to load Cartopy"
from scipy.stats.mstats import scoreatpercentile
from scipy.stats import linregress,mode as scimode
from calendar import month_name
from shelve import open as shOpen
import socket

from  bgcvaltools.RobustStatistics import MAD
try:import yaml 
except: pass

#local imports
#from ncdfView import ncdfView
"""	This is a catch all toolkit for the python methods and shorthands used in this code.
"""

try:	defcmap = pyplot.cm.viridis
except:	
	from bgcvaltools.viridis import viridis
	defcmap = viridis

def folder(name):
	""" This snippet takes a string, makes the folder and the string.
	    It also accepts lists of strings.
	"""
	if type(name) == type(['a','b','c']):
		name=join(name,'/')
	if name[-1] != '/':
		name = name+'/'
	if exists(name) is False:
		makedirs(name)
		print 'makedirs ', name
	return name

def mnStr(month):
	mn = '%02d' %  month
	return mn
	
def getCommandJobIDandTime():
	jobID = argv[1]	
	timestamp = argv[2]
	return jobID,timestamp
	
def getFileList(fin):
	if type(fin)==type('abc') and fin.find('*')<0 and fin.find('?')<0: # fin is a string file:
		return [fin,]
	if type(fin)==type('abc') and (fin.find('*')>-1 or fin.find('?')>-1 or fin.find('[')>-1): # fin is a string file:
		return glob(fin)
	if type(fin) == type(['a','b','c',]): # fin is many files:
		filesout = []
		for f in fin:
			filesout.extend(glob(f))
		return filesout


def makeThisSafe(arr,log=False,debug = True, key='',noSqueeze=False):
	if noSqueeze:pass
	else: arr=np.ma.array(arr).squeeze()
	
	ma,mi = arr.max(), arr.min()
	
	if ma > 9.E36:	
		if debug: 	print "makeThisSafe: \tMasked values greater than 9.E36",key
		arr = np.ma.masked_greater(arr, 9.E36)
	
	if np.isinf(ma ) or np.isnan(ma ):
		if debug: print "makeThisSafe: \tMasking infs and Nans",key	
		arr = np.ma.array(arr)
		arr = np.ma.masked_where(np.isnan(arr)+arr.mask +np.isinf(arr) , arr)	
		
	return arr



def maenumerate(marr):
	"""	Masked assary enumerate command based on numpy.ndenumerate, which iterates a list of (index, value) for n-dimensional arrays.
		This version ignores masked values.
	"""
	
    	mask = ~marr.mask.ravel()
    	for i, m in izip(np.ndenumerate(marr), mask):
        	if m: yield i
        
        

class AutoVivification(dict):
    """Implementation of perl's autovivification feature.
    	This class allows you to automate the creating of layered dictionaries.
    	from https://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python
    """
    def __getitem__(self, item):
        try: return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def AutoVivToYaml(av,yamlFile):
	#####
	# Saving Nested dictionary or AutoVivification as a yaml readable file.
	space = 4*' '
	s = ''	
	def recursivePrint(d,depth,s):
	    for key in sorted(d.keys()):
	        if depth==0:s+='\n'	# empty line separator.
	        if isinstance(d[key], dict):
	            s += depth * space + str(key) + ': \n'
	            s = recursivePrint(d[key], depth+1, s)
	        else:
	            s += depth * space + str(key) + ': ' + str(d[key]) + '\n'	      
	    return s

	s = recursivePrint(av,0,s)
	
	#print 'AutoVivToYaml:\tFinal string:\n',s
	
	print 'AutoVivToYaml:\tSaving:',yamlFile
	fn = open(yamlFile,'w')
	fn.write(s)
	fn.close()

def YamlToDict(yamlFile):
	print 'YamlToDict:\tLoading:',yamlFile	
	with open(yamlFile, 'r') as f:
		d = yaml.load(f)
	return d


def machineName():
	name = str(socket.gethostname())
	if name.find('npm')>-1:	return 'PML'
	if name.find('pmpc')>-1: return 'PML'
	if name.find('esmval')>-1: return 'esmval'
	if name.find('ceda')>-1: return 'ceda'
	return False
	
class NestedDict(dict):
    """                                                                       
    Nested dictionary of arbitrary depth with autovivification.               

    Allows data access via extended slice notation.                           
    
    from https://stackoverflow.com/questions/15077973/how-can-i-access-a-deeply-nested-dictionary-using-tuples
    """
    def __getitem__(self, keys):
        # Let's assume *keys* is a list or tuple.                             
        if not isinstance(keys, basestring):
            try:
                node = self
                for key in keys:
                    node = dict.__getitem__(node, key)
                return node
            except TypeError:
            # *keys* is not a list or tuple.                              
                pass
        try:
            return dict.__getitem__(self, keys)
        except KeyError:
            raise KeyError(keys)
    def __setitem__(self, keys, value):
        # Let's assume *keys* is a list or tuple.                             
        if not isinstance(keys, basestring):
            try:
                node = self
                for key in keys[:-1]:
                    try:
                        node = dict.__getitem__(node, key)
                    except KeyError:
                        node[key] = type(self)()
                        node = node[key]
                return dict.__setitem__(node, keys[-1], value)
            except TypeError:
                # *keys* is not a list or tuple.                              
                pass
        dict.__setitem__(self, keys, value)
        
        
def getGridFile(grid):
	if grid.upper() in ['ORCA1',]:
		#grid = 'ORCA1'
		gridFile    = "data/mesh_mask_ORCA1_75.nc"		
	if grid in ['Flat1deg',]:	
		gridFile = 'data/Flat1deg.nc' 
				
	if grid.upper() in ['ORCA025',]:	
		#####
		# Please add files to link to 
		for orcafn in [ "/data/euryale7/scratch/ledm/UKESM/MEDUSA-ORCA025/mesh_mask_ORCA025_75.nc",	# PML
				"/group_workspaces/jasmin/esmeval/example_data/bgc/mesh_mask_ORCA025_75.nc",]:	# JASMIN
			if exists(orcafn):	gridFile  = orcafn
		try: 
			if exists(gridFile):pass
		except: 
			print "UKESMpython:\tgetGridFile:\tERROR:\tIt's not possible to load the ORCA025 grid on this machine."+ \
			      "\n\t\t\tPlease add the ORCA025 file to the orcafn getGridFile() list to UKESMpython.py"
			assert False
        return gridFile
	
def sliceA_obsolete(arr,region):
	# you should already have removed time by now.
	#assume time 0.
	#if region == 'DeepestWetCells':return getDeepestWetCells(arr)
	#if region == 'Lutz': return applyLutzMask(arr)
#		region = 'Lutz':			
#		lutzmask = 	
	arr = makeThisSafe(arr,noSqueeze=True)
	

	if arr.shape[-2:] != (292,362):
		print "sliceA:\tERROR:\tThis was not designed for anything except the ORCA1 grid.", arr.shape ,"won't work."
		assert False
				 
	if len(arr.shape) == 2:

		
	    	if region == 'SEA': 		return arr[100:200,:100]
	    	elif region == 'Arctic': 	return arr[230:,45:320]
	    	elif region == 'Antarctic': 	return arr[:80,:]	
	    	elif region == 'NWAtlantic': 	return arr[205:250,220:250]
	    	elif region == 'NEPacific': 	return arr[180:243, 130:185]		    	    	
	    	elif region == 'Med': 		return arr[166:243,268:]	    	
		elif region == 'Transect': 	print 'NOT POSSIBLE TO TRANSECT A 2D FIELD'
		elif region == 'Global': 	return arr[:,:]
		elif region == 'Surface': 	return arr[:,:]
		elif region == 'NoArtics': 	return arr[80:240,:]
		elif region == 'SurfaceNoArtics': 	return arr[80:240,:]		
		elif region == 'TopLayers': 	print 'NOT POSSIBLE TO TRANSECT A 2D FIELD'						
		elif region == 'All': 		return arr[:,:]				
		elif region in ['BATS', 'HOT',]:return arr[:,::-1].squeeze().transpose()
		
	    	elif region == 'SouthPacificOcean': 	return arr[80:160,70:215]
	    	elif region == 'NorthAtlanticOcean': 	return arr[185:251,215:286,]
	    	elif region == 'SouthPacificOcean': 	return arr[80:160,70:215]
	    	elif region == 'SouthAtlanticOcean': 	return arr[72:157,238:308] 	    		    	
	    	elif region == 'NorthPacificOcean': 	return arr[170:247,57:187]	    		    	
	    	elif region == 'IndianOcean': 		return arr[88:187,-40:]    		    		    		    		    			    				 

				 
				 		    		
	elif len(arr.shape) == 3:
	    	if region == 'SEA': 		return arr[0,100:200,:100]
		elif region == 'Arctic': 	return arr[0,230:,45:320]
	    	elif region == 'Antarctic': 	return arr[:,:80,:]	
		elif region == 'Atlantic': 	return arr[::-1,:,260]
	    	elif region == 'NWAtlantic': 	return arr[:,205:250,220:250]	
	    	elif region == 'NEPacific': 	return arr[:,180:243, 130:185]	    		
	    	elif region == 'Med': 		return arr[:,166:243,268:]
		elif region == 'Transect': 	return arr[::-1,:,115]
		elif region == 'Global': 	return arr[:,:,:]
		elif region == 'Surface': 	return arr[0,:,:]
		elif region == 'NoArtics': 	return arr[:,80:240,:]
		elif region == 'SurfaceNoArtics': 	return arr[0,80:240,:]					
		elif region == 'TopLayers': 	return arr[:24,:,:]						
		elif region == 'Top200m': 	return arr[:31,:,:]
		elif region == 'Top200mNoArtics': 	return arr[:31,80:240,:]		
		elif region == 'Top40mNoArtics': 	return arr[:17,80:240,:]				
		elif region == 'Top40m': 	return arr[:17,:,:]		
		elif region == 'DeepLayers': 	return arr[24:,:,:]								
		elif region == 'All': 		return arr[:,:,:]				
		elif region in ['BATS', 'HOT',]:return arr[:,::-1].squeeze().transpose()
	    	elif region == 'SouthPacificOcean': 	return arr[:,80:160,70:215]
	    	elif region == 'NorthAtlanticOcean': 	return arr[:,185:251,215:286,]
	    	elif region == 'SouthPacificOcean': 	return arr[:,80:160,70:215]
	    	elif region == 'SouthAtlanticOcean': 	return arr[:,72:157,238:308] 	    		    	
	    	elif region == 'NorthPacificOcean': 	return arr[:,170:247,57:187]	    		    	
	    	elif region == 'IndianOcean': 		return arr[:,88:187,-40:]    
	elif len(arr.shape) == 4:
	    	if region == 'SEA':		return arr[:,0,100:200,:100].squeeze()
		elif region == 'Arctic': 	return arr[:,0,230:,45:320].squeeze()
	    	elif region == 'Antarctic': 	return arr[:,:,:80,:].squeeze()
		elif region == 'Atlantic': 	return arr[:,::-1,:,260].squeeze()
	    	elif region == 'NWAtlantic': 	return arr[:,:,205:250,220:250].squeeze()
	    	elif region == 'NEPacific': 	return arr[:,:,180:243, 130:185]	
	    	elif region == 'Med': 		return arr[:,:,166:243,268:].squeeze()	    			
		elif region == 'Transect': 	return arr[:,::-1,:,115].squeeze()
		elif region == 'Global': 	return arr[:,:,:,:].squeeze()		    			 
		elif region == 'Surface': 	return arr[:,0,:,:].squeeze()
		elif region == 'NoArtics': 	return arr[:,:,80:240,:].squeeze()
		elif region == 'SurfaceNoArtics':return arr[:,0,80:240,:].squeeze()
		elif region == 'TopLayers': 	return arr[:,0:24:,:,:].squeeze()	
		elif region == 'Top200m': 	return arr[:,:31,:,:].squeeze()						
		elif region == 'Top40m': 	return arr[:,:17,:,:].squeeze()	
		elif region == 'Top200mNoArtics': 	return arr[:,:31,80:240,:]		
		elif region == 'Top40mNoArtics': 	return arr[:,:17,80:240,:]									
		elif region == 'DeepLayers': 	return arr[:,24:,:,:].squeeze()					
		elif region == 'All': 		return arr[:,:,:,:].squeeze()		    			    							
		elif region in ['BATS', 'HOT',]:return arr[:,::-1].squeeze().transpose()
	    	elif region == 'SouthPacificOcean': 	return arr[:,:,80:160,70:215]
	    	elif region == 'NorthAtlanticOcean': 	return arr[:,:,185:251,215:286,]
	    	elif region == 'SouthPacificOcean': 	return arr[:,:,80:160,70:215]
	    	elif region == 'SouthAtlanticOcean': 	return arr[:,:,72:157,238:308] 	    		    	
	    	elif region == 'NorthPacificOcean': 	return arr[:,:,170:247,57:187]	    		    	
	    	elif region == 'IndianOcean': 		return arr[:,:,88:187,-40:]    
	else:
	    	print 'WARNINIG: PLOT SHAPE IS ODD:',arr.shape, region
	    	assert False
	print 'Could not slice', region, arr.shape
	assert False
	return arr

def shouldIMakeFile(fin,fout,debug = True):
	""" the idea is to take the file: returns:
		 True: make the file
		 False: Don't make the file.
		 
	"""
	if not exists(fout): 
		if debug: print 'shouldIMakeFile: out file doesn\'t exit and should be made.'
		return True	

	if type(fin)==type('abc') and fin.find('*')<0: # fin is a string file:
		if not exists(fin): 
			if debug: print 'Warning: ',fin ,'does not exist'
			return False 
	
		if getmtime(fin) > getmtime(fout):
			if debug: print 'shouldIMakeFile: out-file is younger than in-file, you should make it.'
			return True #
		if debug: print 'shouldIMakeFile: out-file is older than in-file, you shouldn\'t make it.'		 
		return False
	if type(fin)==type('abc') and fin.find('*')>0:
		if debug: print 'shouldIMakeFile: in-file contains *, assuming it is a wildcard: ',fin
		fin = glob(fin)
		if debug: print 'shouldIMakeFile: files : ', fin
		
	if type(fin) == type(['a','b','c',]): # fin is many files:
		for f in fin:
			if not exists(f): 
				if debug: print 'Warning: ',f ,'does not exist'
				return False 
			if getmtime(f) > getmtime(fout):
				if debug: print	'shouldIMakeFile: ',f,' is younger than an ',fout,', you should make it'
				return True
		if debug: print 'shouldIMakeFile: no new files in the list. Don\'t make it.'
		return False
	if debug:
		print	'shouldIMakeFile: got to the end somehow:'
		print type(fin), fin, fout
	return False


	
def robinPlotPair(lons, lats, data1,data2,filename,titles=['',''],lon0=0.,marble=False,drawCbar=True,cbarlabel='',doLog=False,scatter=True,dpi=100,):#**kwargs):

	fig = pyplot.figure()

	fig.set_size_inches(10,10)

	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)
		
	ax1 = fig.add_subplot(211)		
	m1 = Basemap(projection='robin',lon_0=lon0,resolution='c') #lon_0=-106.,
	x1, y1 = m1(lons, lats)
	m1.drawcoastlines(linewidth=0.5)

	rbmi = min([data1.min(),data2.min()])
	rbma = max([data1.max(),data2.max()])	
	if marble: m1.bluemarble()
	else:
		m1.drawmapboundary(fill_color='1.')
		m1.fillcontinents(color=(255/255.,255/255.,255/255.,1))
	m1.drawparallels(np.arange(-90.,120.,30.))
	m1.drawmeridians(np.arange(0.,420.,60.))

	if doLog and rbmi*rbma <=0.:
		print "UKESMpython:\trobinPlotPair: \tMasking",
		data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
		data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
	if scatter:
		if doLog:	
			if len(cbarlabel)>0: 
				cbarlabel='log$_{10}$('+cbarlabel+')'				
			im1 =m1.scatter(x1,y1,c=np.log10(data1),marker="s",alpha=0.9,linewidth='0', **kwargs) 
		else:	im1 =m1.scatter(x1,y1,c=data1,marker="s",alpha=0.9,linewidth='0',**kwargs)

	else:
		xi1,yi1,di1=mapIrregularGrid(m1,ax1,lons,lats,data1,lon0,xres=360,yres=180)
	
		if doLog: im1 = m1.pcolormesh(xi1,yi1,di1,cmap=defcmap,norm = LogNorm() )
		else:	  im1 = m1.pcolormesh(xi1,yi1,di1,cmap=pyplot.cm.jet)

	
	if drawCbar:
	    c1 = fig.colorbar(im1,pad=0.05,shrink=0.75)

	    if len(cbarlabel)>0: c1.set_label(cbarlabel)

	pyplot.title(titles[0])
	
	
	#lower plot:
	ax2 = fig.add_subplot(212)					
	m2 = Basemap(projection='robin',lon_0=lon0,resolution='c') #lon_0=-106.,
	x2, y2 = m2(lons, lats)
	m2.drawcoastlines(linewidth=0.5)
	if marble: m2.bluemarble()
	else:
		m2.drawmapboundary(fill_color='1.')
		m2.fillcontinents(color=(255/255.,255/255.,255/255.,1))
	
	m2.drawparallels(np.arange(-90.,120.,30.))
	m2.drawmeridians(np.arange(0.,420.,60.))

	if scatter:
		if doLog:	im2 =m2.scatter(x2,y2,c=np.log10(data2),marker="s",alpha=0.9,linewidth='0',**kwargs) #vmin=vmin,vmax=vmax)
		else:		im2 =m2.scatter(x2,y2,c=data2,marker="s",alpha=0.9,linewidth='0',**kwargs) #vmin=vmin,vmax=vmax)		
	else:
		xi2,yi2,di2=mapIrregularGrid(m2,ax2,lons,lats,data2,lon0,xres=360,yres=180)
	
		if doLog: im2 = m2.pcolormesh(xi2,yi2,di2,cmap=defcmap,norm = LogNorm() )
		else:	  im2 = m2.pcolormesh(xi2,yi2,di2,cmap=defcmap) #shading='flat',
	
	if drawCbar:
	    c2 = fig.colorbar(im2,pad=0.05,shrink=0.75)	
	    if len(cbarlabel)>0: c2.set_label(cbarlabel)

	pyplot.title(titles[1])			
		
	print "UKESMpython:\trobinPlotPair: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()




def robinPlotQuad(lons, lats, data1,data2,filename,titles=['',''],title='',lon0=0.,marble=False,drawCbar=True,cbarlabel='',doLog=False,scatter=True,dpi=100,vmin='',vmax='',maptype='Basemap'):#,**kwargs):

	fig = pyplot.figure()
	fig.set_size_inches(10,6)

	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)
	axs,bms,cbs,ims = [],[],[],[]

	if not vmin: vmin = data1.min()
	if not vmax: vmax = data1.max()
	vmin = min([data1.min(),data2.min(),vmin])
	vmax = max([data1.max(),data2.max(),vmax])			
	
	#doLog, vmin,vmax = determineLimsAndLog(vmin,vmax)
	doLog, vmin,vmax = determineLimsFromData(data1,data2)
	
	doLogs = [doLog,doLog,False,True]
	print "robinPlotQuad:\t",len(lons),len(lats),len(data1),len(data2)
	for i,spl in enumerate([221,222,223,224]):	
		
		if spl in [221,222]:
			rbmi = vmin
			rbma = vmax
			
		if spl in [223,]:
			
			rbma =3*np.ma.std(data1 -data2)
			print spl,i, rbma, max(data1),max(data2)
			#assert False
			rbmi = -rbma
		if spl in [224,]:
			rbma = 10. #max(np.ma.abs(data1 -data2))
			rbmi = 0.1		
				
		if doLogs[i] and rbmi*rbma <=0.:
			print "UKESMpython:\trobinPlotQuad: \tMasking",
			data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
			data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
		data = ''
		
		if spl in [221,]:data  = np.ma.clip(data1, 	 rbmi,rbma)
		if spl in [222,]:data  = np.ma.clip(data2, 	 rbmi,rbma)
		if spl in [223,]:data  = np.ma.clip(data1-data2, rbmi,rbma)
		if spl in [224,]:data  = np.ma.clip(data1/data2, rbmi,rbma)


		if spl in [221,222,]:cmap= defcmap
		if spl in [223,224,]:cmap= pyplot.cm.RdBu_r		
		

			
		if maptype=='Basemap':
			axs.append(fig.add_subplot(spl))		
			bms.append( Basemap(projection='robin',lon_0=lon0,resolution='c') )#lon_0=-106.,
			x1, y1 = bms[i](lons, lats)
			bms[i].drawcoastlines(linewidth=0.5)
			if marble: bms[i].bluemarble()
			else:
				bms[i].drawmapboundary(fill_color='1.')
				bms[i].fillcontinents(color=(255/255.,255/255.,255/255.,1))
			bms[i].drawparallels(np.arange(-90.,120.,30.))
			bms[i].drawmeridians(np.arange(0.,420.,60.))
			
			if doLogs[i]:
				rbmi = np.int(np.log10(rbmi))
				rbma = np.log10(rbma)
				if rbma > np.int(rbma): rbma+=1
				rbma = np.int(rbma)
											
			if scatter:
				if doLogs[i]:	
					if len(cbarlabel)>0: 
						cbarlabel='log$_{10}$('+cbarlabel+')'									
					ims.append(bms[i].scatter(x1,y1,c = np.log10(data),cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))# **kwargs))
				else:	ims.append(bms[i].scatter(x1,y1,c = data,	   cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))# **kwargs))
			else:
				xi1,yi1,di1=mapIrregularGrid(bms[i],axs[i],lons,lats,data,lon0,xres=360,yres=180)
				if doLogs[i]: 	ims.append( bms[i].pcolormesh(xi1,yi1,di1,cmap=cmap,norm = LogNorm() ))
				else:	  	ims.append( bms[i].pcolormesh(xi1,yi1,di1,cmap=cmap))
			if drawCbar:
				if spl in [221,222,223]:
					if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
					else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
				if spl in [224,]:
					cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					cbs[i].set_ticks ([-1,0,1])
					cbs[i].set_ticklabels(['0.1','1.','10.'])
										  
										  
		if maptype=='Cartopy':
			#axs.append(fig.add_subplot(spl))
			bms.append(pyplot.subplot(spl,projection=ccrs.Robinson()))
			bms[i].set_global()
			

						
			if marble:	bms[i].stock_img()
			else:
				# Because Cartopy is hard wired to download the shapes files from a website that doesn't exist anymore:

				bms[i].add_geometries(list(shapereader.Reader('data/ne_110m_coastline.shp').geometries()),
							ccrs.PlateCarree(), color='k',facecolor = 'none',linewidth=0.5)
			
			if scatter:
				if doLogs[i] and spl in [221,222]:
					rbmi = np.int(np.log10(rbmi))
					rbma = np.log10(rbma)
					if rbma > np.int(rbma): rbma+=1
					rbma = np.int(rbma)
							
				if doLogs[i]:
					ims.append(
						bms[i].scatter(lons, lats,c = np.log10(data),
							cmap=cmap,marker="s",alpha=0.9,linewidth='0',
							vmin=rbmi, vmax=rbma,
							transform=ccrs.PlateCarree(),
							)
						)
				else:	
					ims.append(
						bms[i].scatter(lons, lats,c = data,
						        cmap=cmap,marker="s",alpha=0.9,linewidth='0',
						        vmin=rbmi, vmax=rbma,
						        transform=ccrs.PlateCarree(),)
						  )
				if drawCbar:
					if spl in [221,222,223]:
						if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
						else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					if spl in [224,]:
						cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
						cbs[i].set_ticks ([-1,0,1])
						cbs[i].set_ticklabels(['0.1','1.','10.'])
										  
			else:
				crojp2, newData, newLon,newLat = regrid(data.squeeze(),lons, lats)	
				print "cartopy robin quad:",i,spl,newData.shape,newData.min(),newData.max(), rbmi,rbma
				if doLogs[i]:
					ims.append(							
						bms[i].pcolormesh(newLon, newLat,newData,
							transform=ccrs.PlateCarree(),
							cmap=cmap,
							norm=LogNorm(vmin=rbmi,vmax=rbma)
							)
						)
							
				else:
					ims.append(											
						bms[i].pcolormesh(newLon, newLat,newData,
							transform=ccrs.PlateCarree(),
							cmap=cmap,
							vmin=rbmi,vmax=rbma)
						)
				bms[i].coastlines()	#doesn't work.
				#bms[i].fillcontinents(color=(255/255.,255/255.,255/255.,1))
				bms[i].add_feature(cfeature.LAND,  facecolor='1.')	
				if drawCbar:
					if spl in [221,222,223]:
						if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))#ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
						else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					if spl in [224,]:
						cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
						cbs[i].set_ticks ([0.1,1.,10.])
						cbs[i].set_ticklabels(['0.1','1.','10.'])				

			#else:		ticks = np.linspace( rbmi,rbma,9)
			#print i, spl, ticks, [rbmi,rbma]
			
			#pyplot.colorbar(ims[i],cmap=defcmap,values=[rbmi,rbma])#boundaries=[rbmi,rbma])
		 	#cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5))#,ticks=ticks))
		 	
		 	cbs[i].set_clim(rbmi,rbma)

		    	if len(cbarlabel)>0 and spl in [221,222,]: cbs[i].set_label(cbarlabel)
		if i in [0,1]:
			pyplot.title(titles[i])
		if i ==2:	pyplot.title('Difference ('+titles[0]+' - '+titles[1]+')')
		if i ==3:	pyplot.title('Quotient ('  +titles[0]+' / '+titles[1]+')')
	
	if title:
		fig.text(0.5,0.975,title,horizontalalignment='center',verticalalignment='top')	
	pyplot.tight_layout()		
	print "UKESMpython:\trobinPlotQuad: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()

	
def HovPlotQuad(lons,lats, depths, 
		data1,data2,filename,
		titles=['',''],title='',
		lon0=0.,marble=False,drawCbar=True,cbarlabel='',doLog=False,scatter=True,dpi=100,vmin='',vmax='',
		logy = False
		):#,**kwargs):

	fig = pyplot.figure()
	fig.set_size_inches(10,6)
	depths = np.array(depths)
	if depths.max() * depths.min() >0. and depths.max()  >0.: depths = -depths
	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)
	
	#if not vmin: vmin = data1.min()
	#if not vmax: vmax = data1.max()
	#vmin = min([data1.min(),data2.min(),vmin])
	#vmax = max([data1.max(),data2.max(),vmax])
		
	#doLog, vmin,vmax = determineLimsAndLog(vmin,vmax)
	doLog, vmin,vmax = determineLimsFromData(data1,data2)
			
	axs,bms,cbs,ims = [],[],[],[]
	doLogs = [doLog,doLog,False,True]
	print "HovPlotQuad:\t",len(depths),len(lats),len(data1),len(data2)

	#####
	# Plotting coordinate with lowest standard deviation.	
	lon_std = lons.std()
	lat_std = lats.std()	
	if lon_std<lat_std:
		hovXaxis = lats
	else:	hovXaxis = lons
	
	
	for i,spl in enumerate([221,222,223,224]):	
		
		if spl in [221,222]:
			rbmi = vmin
			rbma = vmax
		if spl in [223,]:
			rbma =3*np.ma.std(data1 -data2)
			print spl,i, rbma, max(data1),max(data2)
			rbmi = -rbma
		if spl in [224,]:
			rbma = 10.001 #max(np.ma.abs(data1 -data2))
			rbmi = 0.0999		
				
		if doLogs[i] and rbmi*rbma <=0.:
			print "UKESMpython:\tHovPlotQuad: \tMasking",
			data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
			data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
		data = ''
		
		if spl in [221,]:data  = np.ma.clip(data1, 	 rbmi,rbma)
		if spl in [222,]:data  = np.ma.clip(data2, 	 rbmi,rbma)
		if spl in [223,]:data  = np.ma.clip(data1-data2, rbmi,rbma)
		if spl in [224,]:data  = np.ma.clip(data1/data2, rbmi,rbma)


		if spl in [221,222,]:cmap= defcmap
		if spl in [223,224,]:cmap= pyplot.cm.RdBu_r		
		

						
		#if doLogs[i]:
		#	rbmi = np.int(np.log10(rbmi))
		#	rbma = np.log10(rbma)
		#	if rbma > np.int(rbma): rbma+=1
		#	rbma = np.int(rbma)

		axs.append(fig.add_subplot(spl))
		if scatter:
			if doLogs[i] and spl in [221,222]:
				rbmi = np.int(np.log10(rbmi))
				rbma = np.log10(rbma)
				if rbma > np.int(rbma): rbma+=1
				rbma = np.int(rbma)
					
			if doLogs[i]:	
				if len(cbarlabel)>0: 
					cbarlabel='log$_{10}$('+cbarlabel+')'												
				ims.append(pyplot.scatter(hovXaxis,depths, c= np.log10(data),cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))
			else:	ims.append(pyplot.scatter(hovXaxis,depths, c=          data ,cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))
			if drawCbar:
				if spl in [221,222,223]:
					if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
					else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
				if spl in [224,]:
					cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					cbs[i].set_ticks ([-1.,0.,1.])
					cbs[i].set_ticklabels(['0.1','1.','10.'])			
		else:
			print "hovXaxis:",hovXaxis.min(),hovXaxis.max(),"\tdepths:",depths.min(),depths.max(),"\tdata:",data.min(),data.max()
			newX,newY,newData = arrayify(hovXaxis,depths,data)
			print "newX:",newX.min(),newX.max(),"\tnewY:",newY.min(),newY.max(),"\tnewData:",newData.min(),newData.max() , 'range:', rbmi,rbma			
			if doLogs[i]:	ims.append(pyplot.pcolormesh(newX,newY, newData, cmap=cmap, norm=LogNorm(vmin=rbmi,vmax=rbma),))
			else:		ims.append(pyplot.pcolormesh(newX,newY, newData, cmap=cmap, vmin=rbmi, vmax=rbma,))			

		
			if drawCbar:
				if spl in [221,222,223]:
					if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
					else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
				if spl in [224,]:
					cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					cbs[i].set_ticks ([0.1,1.,10.])
					cbs[i].set_ticklabels(['0.1','1.','10.'])
		 	
		 	cbs[i].set_clim(rbmi,rbma)

		    	if len(cbarlabel)>0 and spl in [221,222,]: cbs[i].set_label(cbarlabel)
		if i in [0,1]:
			pyplot.title(titles[i])
		if i ==2:	pyplot.title('Difference ('+titles[0]+' - '+titles[1]+')')
		if i ==3:	pyplot.title('Quotient ('  +titles[0]+' / '+titles[1]+')')
	
		#if logy: axs[i].set_yscale('log')
                if logy: axs[i].set_yscale('symlog')

		
		#if hovXaxis.min() >=-90. and hovXaxis.max()<=90.:
		#	axs[i].set_xlim([-90.,90.])			
		#if hovXaxis.min() >=-180. and hovXaxis.max()<=180.:	
		#	axs[i].set_xlim([180.,180.])
		#if hovXaxis.min() >=0. and hovXaxis.max()<=360.:	
		#	axs[i].set_xlim([0.,360.])			
		
	if title:
		fig.text(0.5,0.975,title,horizontalalignment='center',verticalalignment='top')	
	pyplot.tight_layout()		
	print "UKESMpython:\tHovPlotQuad: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()
		
def arrayify(oldX,oldY,data):
	#####
	# Takes three arrays and converts it into mesh grid style coordinates and a 2D array of the data.
	newXd,newYd,newDatad = {},{},{}
	
	if len(oldX) == len(oldY) == len(data): pass
	else:
		print "Arrays are the wrong size!"
		assert 0
	for x, y, d in zip(oldX,oldY,data):
		newXd[x] = 1
		newYd[y] = 1		
		newDatad[(x,y)] = d
	newX = np.array(sorted(newXd.keys()))
	newY = np.array(sorted(newYd.keys()))
	indexX = {x:i for i,x in enumerate(newX)}
	indexY = {y:i for i,y in enumerate(newY)}
	
	newData = np.ma.zeros((len(newY),len(newX))) - 999.
	
	for (x,y),d in newDatad.items():
		i = indexX[x]
		j = indexY[y]
		newData[j,i] = d

	newData = np.ma.masked_where(newData==-999.,newData)
	return newX,newY,newData

def determineLimsAndLog(mi,ma):
	#####
	# Takes the minimum, the maximum value and retuns wherether it should be a log, 
	# and the new axis range.
	log = True
	
	if 0. in [mi,ma]:
		log=False		
	elif ma/mi < 500.:
		log=False
		
	if log:
		#####
		# log
		diff = np.log10(ma) - np.log10(mi)
		xmin = 10.**(np.log10(mi)-diff/20.) 
		ma = 10.**(np.log10(ma)+diff/20.) 	
	else:	#####
		# not log
		diff = abs(ma - mi)
		mi =mi-diff/20.
		ma = ma+diff/20.	
	return log, mi ,ma		

def determineLimsFromData(data1,data2):
	#####
	# Takes the two data sets, and retuns wherether it should be a log, 
	# and the new axis range.
	
	log = True
	
	data = np.append(data1.compressed(),data2.compressed(),)
	
	mi = np.percentile(data, 5.)
	ma = np.percentile(data,95.)	
	
	if 0. in [mi,ma]:
		log=False		
	elif ma/mi < 500.:
		log=False
		
	return log, mi ,ma
			

def histPlot(datax, datay,  filename, Title='', labelx='',labely='',xaxislabel='', logx=False,logy=False,nbins=50,dpi=100,minNumPoints = 6, legendDict= ['mean','mode','std','median','mad']):
#	try:import seaborn as sb
#	except:pass
	

	fig = pyplot.figure()		
	ax = pyplot.subplot(111)
	xmin =  np.ma.min([np.ma.min(datax),np.ma.min(datay)])#*0.9
	xmax =  np.ma.max([np.ma.max(datax),np.ma.max(datay)])#*1.1

		
	logx, xmin,xmax = determineLimsAndLog(xmin,xmax)
	
		
	if datax.size < minNumPoints and datay.size < minNumPoints:
		print "UKESMpython:\thistPlot:\tThere aren't enough points for a sensible dataplot: ", datax.size
		return		

	print "UKESMpython:\thistplot:\t preparing", Title, datax.size, datay.size, (xmin, '-->',xmax)#, datax,datay
		
	if logx:
		n, bins, patchesx = pyplot.hist(datax,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
		n, bins, patchesy = pyplot.hist(datay,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
	else: 
		n, bins, patchesx = pyplot.hist(datax,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax] )
		n, bins, patchesy = pyplot.hist(datay,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax])

	ax.set_xlim([xmin,xmax])			
	pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
	pyplot.setp(patchesy, 'facecolor', 'b', 'alpha', 0.5)
	
	if len(legendDict)>0:
		if logx: 
			mod = scimode(np.ma.round(np.ma.log10(datax),2))[0][0]#	
			mod = 10.**mod
		else:	mod = scimode(np.ma.round(datax,2))[0][0]#		
		med = np.ma.median(datax)
		mea = np.ma.mean(datax)
		std = np.ma.std(datax)
		mad = MAD(datax)

		txt =labelx
		if 'mean' in legendDict: 	txt += '\n'+'   Mean:      '+str(round(mea,2))
		if 'median' in legendDict: 	txt += '\n'+'   Median:   '+str(round(med,2))
		if 'mode' in legendDict: 	txt += '\n'+'   Mode:      '+str(round(mod,2))
		if 'std' in legendDict: 	txt += '\n'+'   '+r'$\sigma$'+':             '+str(round(std,2))
		if 'mad' in legendDict: 	txt += '\n'+'   MAD:       '+str(round(mad,2))
		
		if logx: 
			mody = scimode(np.ma.round(np.ma.log10(datay),2))[0][0]#
			mody= 10.**mody
		else:	mody= scimode(np.ma.round(datay,2))[0][0]#	
		
		medy = np.ma.median(datay)
		meay = np.ma.mean(datay)
		stdy = np.ma.std(datay)
		mady = MAD(datay)
							
		txt +='\n\n'+labely
		if 'mean' in legendDict: 	txt += '\n'+'   Mean:      '+str(round(meay,2))
		if 'median' in legendDict: 	txt += '\n'+'   Median:   '+str(round(medy,2))
		if 'mode' in legendDict: 	txt += '\n'+'   Mode:      '+str(round(mody,2))
		if 'std' in legendDict: 	txt += '\n'+'   '+r'$\sigma$'+':             '+str(round(stdy,2))
		if 'mad' in legendDict: 	txt += '\n'+'   MAD:       '+str(round(mady,2))	
		fig.text(0.15,0.12,txt,horizontalalignment='left',verticalalignment='bottom')
		
	#if logx:
	#	bins = range(xmin, xmax)
	#	pyplot.xticks(bins, ["2^%s" % i for i in bins])
	#	plt.hist(numpy.log2(data), log=True, bins=bins)
	
	if logx: 
		ax.set_xscale('log')
		
	if logy: ax.set_yscale('log')

		
	leg = pyplot.legend([labelx,labely],loc='upper left')
	leg.draw_frame(False) 
	leg.get_frame().set_alpha(0.)	
	
	pyplot.title(Title)	
	pyplot.xlabel(xaxislabel)
	#pyplot.ylabel(labely)
	
	print "UKESMpython:\thistPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)
	pyplot.close()	

def histsPlot(datax, datay,  filename, Title='', labelx='',labely='',xaxislabel='', logx=False,logy=False,nbins=50,dpi=100,minNumPoints = 6):


	fig = pyplot.figure()		
	ax = pyplot.subplot(311)
	fig.set_size_inches(8,14)	
	xmin =  np.ma.min([np.ma.min(datax),np.ma.min(datay)])
	xmax =  np.ma.max([np.ma.max(datax),np.ma.max(datay)])
	
	logx, xmin,xmax = determineLimsAndLog(xmin,xmax)
		
	
	
	if datax.size < minNumPoints and datay.size < minNumPoints:
		print "UKESMpython:\thistsPlot:\tThere aren't enough points for a sensible dataplot: ", datax.size
		return		

	
	if logx:
		n, bins, patchesx = pyplot.hist(datax,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
		n, bins, patchesy = pyplot.hist(datay,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
	else: 
		n, bins, patchesx = pyplot.hist(datax,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax] )
		n, bins, patchesy = pyplot.hist(datay,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax])
			
	pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
	pyplot.setp(patchesy, 'facecolor', 'b', 'alpha', 0.5)
	
	#if logx:
	#	bins = range(xmin, xmax)
	#	pyplot.xticks(bins, ["2^%s" % i for i in bins])
	#	plt.hist(numpy.log2(data), log=True, bins=bins)
	
	if logx: ax.set_xscale('log')
	if logy: ax.set_yscale('log')
	pyplot.legend([labelx,labely],loc='upper left')
	
	pyplot.title(Title)	
	#pyplot.xlabel(xaxislabel)
	#pyplot.ylabel(labely)

	ax = pyplot.subplot(312)
	pyplot.title('Difference: '+labelx+' - '+labely )	
	d = datax-datay
	maxd = np.max(np.abs(d))
	n, bins, patchesx = pyplot.hist(d,  bins=np.linspace(-maxd, maxd, nbins), histtype='stepfilled',range=[-maxd,maxd] )
	pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5,)		
	y = pyplot.axvline(x=0., c = 'k',ls='--',lw=2,)
	y = pyplot.axvline(x=np.ma.mean(d), c = 'k',ls='-',label= 'Mean Bias: '+str(round(np.ma.mean(d),2)))	
	y = pyplot.axvline(x=np.ma.median(d), c = 'k',ls='--',label= 'Median Bias: '+str(round(np.ma.median(d),2)))		
	pyplot.legend(loc='upper left')
	
	ax = pyplot.subplot(313)
	pyplot.title('Quotient: '+labelx+' / '+labely)	
	d = datax/np.ma.masked_where(datay==0.,datay)

	if logx:		
		maxd = np.ma.power(10.,np.int(np.ma.max(np.ma.abs(np.ma.log10(d)))+1))
		print maxd, 1/maxd
		n, bins, patchesx = pyplot.hist(d,  histtype='stepfilled', bins=10**np.linspace(np.log10(1./maxd), np.log10(maxd), nbins),range=[xmin,xmax])	
		pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
		ax.set_xscale('log')
	else:
		n, bins, patchesx = pyplot.hist(d,  histtype='stepfilled', range=[d.min(),d.max()])	
		pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
				
	y = pyplot.axvline(x=1., c = 'k',ls='--',lw=2,)
	y = pyplot.axvline(x=np.ma.mean(d), c = 'k',ls='-',label= 'Mean Slope: '+str(round(np.ma.mean(d),2)))	
	y = pyplot.axvline(x=np.ma.median(d), c = 'k',ls='--',label= 'Median Slope: '+str(round(np.ma.median(d),2)))	
	pyplot.legend(loc='upper left')		
	
	print "UKESMpython:\thistPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)
	pyplot.close()	
	

def makeOneDPlot(dates, data, title, filename, minmax=[0.,0.],dpi=100):
	print "makeOneDPlot: ", filename
	fig = pyplot.figure()
	ax = fig.add_subplot(111)
	fig.set_size_inches(16, 6)
	
	if len(dates) != len(data):
		print "makeOneDPlot:\tTHere is a size Mismatch between time and data", len(dates) ,len(data)
		assert False
		
	ma,mi = np.ma.max(data), np.ma.min(data)
	if np.isinf(ma ) or np.isnan(ma ) :
		print title,"has an inf/NaN:",ma,mi, np.isinf(ma ) , np.isnan(ma)	
		data = np.ma.array(data)
		data = np.ma.masked_invalid(data)
		ma = np.ma.max(data)
		mi = np.ma.min(data)
		
	if ma is np.ma.masked: 
		print 'makeOneDPlot:\tNo values in the masked array'
		return
	try: print ma+mi
	except: 
		print 'makeOneDPlot:\tmaximum isn\'t a number. exiting.'	
		return
				
	if minmax!= [0.,0.]:
		mi,ma = minmax[0],minmax[1]
		
	pyplot.plot(dates, data)
		
	if ma/100. > mi and ma * mi > 0. and ma > 0.: ax.set_yscale('log')
	
	pyplot.title(title) 
		
	print "makeOneDPlot:\tSaving: " + filename
	pyplot.savefig(filename,dpi=dpi)#, bbox_inches='tight')
	pyplot.close()	
	
		
		
def strRound(val,i=4):
	if round(val,i)==0. and i==4:return ' < 0.0001'
		
	if val>10000: return str(int(round(val,i-5)))
	if val>1000: return str(int(round(val,i-4)))
	if val>100: return str(round(val,i-3))
	if val>10: return str(round(val,i-2))
	if val>1: return str(round(val,i-1))
	return str(round(val,i))
	
def addStraightLineFit(ax, x,y,showtext=True, addOneToOne=False,extent = [0,0,0,0]):
	def getLinRegText(ax, x, y, showtext=True):
		x = [a for a in x if (a is np.ma.masked)==False]
		y = [a for a in y if (a is np.ma.masked)==False]
		beta1, beta0, rValue, pValue, stdErr = linregress(x, y)
		thetext = r'$\^\beta_0$ = '+strRound(beta0)		\
			+ '\n'+r'$\^\beta_1$ = '+strRound(beta1)	\
			+ '\nR = '+ strRound(rValue)		\
			+ '\nP = '+strRound(pValue)		\
			+ '\nN = '+str(int(len(x)))
			#+ '\n'+r'$\epsilon$ = ' + strRound(stdErr)	\
		if showtext: pyplot.text(0.04, 0.96,thetext ,
	     			horizontalalignment='left',
	     			verticalalignment='top',
	     			transform = ax.transAxes)
		return beta1, beta0, rValue, pValue, stdErr
	
	b1, b0, rValue, pValue, stdErr = getLinRegText(ax, x, y, showtext =showtext)
	if extent == [0,0,0,0]:
		fx = arange(x.min(), x.max(), (x.max()-x.min())/20.)
		fy =[b0 + b1*a for a in fx]
	else:
		minv = min(extent)
		maxv = max(extent)
		fx = np.arange(minv, maxv, (maxv-minv)/1000.)
		fy = np.array([b0 + b1*a for a in fx])
		
		fx = np.ma.masked_where((fx<minv) + (fy < minv) + (fx>maxv) + (fy > maxv), fx)
		fy = np.ma.masked_where((fx<minv) + (fy < minv) + (fx>maxv) + (fy > maxv), fy)
		
	pyplot.plot(fx,fy, 'k')
	if addOneToOne: pyplot.plot(fx,fx, 'k--')
				
	#xstep = (x.max()-x.min())/40.
	#ystep = (y.max()-y.min())/40.
	#pyplot.axis([x.min()-xstep, x.max()+xstep, y.min()-ystep, y.max()+ystep])
	

	

	
def scatterPlot(datax, datay,  filename, Title='', labelx='',labely='', logx=False,logy=False, hexPlot = True, bestfitLine=True,gridsize=50,set_equal=True,percentileRange = [0,100],dpi=100):
	fig = pyplot.figure()		
	ax = pyplot.subplot(111)

	if percentileRange == [0,100]:
		xmin = datax.min()
		xmax = datax.max()
		ymin = datay.min()
		ymax = datay.max()
	else:
		xmin = scoreatpercentile(datax.compressed(),percentileRange[0])
		xmax = scoreatpercentile(datax.compressed(),percentileRange[1])
		ymin = scoreatpercentile(datay.compressed(),percentileRange[0])
		ymax = scoreatpercentile(datay.compressed(),percentileRange[1])
	
	if set_equal:
		ax.set_aspect("equal")
		xmin = ymin= np.ma.min([xmin,ymin])
		xmax = ymax= np.ma.max([xmax,ymax])
		
	dolog, xmin,xmax = determineLimsAndLog(xmin,xmax)
	logx=dolog
	logy=dolog	
	
	plotrange = [xmin, xmax, ymin, ymax]			
	print "UKESMpython:\tscatterPlot:\trange:",plotrange
	
	#if xmin*xmax <= 0. or ymin*ymax <=.0:
#		logx=False
#		logy=False
#		print "UKESMpython:\tscatterPlot:\tx value below zero, can not run log scale.", '\t',labelx,'(x):', xmin, '\t',labely,'(y):', ymin		
	
	if logx: ax.set_xscale('log')
	if logy: ax.set_yscale('log')
		
	#gridsize = 50
	if hexPlot:
		colours = 'gist_yarg' # 'Greens'
		
		#if logx:bins = 10**linspace(np.log10(xmin), np.log10(xmax))
		#else: 
		bins = 'log'

		if logx and logy:
			
			h = pyplot.hexbin(datax, datay,xscale='log', yscale='log',  bins='log', extent=np.log10(plotrange), gridsize = gridsize, cmap=pyplot.get_cmap(colours),mincnt=0)
		else:
			h = pyplot.hexbin(datax, datay, bins='log',gridsize = gridsize, extent=plotrange,cmap=pyplot.get_cmap(colours),mincnt=0)		
		cb = pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, ],)
	
		cb.set_ticklabels([r'$10^0$',r'$10^1$',r'$10^2$',r'$10^3$',r'$10^4$',r'$10^5$',r'$10^6$',])
		#cb.set_label('np.log10(N)')
					
	else:
		pyplot.scatter(datax, datay, marker ='o')	

	if bestfitLine:
		addStraightLineFit(ax, datax, datay, showtext =True,addOneToOne=True, extent=plotrange) 
		

	pyplot.axis(plotrange)	
		
	pyplot.title(Title)	
	pyplot.xlabel(labelx)
	pyplot.ylabel(labely)

	print "UKESMpython:\tscatterPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)
	pyplot.close()			
			
def getOrcaIndexCC(lat,lon, latcc, loncc, debug=True,slowMethod=False,llrange=5.):
	""" takes a lat and long coordinate, an returns the position of the closest coordinate in the NemoERSEM (ORCA1) grid.
	    uses the bathymetry file.
	"""
	km = 10.E20
	la_ind, lo_ind = -1,-1
	lat = makeLatSafe(lat)
	lon = makeLonSafe(lon)	
	
	c = (latcc - lat)**2 + (loncc - lon)**2

	(la_ind,lo_ind) =  np.unravel_index(c.argmin(),c.shape)

	if debug: print 'location ', [la_ind,lo_ind],'(',latcc[la_ind,lo_ind],loncc[la_ind,lo_ind],') is closest to:',[lat,lon]	
	return la_ind,lo_ind


def getORCAdepth(z,depth,debug=True):
	""" Calculate closest depth. Returns an index
	"""
	d = 1000.
	best = -1
	for i,zz in enumerate(depth.squeeze()):
		d2 = abs(abs(z)-abs(zz))
		if d2<d:
		   d=d2
		   best = i
		   if debug: print 'UKESMPython.getORCAdepth:',i,z,zz,depth.shape, 'best:',best
	if debug: print 'UKESMPython.getORCAdepth:\tdepth: in situ:', z,'index:', best, 'distance:',d,', closest model:',depth.shape, depth[best]
	return best

def getclosestlon(x,lons,debug=True):
	"""	Code to locate the closets longitude coordinate for transects. 
		Only works for 1D longitude arrays
		Returns an index
	"""
	d = 1000.
	best = -1
	if lons.ndim >1: 
		print "getclosestlon:\tFATAL:\tThis code only works for 1D longitude arrays"
		assert False
	x = makeLonSafe(x)
	lons = makeLonSafeArr(lons)
	
	for i,xx in enumerate(lons.squeeze()):
		d2 = abs(x-xx)
		if d2<d:
		   d=d2
		   best = i
		   print 'getORCAdepth:',i,x,xx,lons.shape, 'best:',best
	if debug: print 'lons: in situ:', x,'index:', best, 'distance:',d,', closest model:',lons.shape, lons[best]
	return best
	
def getclosestlat(x,lats,debug=True):
	"""	Code to locate the closets latitute coordinate for transects. 
		Only works for 1D latitute arrays
		Returns an index
	"""
	d = 1000.
	best = -1
	if lats.ndim >1: 
		print "getclosestlon:\tFATAL:\tThis code only works for 1D latitute arrays"
		assert False
	
	for i,xx in enumerate(lats.squeeze()):
		d2 = abs(x-xx)
		if d2<d:
		   d=d2
		   best = i
		   print 'getORCAdepth:',i,x,xx,lats.shape, 'best:',best
	if debug: print 'lats: in situ:', x,'index:', best, 'distance:',d,', closest model:',lats.shape, lats[best]
	return best
	
	
	
	
def makeLonSafe(lon):
	while True:
		if -180<lon<=180:return lon
		if lon<=-180:lon+=360.
		if lon> 180:lon-=360.		
	
def makeLatSafe(lat):
	#while True:
	if -90.<=lat<=90.:return lat
	#print 'You can\'t have a latitude > 90 or <-90',lat
	if lat is np.ma.masked: return lat
	print "makeLatSafe:\tERROR:\tYou can\'t have a latitude > 90 or <-90", lat
	assert False
	#return np.ma.clip(lat,-90.,90.)
	#assert False		
	#return False
	#if lon<=-90:lat+=360.
	#if lon> 90:lat-=360.		
	   
def makeLonSafeArr(lon):
	if lon.ndim == 2:
	 for l,lon1 in enumerate(lon):
	  for ll,lon2 in enumerate(lon1):
	   lon[l,ll] = makeLonSafe(lon2)
	 return lon
	if lon.ndim == 1:
	 for l,lon1 in enumerate(lon):
	   lon[l] = makeLonSafe(lon1)
	 return lon
	 	 
	assert False


def Area(p1,p2):#lat,lon
	R=6378000. #m
	lat1,lon1=p1[0],p1[1]
	lat2,lon2=p2[0],p2[1]

	A = (np.pi/180.)*R*R* abs(np.sin(lat1*np.pi/180.)-np.sin(lat2*np.pi/180.))*abs(lon1-lon2)
	print 'Area:',lat1,'N->',lat2,'N\t',lon1,'E->',lon2,'E,\tA=',A

	return A
			
			

def regrid(data,lon,lat):
    	nX = np.arange(-179.5,180.5,1.)
    	nY = np.arange( -89.5, 90.5,1.)
    	
    	if lat.ndim ==2:
    		   oldLon, oldLat = lon,lat		
    	else:
    		if data.ndim >1:
 	   		oldLon, oldLat = np.meshgrid(lon,lat)
 	   	else:
 	   		oldLon, oldLat,data = lon,lat,data

    	newLon, newLat = np.meshgrid(nX,nY)
    	
    	crojp1 = ccrs.PlateCarree(central_longitude=180.0, )#central_latitude=300.0)
    	crojp2 = ccrs.PlateCarree(central_longitude=180.0, )#central_latitude=300.0)

    	a = img_transform.regrid(data,
    			     source_x_coords=oldLon,
                             source_y_coords=oldLat,
                             source_cs=crojp1,
                             target_proj=crojp2,
                             target_x_points=newLon,
                             target_y_points=newLat
                             )
       # print 'newregid shape:',a.shape                     
	return crojp2, a, newLon,newLat
	
	
			

class shelveMetadata:
   def __init__(self,model='',name='',year='',depthLevel='',newSlice='',xkey='',ykey='',shelve = ''):
   	self.model 	= model
   	self.name 	= name
   	self.year 	= year   	
   	self.depthLevel	= depthLevel
   	self.newSlice 	= newSlice
   	self.xkey 	= xkey   	   	   	
   	self.ykey 	= ykey   	   	   	   	
   	self.shelve 	= shelve   	      	
   def __repr__(self):
	string = ''   
   	for a in [ self.model,self.name,self.year,self.depthLevel,self.newSlice,self.xkey,self.ykey]:
   		string+=', '+a
   	string+='\nshelve:'+self.shelve
        return string
   def __str__(self):
	string = ''   
   	for a in [ self.model,self.name,self.year,self.depthLevel,self.newSlice,self.xkey,self.ykey]:
   		if len(a) ==0:continue
   		string+='-'+a
        return string   
       
        
        
def reducesShelves(AllShelves,models=[],names=[],years=[],depthLevels=[],sliceslist=[],):
	"""
	This routine takes the AllShelves dictionary of shelveMetadata then returns a list of shelves.
	This is useful for producing a target diagram, or a patterns plot.
	requirements is a list of models, slices, depthLevels that are required.
	"""
	emptySMDtype = type(shelveMetadata())
	outArray = []
	for shelveMD in AllShelves:
		if type(shelveMD) != emptySMDtype:
			print "somewhere, this is not a shelveMD:",shelveMD
			assert False
		
		if len(models) 		and shelveMD.model 	not in models:	continue
		if len(names) 		and shelveMD.name 	not in names:	continue
		if len(years) 		and shelveMD.year 	not in years:	continue
		if len(depthLevels) 	and shelveMD.depthLevel not in depthLevels:continue
		if len(sliceslist) 	and shelveMD.newSlice 	not in sliceslist:continue
		outArray.append(shelveMD.shelve)
	return outArray		
	
class listShelvesContents:
   def __init__(self,AllShelves):
	"""
	This routine takes the AllShelves dictionary of shelveMetadata then produces lists of all components.
	"""
	models={}
	names={}
	years={}
	depthLevels={}
	sliceslist = {}
	emptySMDtype = type(shelveMetadata())
	for shelveMD in AllShelves:
		if type(shelveMD) != emptySMDtype:
			print "somewhere, this is not a shelveMD:",shelveMD
			assert False
		
		models[shelveMD.model] 		= True
		names[shelveMD.name] 		= True
		years[shelveMD.year] 		= True
		depthLevels[shelveMD.depthLevel]= True				
		sliceslist[shelveMD.newSlice] 	= True						

	self.models = models.keys()
	self.names = names.keys()
	self.years = years.keys()
	self.depthLevels = depthLevels.keys()
	self.sliceslist = sliceslist.keys()
   def __repr__(self):
	string = ''   
   	for a in [ self.models,self.names,self.years,self.depthLevels,self.sliceslist]:
   		string+=', '+' '.join(a)
   	string+='\nshelve contents:'+self.shelve
        return string
   def __str__(self):
	string = ''   
   	for a in [ self.models,self.names,self.years,self.depthLevels,self.sliceslist]:
   		if len(a) ==0:continue
   		string+='-'+' '.join(a)
        return string   
					

def getSlicesDict():
	slicesDict = {}
	standardCuts = ['5-95pc','ignoreInlandSeas','OffShelf','ignoreExtraArtics','aboveZero',]	
	months = [month_name[i+1] for i in xrange(0,12) ]#{month_name[i+1]:i for i in xrange(0,12) }

	
	
		
	#depthRanges	=['OffShelf','maskBelowBathy', 'OnShelf',] 
	depthRanges	=['Depth_0-50m','Depth_50-100m','Depth_100-200m','Depth_200-500m','Depth_500-1000m','Depth_1000-2000m','Depth_2000m']
	percentiles	=['0-1pc','1-5pc','5-25pc',
			  '25-40pc','40-60pc','60-75pc',
			  '75-95pc','95-99pc','99-100pc',]
	latregions	=['NorthTemperate','SouthTemperate','NorthTropics',
			  'Equatorial',  'SouthTropics','Antarctic',
			  'NorthArctic',
			  'Arctic','Tropics','Temperate']
	Hemispheres	=['NorthHemisphere','SouthHemisphere',]
	Seas		=['ignoreMediteranean','BlackSea','ignoreBlackSea',
			  'RedSea','BalticSea','PersianGulf',
			  'ignoreInlandSeas',	
			  'ignoreRedSea', 'ignoreBalticSea','ignorePersianGulf',]
	Oceans		=['SouthPacificOcean',  'ArcticOcean',
			  'AntarcticOcean','NorthAtlanticOcean','SouthAtlanticOcean',
			  'NorthPacificOcean','IndianOcean', 
			  'EquatorialPacificOcean','EquatorialAtlanticOcean',
			 ]#'ignoreExtraArtics','ignoreMidArtics','ignoreArtics','ignoreMoreArtics',]
	QualityCuts 	=['Overestimate','Underestimate','Overestimate_2sig',
			  'Underestimate_2sig','Overestimate_3sig','Underestimate_3sig', 
			  'Matched','OffAxis','1-99pc',
			  '5-95pc','0-99pc',]
	Seasons		=['JFM','AMJ','JAS','OND'] 
	Transects	= ['AtlanticTransect', 'PacificTransect','SouthernTransect','10N','10S']
	Misc		= ['HighLatWinter',]
	BGCVal		= ['Global','ignoreInlandSeas','Equator10', 'ArcticOcean','NorthernSubpolarAtlantic','NorthernSubpolarPacific','SouthernOcean','Remainder',]
	
	OceanMonths  		= { o: [ (o,m) for m in months] for o in Oceans}
	OceanSeasons 		= { o: [ (o,m) for m in Seasons] for o in Oceans}	
	HemispheresMonths  = { o: [ (o,m) for m in months] for o in Hemispheres}
	HemispheresSeasons = { o: [ (o,m) for m in Seasons] for o in Hemispheres}	
	
	newSlices =['All','Standard',]
	newSlices.extend(months)
	newSlices.extend(depthRanges)
	newSlices.extend(percentiles)
	newSlices.extend(latregions)	
	newSlices.extend(QualityCuts)	
	newSlices.extend(Seas)		
	newSlices.extend(Oceans)
	newSlices.extend(Hemispheres)	
	newSlices.extend(Seasons)
	newSlices.extend(OceanSeasons)
	newSlices.extend(OceanMonths)
	newSlices.extend(HemispheresMonths)
	newSlices.extend(HemispheresSeasons)	
	newSlices.extend(Transects)		
	newSlices.extend(Misc)			
	newSlices.extend(BGCVal)				
	for om,keys in OceanMonths.items(): 		newSlices.extend(keys)
	for om,keys in OceanSeasons.items(): 		newSlices.extend(keys)
	for om,keys in HemispheresMonths.items(): 	newSlices.extend(keys)
	for om,keys in HemispheresSeasons.items(): 	newSlices.extend(keys)
	

	slicesDict['Default'] 		= ['All','Standard',]		
	slicesDict['StandardCuts'] 	= standardCuts
	slicesDict['AllSlices'] 	= newSlices
	slicesDict['Months'] 		= months
	slicesDict['Hemispheres'] 	= Hemispheres	
	slicesDict['Oceans'] 		= Oceans	
	slicesDict['Seasons'] 		= Seasons
	slicesDict['depthRanges'] 	= depthRanges	
	slicesDict['Transects'] 	= Transects		
	slicesDict['Misc'] 		= Misc			
	slicesDict['BGCVal'] 		= BGCVal				
	for om,keys in OceanMonths.items(): 		slicesDict[om+'Months' ] = keys
	for om,keys in OceanSeasons.items(): 		slicesDict[om+'Seasons'] = keys
	for om,keys in HemispheresMonths.items(): 	slicesDict[om+'Months' ] = keys
	for om,keys in HemispheresSeasons.items(): 	slicesDict[om+'Seasons'] = keys
	
	return slicesDict
slicesDict = getSlicesDict()



def populateSlicesList(#plotallcuts = False,
		 plotDefaults		=True,		 	
		 plotMonths		=0,#True
		 plotdepthRanges	=0,#True	
		 plotpercentiles	=0,#True	
		 plotLatRegions		=0,#True
		 plotQualityCuts	=0,#True
		 plotSeas		=0,#True		 
		 plotOceans		=0,#True	
		 plotHemispheres	=0,		 
		 plotSeasons		=0,# True
		 plotOceanSeasons	=0,# True		 
		 plotOceanMonths   	=0,	 	 	 
		 plotHemispheresMonths  =0,
		 plotHemispheresSeasons =0,
		 plotTransects		=0,
 		 plotMisc		=0,):
				 

	if plotDefaults:	newSlices = ['All', 'Standard',]# Defaults
	else:			newSlices = []
	if plotMonths: 	 	newSlices.extend(slicesDict['Months'])
	if plotdepthRanges: 	newSlices.extend(slicesDict['depthRanges'])
	if plotpercentiles: 	newSlices.extend(slicesDict['percentiles'])
	if plotLatRegions:	newSlices.extend(slicesDict['latregions'])	
	if plotQualityCuts: 	newSlices.extend(slicesDict['QualityCuts'])		
	if plotSeas: 	 	newSlices.extend(slicesDict['Seas'])			
	if plotOceans: 	 	newSlices.extend(slicesDict['Oceans'])
	if plotHemispheres: 	newSlices.extend(slicesDict['Hemispheres'])
	if plotSeasons: 	newSlices.extend(slicesDict['Seasons'])
	if plotTransects: 	newSlices.extend(slicesDict['Transects'])	
	if plotMisc: 		newSlices.extend(slicesDict['Misc'])		
		
	if plotOceanMonths:	
		for o in slicesDict['Oceans']:		newSlices.extend(slicesDict[o+'Months'])				
	if plotOceanSeasons:	
		for o in slicesDict['Oceans']:		newSlices.extend(slicesDict[o+'Seasons'])
	if plotHemispheresMonths:	
		for o in slicesDict['Hemispheres']:	newSlices.extend(slicesDict[o+'Months'])		
	if plotHemispheresSeasons:	
		for o in slicesDict['Hemispheres']:	newSlices.extend(slicesDict[o+'Seasons'])
		
	
	return newSlices

		      	
def makeMask(name,newSlice, xt,xz,xy,xx,xd,debug=False):	  
	if debug:print "makeMask:\tmakeMask:\tinitialise:\t",name, '\t',newSlice
		
	if newSlice in ['OffAxis', 'Overestimate','Underestimate','Matched', 
			'Overestimate_2sig','Underestimate_2sig', 
			'Overestimate_3sig','Underestimate_3sig',]:
		print "makeMask:\tSlice", newSlice, "requires both datasets, and you should never see this"
		assert False

  	if newSlice in ['All', 'Global','regionless','layerless']: 		
 # 		return
  		m = np.zeros(len(xd))		
  		for a in [xt,xz,xy,xx,xd]:
  			try: m+=a.mask
  			except:pass
  		return m
			  	
	nmask = np.ones(len(xd))	# everything masked	
	nmask = np.zeros(len(xd))	# nothing masked	

 	if newSlice in ['maskBelowBathy', 'OnShelf','OffShelf',]:
		#bathync = ncdfView("data/ORCA1bathy.nc",Quiet=True)
		bathync = Dataset("data/ORCA1bathy.nc",'r')		
		bathy = abs(bathync.variables["bathymetry"][:])
		latcc, loncc =  bathync.variables["lat"][:], bathync.variables["lon"][:]	
		bathync.close()
		shelfDepth=500.
		shelveFn = folder("shelves/MatchingMasks/")+"diag_maskMask.shelve"
		try:
			s = shOpen(shelveFn)		
			lldict  = s['lldict']
			s.close()
		except:	lldict={}	
	
		print "Bathy mask: before mask:", newSlice, nmask.sum(), 'of', len(nmask)			  	
		i =0
		for i,z in enumerate(xz):
			try:
				la,lo = lldict[(xy[i],xx[i])]
			except:
				la,lo = getOrcaIndexCC(xy[i],xx[i],latcc,loncc,debug=False)
				lldict[(xy[i],xx[i])] = la,lo
			if la==lo==-1:
				print "Corner case:", la,lo,bathy[la,lo] 
				nmask[i]=1
			if newSlice == "maskBelowBathy":
				if (bathy[la,lo]-10.) > abs(z): nmask[i]=1	
			if newSlice == "OnShelf":
				if  bathy[la,lo] >= shelfDepth: nmask[i]=1	
			if newSlice == "OffShelf":
				if  bathy[la,lo] < shelfDepth:  nmask[i]=1
		
			if i%100000==0:# or i==(len(xz)+1):
			    try:
				s = shOpen(shelveFn)		
				s['lldict'] = lldict 
				s.close()
			    except:
			    	print "makeMask:\tWARNING:\tUnable to save lldict at this time"
		if i > 0:
		    try:
			s = shOpen(shelveFn)		
			s['lldict'] = lldict 
			s.close()
		    except:
		    	print "makeMask:\tWARNING:\tUnable to save lldict at this time"
		print "Bathy mask:", newSlice, nmask.sum(), 'of', len(nmask)
		return nmask
		
	

	if newSlice in ['1-99pc','5-95pc','0-99pc'] or newSlice in ['0-1pc','1-5pc','5-25pc','25-40pc','40-60pc','60-75pc','75-95pc','95-99pc','99-100pc',]:	  		
		if newSlice in ['0-1pc','1-5pc','5-25pc','25-40pc','40-60pc','60-75pc','75-95pc','95-99pc','99-100pc',]:
		  	tmp  = newSlice.replace('pc','').split('-')
		  	pcmin,pcmax = float(tmp[0]),float(tmp[1])
		  	print newSlice, pcmin, pcmax
		  	if pcmin == 0:	ymin = yd.min()
			else:		ymin = scoreatpercentile(yd,pcmin)
		  	if pcmax == 100:ymax = yd.max()
			else:		ymax = scoreatpercentile(yd,pcmax)
				
		if newSlice in ['1-99pc',]:
			ymin = scoreatpercentile(xd,1)
			ymax = scoreatpercentile(xd,99)
		if newSlice in ['5-95pc',]:
			ymin = scoreatpercentile(xd,5)
			ymax = scoreatpercentile(xd,95)
		
		if newSlice in ['0-99pc',]:
			ymin = xd.min()
			ymax = scoreatpercentile(xd,99)	
		print  "makeMask:\t",newSlice,ymin,ymax
		return  np.ma.masked_outside(xd,ymin, ymax).mask
				
	months = {month_name[i+1]:i for i in xrange(0,12) }
	if newSlice in months.keys():
		print "masking a month:",newSlice,xt[0], xt[-1]
		return np.ma.masked_where( xt != months[newSlice],nmask).mask 

	if newSlice =='JFM':	
		return np.ma.masked_where( ~(xt== months['January'])+(xt== months['February'])+(xt== months['March']),nmask).mask 
	if newSlice =='AMJ':	
		return np.ma.masked_where(~(xt==months['April'])+(xt==months['May'])+(xt==months['June']),nmask).mask 
	if newSlice =='JAS':	
		return np.ma.masked_where(~(xt==months['July'])+(xt==months['August'])+(xt==months['September']),nmask).mask 
	if newSlice =='OND':	
		return np.ma.masked_where(~(xt==months['October'])+(xt==months['November'])+(xt==months['December']),nmask).mask 						
	
	
	if newSlice == "0.1":	return np.ma.masked_where( xd==0.1, xd).mask
	if newSlice == "0.2":	return np.ma.masked_where( xd==0.2, xd).mask
	if newSlice == "0.01":	return np.ma.masked_where( xd==0.01, xd).mask	
	
	
	if newSlice == 'Shallow':	return np.ma.masked_where( xz > 200.,nmask).mask
	if newSlice == 'Depth':		return np.ma.masked_where( xz < 200.,nmask).mask
	if newSlice == 'Zoom':		return np.ma.masked_where( xd > 10.,nmask).mask 
	if newSlice == 'Zoom5':		return np.ma.masked_where( xd > 5., nmask).mask 
	if newSlice == 'Zoom2':		return np.ma.masked_where( xd > 2., nmask).mask 
	if newSlice == 'nonZero':	return np.ma.masked_where( xd == 0.,nmask).mask 			
	if newSlice == 'aboveZero':	return np.ma.masked_where( xd <= 0.,nmask).mask
	if newSlice == 'Tropics':	return np.ma.masked_where( abs(xy) >23.,nmask).mask 			
	if newSlice == 'Equatorial':	return np.ma.masked_where( abs(xy) >7.,nmask).mask 
	if newSlice == 'Temperate':	return np.ma.masked_where( (abs(xy) <23.)+(abs(xy) >60.),nmask).mask 	
	if newSlice == 'NorthTropics':	return np.ma.masked_where( (xy >23.)+(xy < 7.),nmask).mask 			
	if newSlice == 'SouthTropics':	return np.ma.masked_where( (xy <-23.)+(xy > -7.),nmask).mask 				
	if newSlice == 'NorthTemperate':return np.ma.masked_where( (xy <23.)+(xy >60.),nmask).mask 			
	if newSlice == 'SouthTemperate':return np.ma.masked_where( (xy >-23.)+(xy <-60.),nmask).mask 	

	if newSlice == 'NorthHemisphere':	return np.ma.masked_where( xy < 0.,nmask).mask
	if newSlice == 'SouthHemisphere':	return np.ma.masked_where( xy > 0.,nmask).mask	

	if newSlice == 'AtlanticTransect':	return np.ma.masked_where( (xx > -26.)+(xx<-30.),nmask).mask
	if newSlice == 'PacificTransect':	return np.ma.masked_where( (xx > -139.)+(xx<-143.),nmask).mask
	if newSlice == '10N':			return np.ma.masked_where( (xy >  12.)+(xy<  8.),nmask).mask
	if newSlice == '10S':			return np.ma.masked_where( (xy >  -8.)+(xy<-12.),nmask).mask
	if newSlice == 'SouthernTransect':	return np.ma.masked_where( (xy > -55.)+(xy<-59.),nmask).mask		
		

	if newSlice == 'Arctic':	return np.ma.masked_where( abs(xy) < 60.,nmask).mask
	if newSlice == 'Antarctic':	return np.ma.masked_where( xy > -60.,nmask).mask 			
	if newSlice == 'NorthArctic':	return np.ma.masked_where( xy < 60.,nmask).mask 														
	if newSlice == 'SalArtifact': 	return np.ma.masked_where( (xd > 15.)+(xd < 10.),nmask).mask 
	if newSlice == 'NitArtifact':	return np.ma.masked_where( (xd > 6.)+(xd < 2.),  nmask).mask 
	if newSlice == 'Depth_0-10m': 	return np.ma.masked_where( abs(xz) > 10.,nmask).mask 
	if newSlice == 'Depth_10-20m': 	return np.ma.masked_where( (abs(xz) < 10.)+(abs(xz) > 20.),nmask).mask 
	if newSlice == 'Depth_20-50m': 	return np.ma.masked_where( (abs(xz) > 20.)+(abs(xz) > 50.),nmask).mask 
	if newSlice == 'Depth_50-100m': return np.ma.masked_where( (abs(xz) < 50.)+(abs(xz) > 100.),nmask).mask
	if newSlice == 'Depth_100-500m':return np.ma.masked_where( (abs(xz) < 100.)+(abs(xz) > 500.),nmask).mask
	if newSlice == 'Depth_500m': 	return np.ma.masked_where(  abs(xz) < 500.,nmask).mask	
		
	if newSlice == 'Depth_0-50m': 	return np.ma.masked_where( abs(xz) > 50.,nmask).mask
	if newSlice == 'Depth_50-100m': return np.ma.masked_where( (abs(xz) < 50.)+(abs(xz) > 100.),nmask).mask		
	if newSlice == 'Depth_100-200m':return np.ma.masked_where( (abs(xz) < 100.)+(abs(xz) > 200.),nmask).mask
	if newSlice == 'Depth_200-500m':return np.ma.masked_where( (abs(xz) < 200.)+(abs(xz) > 500.),nmask).mask	
	if newSlice == 'Depth_500-1000m':return np.ma.masked_where( (abs(xz) < 500.)+(abs(xz) > 1000.),nmask).mask
	if newSlice == 'Depth_1000-2000m':return np.ma.masked_where( (abs(xz) < 1000.)+(abs(xz) > 2000.),nmask).mask	
	if newSlice == 'Depth_1000m': 	return np.ma.masked_where(  abs(xz) < 1000.,nmask).mask	
	if newSlice == 'Depth_2000m': 	return np.ma.masked_where(  abs(xz) < 2000.,nmask).mask	
		
	if newSlice == 'TypicalIron': 	return np.ma.masked_where( (xd<=0.) *(xd<=4.),nmask).mask 
	
	if newSlice == 'BlackSea': 	
		mx = np.ma.masked_outside(xx, 25.9,41.7).mask
		my = np.ma.masked_outside(xy, 39.8,48.1).mask				
		return np.ma.masked_where( mx+my,nmask).mask 
		
	if newSlice == 'ignoreBlackSea':
		mx = np.ma.masked_inside(xx, 25.9,41.7).mask
		my = np.ma.masked_inside(xy, 39.8,48.1).mask				
		return np.ma.masked_where( mx*my,nmask).mask 	
		
	if newSlice == 'BalticSea': 	
		mx = np.ma.masked_outside(xx, 12.5,30.7).mask
		my = np.ma.masked_outside(xy, 53.0,66.4).mask				
		return np.ma.masked_where( mx+my,nmask).mask 
		
	if newSlice == 'ignoreBalticSea':
		mx = np.ma.masked_inside(xx, 12.5,30.7).mask
		my = np.ma.masked_inside(xy, 53.0,66.4).mask				
		return np.ma.masked_where( mx*my,nmask).mask 	

	if newSlice == 'RedSea': 	
		mx = np.ma.masked_outside(xx, 30.0,43.0).mask
		my = np.ma.masked_outside(xy, 12.4,30.4).mask				
		return np.ma.masked_where( mx+my,nmask).mask 
		
	if newSlice == 'ignoreRedSea':
		mx = np.ma.masked_inside(xx, 30.0,43.0).mask
		my = np.ma.masked_inside(xy, 12.4,30.4).mask				
		return np.ma.masked_where( mx*my,nmask).mask 	
		
	if newSlice == 'PersianGulf': 	
		mx = np.ma.masked_outside(xx, 47.5, 56.8).mask
		my = np.ma.masked_outside(xy, 22.3, 32.1).mask				
		return np.ma.masked_where( mx+my,nmask).mask 
		
	if newSlice == 'ignorePersianGulf':
		mx = np.ma.masked_inside(xx, 47.5, 56.8).mask
		my = np.ma.masked_inside(xy, 22.3, 32.1).mask				
		return np.ma.masked_where( mx*my,nmask).mask 										
		
	if newSlice == 'ignoreCaspian':
		mx = np.ma.masked_inside(xx,45.0,  55.0).mask * np.ma.masked_inside(xy, 35., 48.).mask 	# caspian
		return np.ma.masked_where( mx,nmask).mask 
		
	if newSlice == 'ignoreMediteranean':
		mx  = np.ma.masked_inside(xx, -5.8, 42.5).mask #E
		my  = np.ma.masked_inside(xy, 30., 43.).mask	#N			
		mx2 = np.ma.masked_inside(xx, 0., 20.).mask #E
		my2 = np.ma.masked_inside(xy, 32., 47.).mask #N
		m = mx*my+ mx2*my2
		return np.ma.masked_where( m,nmask).mask 		

	if newSlice in ['ignoreInlandSeas', 'IndianOcean']: 
		mx = np.ma.masked_inside(xx, 47.5,  56.8).mask * np.ma.masked_inside(xy, 22.3, 32.1).mask	
		mx += np.ma.masked_inside(xx, 30.0, 43.0).mask * np.ma.masked_inside(xy, 12.4,30.4).mask	
		mx += np.ma.masked_inside(xx, 12.5, 30.7).mask * np.ma.masked_inside(xy, 53.0,66.4).mask
		mx += np.ma.masked_inside(xx, 25.9, 41.7).mask * np.ma.masked_inside(xy, 39.8,48.1).mask		
		mx += np.ma.masked_inside(xx, -5.8, 42.5).mask * np.ma.masked_inside(xy, 30., 43.).mask
		mx += np.ma.masked_inside(xx, 0.0,  20.0).mask * np.ma.masked_inside(xy, 32., 47.).mask 
		mx += np.ma.masked_inside(xx,45.0,  55.0).mask * np.ma.masked_inside(xy, 35., 52.).mask 	# caspian
		if newSlice == 'ignoreInlandSeas':return np.ma.masked_where( mx,nmask).mask 		
		mx += np.ma.masked_outside(xx, 25.,100.).mask
		my = np.ma.masked_outside(xy, -50.,30.).mask
		if newSlice == 'IndianOcean':return np.ma.masked_where( mx+my,nmask).mask 

	if newSlice == 'SouthernOcean': 	return np.ma.masked_where(  xy >-40.,nmask).mask 
	if newSlice == 'AntarcticOcean': 	return np.ma.masked_where(  xy >-50.,nmask).mask 
	#if newSlice == 'ArcticOcean': 		return np.ma.masked_where(  xy < 60.,nmask).mask 
	if newSlice == 'ignoreArtics':		return np.ma.masked_outside(xy,-70., 70.).mask
	if newSlice == 'ignoreMidArtics':	return np.ma.masked_outside(xy,-65., 65.).mask
	if newSlice == 'ignoreMoreArtics':	return np.ma.masked_outside(xy,-60., 60.).mask
	if newSlice == 'ignoreExtraArtics':	return np.ma.masked_outside(xy,-50., 50.).mask 
	if newSlice == 'NorthAtlanticOcean': 	return np.ma.masked_outside(makeLonSafeArr(xx), -80.,0.).mask + np.ma.masked_outside(xy, 10.,60.).mask
	if newSlice == 'SouthAtlanticOcean':	return np.ma.masked_outside(makeLonSafeArr(xx), -65.,20.).mask + np.ma.masked_outside(xy, -50.,-10.).mask
	if newSlice == 'EquatorialAtlanticOcean':
	
		return np.ma.masked_outside(makeLonSafeArr(xx), -65.,20.).mask + np.ma.masked_outside(xy, -15.,15.).mask

	if newSlice == 'ArcticOcean': 	
		mx = np.ma.masked_where(  xy < 60.,nmask).mask 
		mx+= np.ma.masked_inside(xx, -45., 15.).mask * np.ma.masked_inside(xy, 50.,80.).mask
		
		return np.ma.masked_where( mx,nmask).mask 

	if newSlice == 'NorthernSubpolarAtlantic':
		mx = np.ma.masked_outside(xx,-80., -3. ).mask + np.ma.masked_outside(xy,40., 60. ).mask
		mx *= np.ma.masked_outside(xx, -45., 15.).mask + np.ma.masked_outside(xy, 60.,80.).mask
		return mx	

	if newSlice == 'NorthernSubpolarPacific':
		mx = np.ma.masked_inside(xx,-100., 120. ).mask
		mx += np.ma.masked_inside(xx,260., 365. ).mask		
		mx += np.ma.masked_outside(xy,40., 60. ).mask
		return np.ma.masked_where( mx,nmask).mask 		

	if newSlice == 'Remainder':
		mx = makeMask(name,'ignoreInlandSeas', xt,xz,xy,xx,xd)
		mx += np.ma.masked_inside(xy,-10., 10. ).mask
		mx += np.ma.masked_outside(abs(xy),-40., 40. ).mask		
		return np.ma.masked_where( mx,nmask).mask 		

 	if newSlice == 'Equator10':
		mx = makeMask(name,'ignoreInlandSeas', xt,xz,xy,xx,xd)
                mx += np.ma.masked_outside(xy,-10., 10. ).mask
                return mx 
 
  					
	
	if newSlice == 'NorthPacificOcean':
		mx = np.ma.masked_inside(xx,-100., 120. ).mask
		mx += np.ma.masked_inside(xx,260., 365. ).mask		
		mx += np.ma.masked_outside(xy,10., 60. ).mask
		return mx

	if newSlice == 'EquatorialPacificOcean':
		mx = np.ma.masked_inside(xx,-83., 120. ).mask
		mx += np.ma.masked_inside(xx,260., 365. ).mask		
		mx += np.ma.masked_outside(xy,-15., 15. ).mask
		return mx
		
	
	if newSlice == 'SouthPacificOcean': 	
		mx = np.ma.masked_inside(xx,-70., 140. ).mask
		mx += np.ma.masked_inside(xx,290., 365. ).mask		
		my = np.ma.masked_outside(xy,-10., -50. ).mask
		return np.ma.masked_where( mx+my,nmask).mask 
		
		
	if newSlice == 'HighLatWinter': 
		NHwinter = np.ma.masked_where( ~((xt == months['January'])+(xt == months['February']) +(xt == months['March'])    ) ,nmask).mask
		SHwinter = np.ma.masked_where( ~((xt == months['July'])   +(xt == months['August'])   +(xt == months['September'])) ,nmask).mask
		print "HighLatWinter masking:\tNHwinter:", NHwinter.sum(),'SH:', SHwinter.sum(), 'of',nmask.sum()
		
		mnhw = np.ma.masked_where( (xy <  45.) + NHwinter ,nmask).mask
		mshw = np.ma.masked_where( (xy > -45.) + SHwinter ,nmask).mask 
		return   np.ma.masked_where( mnhw*mshw,nmask).mask 
		
		
				
	print "Mask region not accepted:",newSlice
	assert False		      	
		      		
		      		
####
# Some functions for maniulating data:
def NoChange(nc,keys):	return nc.variables[keys[0]][:]
def N2Biomass(nc,keys):	return nc.variables[keys[0]][:]* 79.573
def mul1000(nc,keys):	return nc.variables[keys[0]][:]* 1000.
def div1000(nc,keys):	return nc.variables[keys[0]][:]/ 1000.	
def div1e6(nc,keys):	return nc.variables[keys[0]][:]/ 1.e6	

def applymask(nc,keys):	return np.ma.masked_where(nc.variables[keys[1]][:]==0.,nc.variables[keys[0]][:])
def sums(nc,keys):	
	a = nc.variables[keys[0]][:]
	for k in keys[1:]:a += nc.variables[k][:]
	return a 
def oxconvert(nc,keys): return nc.variables[keys[0]][:] *44.661
def convertkgToM3(nc,keys): return nc.variables[keys[0]][:]* 1.027

# 1 ml/l = 103/22.391 = 44.661 umol/l
# http://ocean.ices.dk/Tools/UnitConversion.aspx
	
tdicts = {	'ZeroToZero': {i  :i     for i in xrange(12)},		
		'OneToOne':   {i+1:i+1   for i in xrange(12)},
		'OneToZero':  {i+1:i     for i in xrange(12)},
		'ZeroToOne':  {i  :i+1   for i in xrange(12)},			
	}		      		

def extractData(nc, details,key = ['',]):
  	""" 	This loads the data based on the instructions from details dictionairy.
  		If you want to do something funking to the data before plotting it,
  			just create a new convert function in getMT().
  		details dict usually contains: {'name': 'Chlorophylla', 'vars':['Chlorophylla',], 'convert': ukp.div1000,'units':'ug/L'}
  	"""
  	
	if isinstance(details,dict): 
  		keys = details.keys()
  		print "extractData: details is a dict", details.keys()
  		
  	elif len(key) and key in nc.variables.keys():
  		print "extractData: details Not a dict:", details,'but, the key is valid:',key
  		return np.ma.array(nc.variables[key][:])  	
 		
	if 'convert' in keys and 'vars' in keys:	
		xd = np.ma.array(details['convert'](nc,details['vars']))
		return xd
  	
  	print "extractData:\t you shouldn't get here", details, key
  	assert False
  	
  	
  	
  	
		      		
		      		
