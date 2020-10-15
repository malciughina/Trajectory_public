import numpy as np
import database_io
import os
import csv
import scipy
import json
from scipy import stats
from statistics import mode
from matplotlib import pyplot
from scipy.stats import gaussian_kde
import matplotlib
import mobility_distance_functions
from tosca import *
#from Griglia import *
import seaborn as sns
from individual_mobility_network import *
#from evaluation import evalaute_segmentation
#from trajectory_segmenter import moving_median, moving_avg
#from trajectory_segmenter import segment_trajectories
#from trajectory_segmenter import segment_trajectories_random
#from trajectory_segmenter import segment_trajectories_user_adaptive
#from trajectory_segmenter import segment_trajectories_geohash_adaptive



def scatter_plot(uid):

        with open('moda_stop_celle_uk24.json', 'r') as fb:
              data_celle=json.load(fb)
        #print('num_celle',len(data_celle.keys()))
        with open('stop_utenti_uk24.json', 'r') as fl:
              data_stop= json.load(fl)
        #print('num_utenti',len(data_stop.keys()))          
        with open('soglie_utenti_uk24.json', 'r') as fp:
              data_soglie = json.load(fp)
        print('num_utenti',len(data_soglie.keys()))
    
        if uid not in data_soglie :
                print("USER NOT FOUND, RETURN EMPTY")
                return 

     
       
        value_not_mod=dict()
        moda_da_usare=dict()  
        user_temporal_thr= data_soglie[uid] 
        if uid in data_stop:
             
            celle=data_stop[uid]
            celle_uniche=set(celle)
            
                     
            for k in celle_uniche:
                count=celle.count(k)
                
                if (count<5):
                        moda_da_usare[k]= data_celle[k]
                else:
                        value_not_mod[k]= user_temporal_thr
                        
        y= list(moda_da_usare.values() )#vettore delle celle con le soglie modificate
        x= [user_temporal_thr for Y in y]
        y2= list(value_not_mod.values()) #vettore delle celle con le soglie non modificate
        x2= list(value_not_mod.values() )
        
       # pyplot.plot(x,y)
        pyplot.scatter(x+x2,y+y2)
        pyplot.savefig('prova_scatter')
        pyplot.cla()
        
def scatter_plot_geo(user_list):

        with open('ukthresholds6_bon.json', 'r') as fb:
                soglie_geohash=json.load(fb)           
        
    
        with open('soglie_utenti_uk24.json', 'r') as fp:
                data_soglie = json.load(fp)
        print('num_utenti',len(data_soglie.keys()))
        xplot=list()
        yplot=list()

        
        for uid in user_list:        
                    
                if uid not in data_soglie :
                        print("USER NOT FOUND, RETURN EMPTY")
                        continue

                valore_da_usare=dict()  
                
                user_temporal_thr= data_soglie[uid] 
                for geo in soglie_geohash:
                    
                    valore_da_usare[geo]= soglie_geohash[geo]
        
                y= list(valore_da_usare.values() )#vettore delle celle con le soglie modificate
                x= [user_temporal_thr for Y in y]

                xplot.extend(x)
                yplot.extend(y)

        
        xplot=xplot+np.random.normal(0,60,len(xplot))        
        
       
        yplot=yplot+np.random.normal(0,60,len(yplot)) 
               
        # Calculate the point density
        xy = np.vstack([xplot,yplot])
        z = gaussian_kde(xy)(xy)
        
       # pyplot.plot(x,y)
        pyplot.scatter( xplot,yplot,c=z)
        pyplot.title('Rome')
        pyplot.xlabel('ATS th per cella [s]')
        pyplot.ylabel('ACTS_{LOC} th per cella [s]')
        pyplot.savefig('scatter_ROMAgeop6')
        pyplot.cla() 
     
        
        
        
        
        
        
        
        
        
        
        
def scatter_plot_userlist(user_list):

        with open('moda_stop_celle_ukp7.json', 'r') as fb:
              data_celle=json.load(fb)
        
        with open('stop_utenti_ukp7.json', 'r') as fl:
              data_stop= json.load(fl)
               
        with open('soglie_utenti_ukp7.json', 'r') as fp:
              data_soglie = json.load(fp)
        print('num_utenti',len(data_soglie.keys()))

        xplot=list()
        yplot=list()
        
        xplot2=list()
        yplot2=list()
        for uid in user_list:
        
                    
                if uid not in data_soglie :
                        print("USER NOT FOUND, RETURN EMPTY")
                        continue

                value_not_mod=dict()
                moda_da_usare=dict()  
                user_temporal_thr= data_soglie[uid] 
                if uid in data_stop:
                     
                    celle=data_stop[uid]
                    celle_uniche=set(celle)
                    
                             
                    for k in celle_uniche:
                        count=celle.count(k)
                        
                        if (count<5):
                                moda_da_usare[k]= data_celle[k]
                        else:
                                value_not_mod[k]= user_temporal_thr
                                
                y= list(moda_da_usare.values() )#vettore delle celle con le soglie modificate
                x= [user_temporal_thr for Y in y]
                y2= list(value_not_mod.values()) #vettore delle celle con le soglie non modificate
                x2= list(value_not_mod.values() )
                xplot.extend(x)
                xplot.extend(x2)
                yplot.extend(y)
                yplot.extend(y2)
                        
                xplot2.extend(x)
                yplot2.extend(y)
        
        #xplot=np.log(xplot)
        xplot=xplot+np.random.normal(0,30,len(xplot))
        
        
        #yplot=np.log(yplot)
        yplot=yplot+np.random.normal(0,30,len(yplot))        
# Calculate the point density
        xy = np.vstack([xplot,yplot])
        z = gaussian_kde(xy)(xy)
        z=z/max(z)
       # pyplot.plot(x,y)
        pyplot.scatter( xplot,yplot,c=z)
        cb=pyplot.colorbar()
        pyplot.title('London (p=7)')
        pyplot.xscale('log') 
        pyplot.yscale('log') 
        pyplot.xlabel('ATS th per cella [sec]')
        pyplot.ylabel('ACTS_${WOTC}$ th per cella [sec]')
        pyplot.savefig('scatter_LONDRAp5log30')
        pyplot.cla() 
             
                        
def main():
        
        with open('soglie_utenti_ukp7.json', 'r') as fp:
              data_soglie = json.load(fp)
        print('num_utenti',len(data_soglie.keys()))
        
        users_list=data_soglie.keys()

        
        
        scatter_plot_userlist(users_list)
      #  scatter_plot_geo(users_list)  
                

                
                       
if __name__ == '__main__':
    main()
                                
                        
                        
