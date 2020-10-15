from folium.plugins import MarkerCluster
# sys is required to use the open function to write on file
import sys
# pandas is needed to read the csv file and to perform some basic operations on dataframes
import pandas as pd
# matplotlib is used to draw graphs
from matplotlib import pyplot
import matplotlib
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
# numpy is for scinetific computations
import numpy as np

import json
import math

from xmeans import *
from loc_dist_fun import *
from scipy import stats
from scipy.special import erfc
from collections import defaultdict
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, fcluster


#from kmeans import *
import imn_extractor
import util
import bisecting_kmeans
from loc_dist_fun import *
import trajectory
import database_io
import tosca
from individual_mobility_network import*
import mobility_distance_functions

from trajectory import *
from geohash_functions import*
from tosca import*
from evaluation import*
import geohash2
import csv
import numpy as np
from database_io import*
import pandas as pd

import matplotlib.pyplot as plt
from evaluation import evalaute_segmentation
from trajectory_segmenter import moving_median, moving_avg, thompson_test
from trajectory_segmenter import segment_trajectories
from trajectory_segmenter import segment_trajectories_random
from trajectory_segmenter import segment_trajectories_user_adaptive

import os


def chauvenet_test(data, point):
    mean = np.mean(data)           # Mean of incoming array y
    stdv = np.std(data)            # Its standard deviation
    N = len(data)                # Lenght of incoming arrays
    criterion = 1.0/(2*N)        # Chauvenet's criterion
    d = abs(point-mean)/stdv     # Distance of a value to mean in stdv's
    d /= 2.0**0.5                # The left and right tail threshold values
    prob = erfc(d)               # Area normal dist.
    filter = prob >= criterion   # The 'accept' filter array with booleans
    return filter

def main():

        myfile=open('geohashp5_roma.txt','r')
        lines=myfile.readlines()
        count=0
        media=list()
        mediana=list()
        stand_dev=list()
        latid=list()
        lons=list()
        numero_punti=list()
        gap=10
        max_lim=3600*48
        min_size=10
        window=3
        thresholds=dict()
        
        with open('romauid5.json', 'r') as fp:
                data = json.load(fp)
        
        for line in lines:
                tempi=list()
                list_points= line.split(':')[1].split(',')#prende la lista e lascia la chiave e poi prende solo il terzo parametro
                geohash=line.split(':')[0].split(' ')[0]
                for l in list_points:
                        #print('l=',l)
                        if ']' in l:
                                time=float(l.replace(']',''))
                                #print('time=',time)
                                tempi.append(time)
                average_tempi=np.mean(tempi)
                median_tempi=np.median(tempi)
                var_tempi=np.std(tempi)
                media.append(average_tempi)
                mediana.append(median_tempi)
                stand_dev.append(var_tempi)
                
                longi,lat=geohash2.decode(geohash)
                latit=float(lat)
                longit=float(longi)
                latid.append(latit)
                lons.append(longit)
                numero_punti.append(len(tempi))
                

                list_uid=data[geohash]
                
                num_uid_unici=len(set(list_uid))
                

                
                if len(tempi)>100 and num_uid_unici>1:
                        local_temporal_thr=math.log(1200)
                        pyplot.hist(tempi,bins=100,range=(0,86400))
                        pyplot.show()
                        pyplot.title('stop time distribution per geohash: '+geohash)
                        pyplot.yscale('log')
                        pyplot.savefig('plot_roma/p5plot_'+geohash)
                        
                        pyplot.cla()
                        count=count+1
                        
                        tempi=[math.log(x) for x in tempi if x>0]
                        time_stop_values = np.arange(math.log(gap), math.log(max_lim + gap),(math.log(max_lim + gap)-math.log(gap))/2000.0 )
                        
                        stop_time_count, _ = np.histogram(tempi, bins=time_stop_values)

                        
                        stop_time_count_ma = moving_avg(stop_time_count[::-1], window) #mi da il contenuto dei bin
                        time_stop_values_ma = moving_avg(time_stop_values[::-1], window) #mi da i bordi dei bin (facendo la media mobile toglie i primi due bin)
                       
                       # tempi=[math.log(x) for x in tempi if x>0] #chauvenet 
                        #tempi.sort()    #vhauvenet
    
                       #for t in tempi:
                       # for t in tempi[int(len(tempi)/2):]:
                        #print(t)int(len()/2):
                        #print(chauvenet_test(tempi,t))
                                
                               # if chauvenet_test(tempi,t)==False:
                                #        local_temporal_thr=t
                                 #       break
                        #thresholds[geohash]=math.exp(local_temporal_thr)
                        
                        for cut in range(len(stop_time_count_ma) - 1, min_size, -1):
                                if thompson_test(stop_time_count_ma[:cut], stop_time_count_ma[cut]):
                                        user_temporal_thr = time_stop_values_ma[cut]
                                        break
    

                        thresholds[geohash]=math.exp(local_temporal_thr)
                  
                        

        with open('data_thompson_roma5.json', 'w') as fp:
                json.dump(thresholds, fp)
                

        
    


        xbins=list(set(latid))
        ybins=list(set(lons))
        xbins.sort()
        ybins.sort()

        
        pyplot.hist2d(latid,lons, weights=numero_punti,norm=LogNorm(), bins=[xbins, ybins] )
        cb=pyplot.colorbar()
        pyplot.title('pseudo stop points distribution (Log Scale)')
        pyplot.ylabel('latitude')
        pyplot.xlabel('longitude')
        pyplot.savefig('Plot2000/hist2d_numeropunti_p6')
        pyplot.cla()
        cb.remove()
        
        pyplot.hist(len(tempi),bins=100,range=(0,400))
        pyplot.show()
        pyplot.title('Number of points distribution per geohash')
        pyplot.savefig('Plot2000/hist1d_npoints')
        pyplot.cla()
       
        
        pyplot.hist2d(latid,lons, weights=media, bins=[xbins, ybins] )
        cb=pyplot.colorbar()
        pyplot.title('Average stop distribution')
        pyplot.ylabel('latitude')
        pyplot.xlabel('longitude')
        pyplot.savefig('Plot2000/hist2d_binp6')
        pyplot.cla()
        cb.remove()
        
        pyplot.hist2d(latid,lons, weights=media, norm=LogNorm(), bins=[xbins, ybins] )
        pyplot.title('Average stop distribution (Log Scale)')
        cb=pyplot.colorbar()
        pyplot.ylabel('latitude')
        pyplot.xlabel('longitude')
        pyplot.savefig('Plot2000/hist2d_log_binp6')
        pyplot.cla()
        cb.remove()
        
        pyplot.hist2d(latid,lons, weights=mediana, bins=[xbins, ybins] )
        cb=pyplot.colorbar()
        pyplot.title('Median stop distribution')
        pyplot.ylabel('latitude')
        pyplot.xlabel('longitude')
        pyplot.savefig('Plot2000/hist2d_binp6_mediana')
        pyplot.cla()
        cb.remove()
        
        pyplot.hist2d(latid,lons, weights=mediana, norm=LogNorm(), bins=[xbins, ybins] )
        pyplot.title('Median stop distribution (Log Scale)')
        pyplot.ylabel('latitude')
        pyplot.xlabel('longitude')
        cb=pyplot.colorbar()
        pyplot.savefig('Plot2000/hist2d_log_binp6_mediana')
        pyplot.cla()
        cb.remove()
                              
        
        with open('only2000uid.json', 'r') as fp:
                data = json.load(fp)
                
        
        latitu=list()
        longitu=list()
        num_utenti=list()
               
        for d in data:
                longi,lat=geohash2.decode(d)
                lat=float(lat)
                longi=float(longi)
                latitu.append(lat)
                longitu.append(longi)
                list_uid=data[d]
                
                num_uid_unici=len(set(list_uid))  #set prende solo gli utenti unici
                num_utenti.append(num_uid_unici)
                
                
        xbins=list(set(latitu))
        ybins=list(set(longitu))
        xbins.sort()
        ybins.sort()

        
        pyplot.hist2d(latitu,longitu, weights=num_utenti,norm=LogNorm(), bins=[xbins, ybins] )
        cb=pyplot.colorbar()
        pyplot.title('user distribution (Log Scale)')
        pyplot.ylabel('latitude')
        pyplot.xlabel('longitude')
        pyplot.savefig('Plot2000/hist2d_numero_utenti_p6')
        pyplot.cla()
        cb.remove()
        
        pyplot.hist(num_utenti,bins=100,range=(0,2000))
        pyplot.show()
        pyplot.title('Users distribution per geohash')
        pyplot.savefig('Plot2000/hist1d_npoints')
        pyplot.cla()

                      
                                
if __name__ == '__main__':
    main()
                
                
                
                
        























