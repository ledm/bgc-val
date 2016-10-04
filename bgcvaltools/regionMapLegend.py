#!/usr/bin/ipython
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

"""
.. module:: regionMapLegend 
   :platform: Unix
   :synopsis: Tool to make a plot showing various regions.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

from paths import orcaGridfn, WOAFolder_annual
from netCDF4 import Dataset
import numpy as np
import UKESMpython as ukp
from matplotlib import pyplot
import cartopy.crs as ccrs
from bgcvaltools.pftnames import getLongName


regionList	= [#'Global', 'ignoreInlandSeas',
  		'SouthernOcean','Remainder',
		'Equator10', 
		'NorthernSubpolarAtlantic','NorthernSubpolarPacific','ArcticOcean',
		]

def robinPlotCustom(lons,lats,data,filename,title, zrange=[-100,100],drawCbar=True,cbarlabel='',doLog=False,dpi=100,cmapname='default',crude=False):
	####
	# Based on robinplotSingle
	
	fig = pyplot.figure()
	fig.set_size_inches(10,5)

	lons = np.array(lons)
	lats = np.array(lats)
	data = np.ma.array(data)
	
	rbmi = min([data.min(),])
	rbma = max([data.max(),])
	
	if rbmi * rbma >0. and rbma/rbmi > 100.: doLog=True

	print lons.shape,lats.shape,data.shape
	lon0 = 0.#lons.mean()
	if crude:
		ax = pyplot.subplot(111)#,projection=ccrs.PlateCarree(central_longitude=lon0, ))
		im = pyplot.scatter(lats,lons,c=data,lw=0.,s=3,cmap='viridis',vmin=rbmi,vmax=rbma,)
		#pyplot.colorbar(im)
		#title, zrange=[rbmi,rbma],lon0=lon0,drawCbar=False,cbarlabel=cbarlabel,doLog=doLog,cmap = cmapname)	
	else:
		ax = pyplot.subplot(111,projection=ccrs.PlateCarree(central_longitude=lon0, ))
		fig,ax,im = ukp.makemapplot(fig,ax,lons,lats,data,title, zrange=[rbmi,rbma],lon0=lon0,drawCbar=False,cbarlabel=cbarlabel,doLog=doLog,cmap = cmapname)


          
          
	cmap = im.get_cmap()
	#for i in [0,10,100,1000,10000,1000000,100000]:
	#	print i, cmap(i), data.min(),data.max()
	leg=True
	if leg:
		# Shrink current axis's height by 10% on the bottom
		box = ax.get_position()
		ax.set_position([box.x0, box.y0 + box.height * 0.1,
				 box.width, box.height * 0.9])
			
		for i,r in enumerate(regionList):
			c = cmap((i)/5.)
			print i,r,c
			pyplot.plot([],[],lw=8,color=c,label=getLongName(r))

		# Put a legend below current axis
		leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
			  ncol=3,prop={'size':9})
			  	
		#leg = pyplot.legend(loc='lower center',ncol=3, )
		leg.draw_frame(False) 
		leg.get_frame().set_alpha(0.)		
	
	print "robinPlotSingle.py:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()


def robinPlotTransects(lons,lats,data,filename,title,legends=[], zrange=[-100,100],drawCbar=True,cbarlabel='',doLog=False,dpi=100,cmapname='default',crude=False):
	####
	# Based on robinplotSingle
	
	fig = pyplot.figure()
	fig.set_size_inches(10,5)

	lons = np.array(lons)
	lats = np.array(lats)
	data = np.ma.array(data)
	
	rbmi = min([data.min(),])
	rbma = max([data.max(),])
	
	if rbmi * rbma >0. and rbma/rbmi > 100.: doLog=True

	print lons.shape,lats.shape,data.shape
	lon0 = 0.#lons.mean()
	if crude:
		ax = pyplot.subplot(111)#,projection=ccrs.PlateCarree(central_longitude=lon0, ))
		im = pyplot.scatter(lats,lons,c=data,lw=0.,s=3,cmap='viridis',vmin=rbmi,vmax=rbma,)
		#pyplot.colorbar(im)
		#title, zrange=[rbmi,rbma],lon0=lon0,drawCbar=False,cbarlabel=cbarlabel,doLog=doLog,cmap = cmapname)	
	else:
		ax = pyplot.subplot(111,projection=ccrs.PlateCarree(central_longitude=lon0, ))
		fig,ax,im = ukp.makemapplot(fig,ax,lons,lats,data,title, zrange=[rbmi,rbma],lon0=lon0,drawCbar=False,cbarlabel=cbarlabel,doLog=doLog,cmap = cmapname)


          
          
	cmap = im.get_cmap()
	#for i in [0,10,100,1000,10000,1000000,100000]:
	#	print i, cmap(i), data.min(),data.max()
	leg=True
	if leg:
		

		# Shrink current axis's height by 10% on the bottom
		box = ax.get_position()
		ax.set_position([box.x0, box.y0 + box.height * 0.1,
				 box.width, box.height * 0.9])

		for i,r in enumerate(legends):
			c = cmap((i)/(len(legends)-1.))
			print 'making transect legend:',i,r,c
			pyplot.plot([],[],color=c,lw=8,label=getLongName(r))
			
		# Put a legend below current axis
		leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
			  ncol=4,prop={'size':10})
			  	
		#leg = pyplot.legend(loc='lower center',ncol=3, )
		leg.draw_frame(False) 
		leg.get_frame().set_alpha(0.)		
	
	print "robinPlotTransects.py:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()



def makeRegionMap():

	plotAll = 0#True	# make plots for all regions
	imageFold = ukp.folder('images/maps')
	#####
	# Load data.
	nc = Dataset(orcaGridfn,'r')
	bathy = nc.variables['mbathy'][:]
	xy = np.ma.masked_where(bathy==0,nc.variables['nav_lat'][:]).compressed()
	xx = np.ma.masked_where(bathy==0,nc.variables['nav_lon'][:]).compressed()
	nc.close()
	
	cbathy = np.ma.masked_where(bathy==0,bathy).compressed()
	xt = np.ones_like(cbathy)
	xz = np.ones_like(cbathy)

	####
	# Calculate masks, based on lat/lon.
	masks = {}
	for r in regionList:
		masks[r] = ~ukp.makeMask('',r, xt,xz,xy,xx,cbathy,debug=True)
	
	#####
	# Turn mask into one field.
	data = np.zeros_like(cbathy)
	for i,r in enumerate(regionList):
		data += (i+1)* masks[r]
		if plotAll:
			fn = imageFold+'Region_Legend_'+r+'.png'		
			ukp.robinPlotSingle(xy, xx, masks[r],fn,r,drawCbar=True,cbarlabel='',doLog=False,dpi=100,)
	data = np.ma.masked_where(data==0,data)
	
	#####
	# Send it to the plotting tool.
	colourmaps = ['default',]#'rainbow','jet','gist_earth','terrain','ocean','hsv','gist_rainbow','nipy_spectral',]
	for c in colourmaps:
		fn = imageFold+'Region_Legend.png'
		robinPlotCustom(xy, xx, data,fn,'',drawCbar=False,cbarlabel='',doLog=False,dpi=200,cmapname = c)
		

def makeTransectsMap():
	"""
	Makes a plot of the transect lines.
	"""
	
	plotAll = 0#True	# make plots for all regions
	imageFold = ukp.folder('images/maps/')#Transects')

	#####
	# Load data.
	nc = Dataset(WOAFolder_annual+'/woa13_all_o00_01.nc','r')#Oxy
	oxy = nc.variables['o_mn'][0,0]
	lat = nc.variables['lat'][:]
	lon = nc.variables['lon'][:]
	nc.close()
			
	maps = np.zeros(oxy.shape)

	transects= ['Transect', 'PTransect','SOTransect','Equator']
	
	for i,transect in enumerate(transects):
		i+=1
		single_map = np.zeros(oxy.shape)	
		if transect == 'Transect':	x = -28.
		if transect == 'PTransect': 	x = 200.
	
		if transect in ['Transect','PTransect']:
			k = ukp.getclosestlon(x,lon,debug=True)
			maps[:,k]=i	
			single_map[:,k]=i

		if transect == 'SOTransect':	y = -60.
		if transect == 'Equator':	y =   0.
					
		if transect in ['SOTransect','Equator']:
			k = ukp.getclosestlat(y,lat,debug=True)
			maps[k,:]=i
			single_map[k,:]=i
		singles=False
		if singles:	
			fn = ukp.folder(imageFold+'Transects')+transect+'.png'
			single_map = np.clip(single_map,0,i)		
			single_map = np.ma.masked_where(single_map==0,single_map)
			ukp.robinPlotSingle(lat, lon, single_map,fn,transect,drawCbar=False,cbarlabel='',doLog=False,dpi=100,)
	#maps = np.clip(maps,0,i)
	
	maps = np.ma.masked_where(maps==0,maps)#.compessed()
	fn = imageFold+'Transects_legend.png'
	robinPlotTransects(lat, lon, maps,fn, '',legends=transects,drawCbar=False,cbarlabel='',doLog=False,dpi=200,)

if __name__=="__main__":
	makeTransectsMap()
	
	makeRegionMap()		
	
