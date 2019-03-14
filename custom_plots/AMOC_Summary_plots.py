# 1. (Easy) a time series of only UKESM1 u-aw310 for the full length (~1960 to year 3???) applying either a 5 year or 10 year running mean (likely the former).

# 2. A time series (using the same time meaning as in 1...so likely 5 year running mean) that consists of the following:
#    (i) A 250 year segment of the piControl (it probably does not matter what 250 years are chosen).
#    (ii) The ensemble mean (of however many historical runs have completed...think it is now 11), 5 year running mean, of the 165 years of the (11) historical runs
#    (iii) A 5-member ensemble mean for each of the 4 Tier 1 scenarios for the 85 years of the projections.



import numpy as np
from matplotlib import pyplot
from shelve import open as shopen


def movingaverage_DT(data, times, window_len=10.,window_units='years'):
        window_units = window_units.lower()
        if window_units not in ['days','months','years']:
                raise ValueError("movingaverage_DT: window_units not recognised"+str(window_units))

        data = np.ma.array(data)
        times= np.ma.array(times)

        if len(data) != len(times):
                raise ValueError("movingaverage_DT: Data and times are different lengths.")

        #####
        # Assuming time 
        if window_units in ['years',]:  window = float(window_len)/2.
        if window_units in ['months',]: window = float(window_len)/(2.*12.)
        if window_units in ['days',]:   window = float(window_len)/(2.*365.25)

        output = []#np.ma.zeros(data.shape)
        for i,t in enumerate(times):

                tmin = t-window
                tmax = t+window
                arr = np.ma.masked_where((times < tmin) + (times > tmax), data)

                #print [i,t],[tmin,tmax],[t,data[i]], arr.mean(), 'mask:',arr.mask.sum()
                output.append(arr.mean())

        return np.array(output)


def ensemblemean(dicts,operator = 'mean'):
	times = {}
	for job, dic  in dicts.items():
		print job, len(dic)
		for t,d in dic.items():
			try:	times[t].append(d)
			except: times[t] = [d,]
	check_lengths = {}
	for t in sorted(times):
		try: check_lengths[len(times[t])].append(t)
		except: check_lengths[len(times[t])] = [t,]

	times_keys = sorted(times.keys())
	if operator == 'mean':
		means = [np.mean(times[t]) for t in times_keys]
		return times_keys, means
        if operator == 'min':
		for t in times_keys:
			print operator, t, times[t], np.min(times[t])
                means = [np.min(times[t]) for t in times_keys]
                return times_keys, means
        if operator == 'max':
                means = [np.max(times[t]) for t in times_keys]
                return times_keys, means



def getAMOCdata(j):
        fn = '/group_workspaces/jasmin2/ukesm/BGC_data/ldemora/shelves/timeseries/'+j+'/'+j+'_AMOC_26N.shelve'
        shelve = shopen(fn)
	data = shelve['modeldata'][('regionless', 'layerless', 'metricless')]
        shelve.close() 
#	times = sorted(data.keys())		
#	data = [data[t] for t in times]
	return data


def fig1():
	data1 = getAMOCdata('u-aw310')

        times1 = sorted(data1.keys())
        data1 = [data1[t] for t in times1]

	#pyplot.plot(times, amoc,'k',lw=0.3)
	newd1 = movingaverage_DT(data1, times1)
        pyplot.plot(times1, newd1,'k',lw=1.5)     
	pyplot.title('AMOC - 10 year moving average')
        pyplot.ylabel('Sv')
	pyplot.savefig('custom_plots/amoc_fig1.png', dpi=300)
	pyplot.close()
#fig1()



def fig2():
	piControl = ['u-aw310',]
	historical = ['u-az513', 'u-az515', 'u-az524', 'u-bb075', 'u-bb277', 'u-bc179', 'u-bc292', 'u-bc370', 'u-bc470']
	ssp126 = ['u-be509', 'u-be679', 'u-be682', 'u-be393', 'u-be397']
	ssp245 = ['u-be537', 'u-be606', 'u-be683', 'u-be394', 'u-be398']
	ssp370 = ['u-be647', 'u-be690', 'u-be684', 'u-be335', 'u-be395']
	ssp585 = ['u-be653', 'u-be693', 'u-be686', 'u-be392', 'u-be396']                
	
	ssp_jobs = {'piControl':piControl, 'historical': historical, 'SSP 1 2.6': ssp126, 'SSP 2 4.5': ssp245, 'SSP 3 7.0': ssp370,'SSP 5 8.5': ssp585,}
	ssp_colours = {'piControl': 'black', 'historical': 'purple', 'SSP 1 2.6': 'blue', 'SSP 2 4.5': 'green', 'SSP 3 7.0': 'pink','SSP 5 8.5': 'red',}
	order = ['piControl', 'historical', 'SSP 1 2.6', 'SSP 2 4.5', 'SSP 3 7.0','SSP 5 8.5']

	for ssp in order:
		jobs = ssp_jobs[ssp] 
		runs={}
	        for job in jobs:
		        runs[job] = getAMOCdata(job)
		times, data = ensemblemean(runs)
		print ssp
		if ssp == 'piControl': 
			times, data = times[:250], data[:250]
		data = movingaverage_DT(data, times,)
		pyplot.plot(times, data, ssp_colours[ssp], lw=1.5, label = ssp)

	for ssp in order:
		continue
                if ssp == 'piControl':continue
                jobs = ssp_jobs[ssp]
                runs={}
                for job in jobs:
                        datas = getAMOCdata(job)
			times = sorted(datas.keys())             
			data = [datas[t] for t in times]
	                #data = movingaverage_DT(data, times,)
			runs[job] = {t:d for t,d in zip(times,data)}

                times, data_min = ensemblemean(runs, operator='min')
                times, data_max = ensemblemean(runs, operator='max')
#		for t, mi, ma in zip(times, data_min, data_max):
#			print ssp, t, mi, ma
		data_min = movingaverage_DT(data_min, times,)
		data_max = movingaverage_DT(data_max, times,)
                pyplot.fill_between(times, data_min, data_max, color=ssp_colours[ssp], alpha=0.2)


        pyplot.title('AMOC - 10 year moving average')
	pyplot.ylabel('Sv')
	pyplot.legend()
#	pyplot.show()
        pyplot.savefig('custom_plots/amoc_fig2_noFill.png', dpi=300)
	pyplot.close()
fig2()











