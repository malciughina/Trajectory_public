import database_io
from mobility_distance_functions import *
from trajectory_segmenter import moving_median, moving_avg, thompson_test

import geohash2
import time
import numpy as np
import json
import math

def merge_trajectories(trajectories):
    all_traj = []
    for tid in sorted(trajectories, key=lambda x: int(x)):
        traj = trajectories[tid]
        all_traj.extend(traj.object)
    return all_traj


def stop_time_bis(points,uid, distance_thr=50):
    stop_points=[]

    for p in range(len(points)-1):
        p_index=0
        if p<p_index:
                continue
                
        mypoint=points[p] #punto di riferimento
        for q in range(p+1,len(points)):
                nextpoint=points[q]
                distanza = spherical_distance(mypoint, nextpoint)
                if distanza<distance_thr:
                        continue
                        
                time_range=nextpoint[2]-mypoint[2]

                lat=mypoint[1]
                longi=mypoint[0]

                stop_points.append([lat,longi,time_range,uid])
                p_index=q
                break

    return stop_points


def main():
    
        start_time=time.time()

        input_table = 'tak.italy_traj'
        con = database_io.get_connection()
        cur = con.cursor()
        users_list = database_io.extract_users_list('tak.italy_traj', cur)
        cur.close()
        con.close()
        count=0
        
        #users_list=["197188"]

        sosta=[]  
        con=database_io.get_connection()
        cur = con.cursor()   
        
        counter=0
        
        for uid in users_list:

                print(uid, input_table)
                imh = database_io.load_individual_mobility_history(cur, uid, input_table)

                trajectories = imh['trajectories']
                alltraj = merge_trajectories(trajectories)
                print('alltraj')
                provv=stop_time_bis(alltraj,uid,50./1000)
                sosta.extend(provv)
                tempi_plt=[p[2] for p in provv]                
                print ("time elapsed--", time.time()-start_time, "#user", counter)
                counter=counter+1
                

        cur.close()
        con.close()
        
        print ("geohash encoding")

        geo_point= dict() #creato un dizionario che ha come chiave geohash e come valore la lista dei punti di stop in quella cella e l'identificativo utente
        geo_uid= dict()
        for p in list(sosta):
                if p[0] in [np.nan, np.inf] or p[1] in [np.nan, np.inf]:
                        continue
                key=geohash2.encode(p[0],p[1],precision=4)
                if key in geo_point:
                        geo_point[key].append(p[0:3])
                        geo_uid[key].append(p[3])
                else:
                        geo_point[key]=[p[0:3]]
                        geo_uid[key]=[p[3]]
                        
        print ("done encoding")
        
        #make geohash dep threshold
        thresholds=dict()
        thresholds_quantile=dict()
        
        for geohash in geo_point:
                list_uid=geo_uid[geohash]                
                num_uid_unici=len(set(list_uid))
                tempi=[p[2] for p in geo_point[geohash] ]
                
                if num_uid_unici<=1: continue
                if len(tempi)<100: continue                                        
                                        
    
                local_temporal_thr_q=-99 #default - changed only if ch accepts another one
                local_temporal_thr=-99 #default - changed only if thompson_test accepts another one
                
                #thompson_test stuff (log scale etc)
                
                gap=60
                max_lim=3600*48
                window=3
                min_size=10
                
                #tempilog=[math.log(x) for x in tempi if x>0]
                
                #time_stop_values = np.arange(math.log(gap), math.log(max_lim + gap),(math.log(max_lim + gap)-math.log(gap))/2000.0 ) 
                time_stop_values = np.arange(4*gap,max_lim+2*gap,gap ) 
                stop_time_count, _ = np.histogram(tempi, bins=time_stop_values)
                        
                stop_time_count_ma = moving_avg(stop_time_count[::-1], window) #mi da il contenuto dei bin
                time_stop_values_ma = moving_avg(time_stop_values[::-1], window) #mi da i bordi dei bin (facendo la media mobile toglie i primi due bin)     
                
                #print(time_stop_values_ma)                
                #print ("thomson test",range(len(stop_time_count_ma) - 1, min_size, -1) )
                for cut in range(len(stop_time_count_ma) - 1, min_size, -1):
                        if thompson_test(stop_time_count_ma[:cut+1], stop_time_count_ma[cut]):
                                local_temporal_thr = time_stop_values_ma[cut]
                                break
                
                if (local_temporal_thr>0):
                    thresholds[geohash]=local_temporal_thr#math.exp(local_temporal_thr)
                else:
                    thresholds[geohash]=float(time_stop_values[1])
                #quantile stuff
                
                quantile_high=np.quantile(tempi, 0.90)
                local_temporal_thr_q=quantile_high
                    
                if (local_temporal_thr_q>0):
                    thresholds_quantile[geohash]=local_temporal_thr_q
        
              
        ##with open('geohashp5_uk_bon.json', 'w') as fp:
                ##json.dump(geo_uid, fp)
        
        ##with open('ukuid5_bon.json', 'w') as fp:
                ##json.dump(geo_uid, fp)         
        
        print ("done making threshold with thomson")
        
        print ("thomson",thresholds)
        print ("quantiles",thresholds_quantile)
                
        with open('it_thresholds4_bon.json', 'w') as fp:
                json.dump(thresholds, fp)
        
        with open('it_qthresholds4_bon.json', 'w') as fp:
                json.dump(thresholds_quantile, fp)


if __name__ == '__main__':
    main()
