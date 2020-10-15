import numpy as np
import database_io
import os
import csv
import scipy
from scipy import stats
from statistics import mode
import mobility_distance_functions
from tosca import *
from Griglia import *
from individual_mobility_network import *
from evaluation import evalaute_segmentation
from trajectory_segmenter import moving_median, moving_avg
from trajectory_segmenter import segment_trajectories
from trajectory_segmenter import segment_trajectories_random
from trajectory_segmenter import segment_trajectories_user_adaptive
from trajectory_segmenter import segment_trajectories_geohash_adaptive



def main():
#questo file deve essere girato dopo alternative strategy.py in modo da calcolare le mode che serviranno poi per la segmentazione (fatta in experiment.py)
        with open('soglie_utenti_itp4.json', 'r') as fp:
                data_soglie = json.load(fp)
        print('num_utenti',len(data_soglie.keys()))        
        with open('celle_utenti_itp4.json', 'r') as fd:
                data_celle = json.load(fd)
        print('num_utenti',len(data_celle.keys()))        
        with open('stop_utenti_itp4.json', 'r') as fl:
                data_stop= json.load(fl)
        print('num_utenti',len(data_stop.keys()))
        lista_soglie=dict()
        lista_soglie_stop=dict()
        media=dict() 
        new_soglie=dict()
        moda_celle=dict()
        moda_celle_stop=dict()
        
        for uid in data_soglie:
               # if uid=='100147':
                #        continue
             
                soglia=data_soglie[uid] 
                celle=data_celle[uid]
                if uid in data_stop:
                        celle_stop=data_stop[uid]
                else:
                        celle_stop=[]
                for c in celle:
                        if c in lista_soglie:
                                lista_soglie[c].append(soglia) 
                        else: 
                                
                                lista_soglie[c]=[soglia]
                                       
                for s in celle_stop:
                        if s in lista_soglie_stop:
                                lista_soglie_stop[s].append(soglia) 
                        else: 
                        
                                lista_soglie_stop[s]=[soglia]
       
        for c in lista_soglie:
                sum_soglie_celle=lista_soglie[c]
               
                contents,edges=np.histogram(sum_soglie_celle, bins=int(max(sum_soglie_celle)+1), range=(0,int(max(sum_soglie_celle)+1)))
                moda_sum_soglie_celle=edges[np.argmax(contents)]                 
                moda_celle[c]=  moda_sum_soglie_celle              


        for s in lista_soglie_stop:
                sum_soglie_celle_stop=lista_soglie_stop[s]
               
                contents2,edges2=np.histogram(sum_soglie_celle_stop, bins=int(max(sum_soglie_celle_stop)+1), range=(0,int(max(sum_soglie_celle_stop)+1)))
                moda_sum_soglie_celle_stop=edges2[np.argmax(contents2)]                 
                moda_celle_stop[s]=  moda_sum_soglie_celle_stop 


        with open('moda_stop_celle_itp4.json', 'w') as fs:
                json.dump(moda_celle_stop, fs)

        with open('moda_celle_itp4.json', 'w') as fb:
                json.dump(moda_celle, fb)
                
        filename="confronto_soglie_moda_itp4.csv"
        if os.path.isfile(filename):
                os.remove(filename)

        with open(filename, 'a', newline='\n') as file:
                writer = csv.writer(file)
                writer.writerow(["initial_threshold"," uid","moda_soglie"])
                
                
        with open('soglie_celle_itp4.json', 'w') as fr: #per ogni cella mi da tutte le soglie
                json.dump(lista_soglie, fr)
        '''               
        for uid in data_celle:
                soglia=data_soglie[uid] 
                celle=set(data_celle[uid]) #ho tolto set set(=data_celle[uid])
                somma_soglie=list()
                
                for c in celle:
                        soglie=lista_soglie[c]
                        somma_soglie+=soglie
                
                
                avg_somma_soglie=np.mean(somma_soglie) 
                #istogramma con bin dipendenti da max(a)
                contents,edges=np.histogram(somma_soglie, bins=int(max(somma_soglie)+1), range=(0,int(max(somma_soglie)+1)))
#trovo il massimo contenuto e poi il bordo del bin
                moda_somma_soglie=edges[np.argmax(contents)]
                #moda_somma_soglie=mode( somma_soglie )       
                print('moda somma soglie',moda_somma_soglie) 
                print('soglia', soglia)
                print('user',uid)
                
                
                if uid in new_soglie:
                       new_soglie[uid].append(moda_somma_soglie)
                else:
                       new_soglie[uid]=[moda_somma_soglie]  
                 
                with open(filename, 'a', newline='\n') as file:
                        writer = csv.writer(file)
                        writer.writerow([data_soglie[uid], uid,new_soglie[uid]])
                               
        with open('new_soglie_celle_pesate_ukmoda_set.json', 'w') as fy:
                json.dump(new_soglie, fy)
                
                
         '''            

                
                       
if __name__ == '__main__':
    main()
