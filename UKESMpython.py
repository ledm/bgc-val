from sys import argv
from string import join
from os.path  import exists,getmtime
from os import mkdir, makedirs
from glob import glob
import numpy as np
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
from scipy.stats.mstats import scoreatpercentile
from scipy.stats import linregress
from calendar import month_name
from shelve import open as shOpen

#local imports
from ncdfView import ncdfView
"""	This is a catch all toolkit for the python methods and shorthands used in this code.
"""



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
	
def sliceA(arr,region):
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


	
def robinPlotPair(lons, lats, data1,data2,filename,titles=['',''],lon0=0.,marble=False,drawCbar=True,cbarlabel='',doLog=False,scatter=True,dpi=100,**kwargs):

	fig = pyplot.figure()

	fig.set_size_inches(12,10)

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
		if doLog:	im1 =m1.scatter(x1,y1,c=np.log10(data1),marker="s",alpha=0.9,linewidth='0', **kwargs) 
		else:		im1 =m1.scatter(x1,y1,c=data1,marker="s",alpha=0.9,linewidth='0',**kwargs)
	else:
		xi1,yi1,di1=mapIrregularGrid(m1,ax1,lons,lats,data1,lon0,xres=360,yres=180)
	
		if doLog: im1 = m1.pcolormesh(xi1,yi1,di1,cmap=pyplot.cm.jet,norm = LogNorm() )
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
	
		if doLog: im2 = m2.pcolormesh(xi2,yi2,di2,cmap=pyplot.cm.jet,norm = LogNorm() )
		else:	  im2 = m2.pcolormesh(xi2,yi2,di2,cmap=pyplot.cm.jet) #shading='flat',
	
	if drawCbar:
	    c2 = fig.colorbar(im2,pad=0.05,shrink=0.75)	
	    if len(cbarlabel)>0: c2.set_label(cbarlabel)

	pyplot.title(titles[1])			
		
	print "UKESMpython:\trobinPlotPair: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi,  bbox_inches='tight')		
	pyplot.close()
	

def histPlot(datax, datay,  filename, Title='', labelx='',labely='',xaxislabel='', logx=False,logy=False,nbins=50,dpi=100,minNumPoints = 3):
	print "UKESMpython:\thistplot:\t preparing", Title, datax.size, datay.size
	fig = pyplot.figure()		
	ax = pyplot.subplot(111)
	xmin =  np.ma.min([np.ma.min(datax),np.ma.min(datay)])
	xmax =  np.ma.max([np.ma.max(datax),np.ma.max(datay)])
	
	if xmin*xmax <= 0.:
		logx=False
		print "UKESMpython:\thistPlot:\tx value below zero, can not run log scale.", xmin, '\t',labelx,'(x):', np.ma.min(datax), '\t',labely,'(y):', np.ma.min(datay)
	
	
	if datax.size < minNumPoints and datay.size < minNumPoints:
		print "UKESMpython:\thistPlot:\tThere aren't enough points for a sensible dataplot: ", datax.size
		return		

	
	if logx:
		n, bins, patchesx = pyplot.hist(datax,  histtype='stepfilled', bins=10**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
		n, bins, patchesy = pyplot.hist(datay,  histtype='stepfilled', bins=10**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
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
	pyplot.xlabel(xaxislabel)
	#pyplot.ylabel(labely)
	
	print "UKESMpython:\thistPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi,  bbox_inches='tight')
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
		
	plotrange = [xmin, xmax, ymin, ymax]		



	print "UKESMpython:\tscatterPlot:\trange:",plotrange
	
	if xmin*xmax <= 0. or ymin*ymax <=.0:
		logx=False
		logy=False
		print "UKESMpython:\tscatterPlot:\tx value below zero, can not run log scale.", '\t',labelx,'(x):', xmin, '\t',labely,'(y):', ymin		
	
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
	pyplot.savefig(filename ,dpi=dpi,  bbox_inches='tight')
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
	
def makeLonSafe(lon):
	while True:
		if -180<lon<=180:return lon
		if lon<=-180:lon+=360.
		if lon> 180:lon-=360.		
	
def makeLatSafe(lat):
	while True:
		if -90.<=lat<=90.:return lat
		#print 'You can\'t have a latitude > 90 or <-90',lat
		print "makeLatSafe:\tERROR:\tYou can\'t have a latitude > 90 or <-90", lat
		if lat is masked: return lat
		assert False		
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
		      	
def makeMask(name,newSlice, xt,xz,xy,xx,xd):	  
	print "makePlots:\tmakeMask:\tinitialise:\t",name, '\t',newSlice
		
	if newSlice in ['OffAxis', 'Overestimate','Underestimate','Matched', 
			'Overestimate_2sig','Underestimate_2sig', 
			'Overestimate_3sig','Underestimate_3sig',]:
		print "makeMask:\tSlice", newSlice, "requires both datasets, and you should never see this"
		assert False

  	if newSlice == 'All': return np.zeros(len(xd))		
			  	
	nmask = np.ones(len(xd))	# everything masked	
	nmask = np.zeros(len(xd))	# nothing masked	

 	if newSlice in ['maskBelowBathy', 'OnShelf','OffShelf',]:
		bathync = ncdfView("data/ORCA1bathy.nc",Quiet=True)
		bathy = abs(bathync("bathymetry")[:])
		latcc, loncc =  bathync("lat")[:], bathync("lon")[:]	
		bathync.close()
		shelfDepth=500.
		shelveFn = folder("shelves/MaredatErsemMatch-latlon/"+name)+"diag_"+name+".shelve"
		try:
			s = shOpen(shelveFn)		
			lldict  = s['lldict']
			s.close()
		except:	lldict={}	
	
		print "Bathy mask: before mask:", newSlice, nmask.sum(), 'of', len(nmask)			  	
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
		
			if i%100000==0 or i==(len(xz)+1):
				s = shOpen(shelveFn)		
				s['lldict'] = lldict 
				s.close()			
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
		if newSlice == 'ignoreInlandSeas':return np.ma.masked_where( mx,nmask).mask 		
		mx += np.ma.masked_outside(xx, 25.,100.).mask
		my = np.ma.masked_outside(xy, -50.,30.).mask
		if newSlice == 'IndianOcean':return np.ma.masked_where( mx+my,nmask).mask 

	if newSlice == 'AntarcticOcean': 	return np.ma.masked_where(  xy >-50.,nmask).mask 
	if newSlice == 'ArcticOcean': 		return np.ma.masked_where(  xy < 60.,nmask).mask 
	if newSlice == 'ignoreArtics':		return np.ma.masked_outside(xy,-70., 70.).mask
	if newSlice == 'ignoreMidArtics':	return np.ma.masked_outside(xy,-65., 65.).mask
	if newSlice == 'ignoreMoreArtics':	return np.ma.masked_outside(xy,-60., 60.).mask
	if newSlice == 'ignoreExtraArtics':	return np.ma.masked_outside(xy,-50., 50.).mask 
	if newSlice == 'NorthAtlanticOcean': 	return np.ma.masked_outside(makeLonSafeArr(xx), -80.,0.).mask + np.ma.masked_outside(xy, 10.,60.).mask
	if newSlice == 'SouthAtlanticOcean':	return np.ma.masked_outside(makeLonSafeArr(xx), -65.,20.).mask + np.ma.masked_outside(xy, -50.,-10.).mask

	if newSlice == 'NorthPacificOcean':
		mx = np.ma.masked_inside(xx,-100., 120. ).mask
		mx += np.ma.masked_inside(xx,260., 365. ).mask		
		mx += np.ma.masked_outside(xy,10., 60. ).mask
		return mx
	
	if newSlice == 'SouthPacificOcean': 	
		mx = np.ma.masked_inside(xx,-70., 140. ).mask
		mx += np.ma.masked_inside(xx,290., 365. ).mask		
		my = np.ma.masked_outside(xy,-10., -50. ).mask
		return np.ma.masked_where( mx+my,nmask).mask 
	print "Mask region not accepted:",newSlice
	assert False		      	
		      		
