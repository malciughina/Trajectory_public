import numpy as np
import database_io
import os
import csv
import mobility_distance_functions
from tosca import *
from Griglia import *
from individual_mobility_network import *
from evaluation import evalaute_segmentation
from trajectory_segmenter import *


def merge_trajectories(trajectories):
    all_traj = []
    for tid in sorted(trajectories, key=lambda x: int(x)):
        traj = trajectories[tid]
        all_traj.extend(traj.object)
    return all_traj


def get_points_trajfromto_list(trajectories):
    points = dict()
    traj_from_to = dict()
    for traj in trajectories:
        tid = trajectories.index(traj)

        lon_from = float(traj.start_point()[0])
        lat_from = float(traj.start_point()[1])
        time_from = int(traj.start_point()[2])

        lon_to = float(traj.end_point()[0])
        lat_to = float(traj.end_point()[1])
        time_to = int(traj.end_point()[2])

        pid_start_point = len(points)
        points[pid_start_point] = [lon_from, lat_from, time_from, 'f', tid]

        pid_end_point = len(points)
        points[pid_end_point] = [lon_to, lat_to, time_to, 't', tid]

        traj_from_to[tid] = [pid_start_point, pid_end_point]

    return points, traj_from_to
    
def main():
        input_table = 'tak.italy_traj'
        con = database_io.get_connection()
        cur = con.cursor()
        users_list = database_io.extract_users_list('tak.italy_traj', cur)
        cur.close()
        con.close()

        uid = users_list[0]
        print(len(users_list))

        count = 0
        nbr_exp = 2000
        #thresholds = [60, 120, 180, 240]
        thresholds = 60
        
        point=dict()
        thr=dict()
        geo_uid= dict()
        geo_point= dict()
        eval_adaptive = list()

    
        for uid in users_list:
                if uid=='100167':
                        continue


                print(uid, input_table)
                con = database_io.get_connection()
                cur = con.cursor()
                imh = database_io.load_individual_mobility_history(cur, uid, input_table)
                cur.close()
                con.close()


                trajectories = imh['trajectories']
                alltraj = merge_trajectories(trajectories)
                
                if (len(alltraj)<1):
                    continue 

                for mypoint in range(len(alltraj)):
                        p=alltraj[mypoint] #punto di riferimento
                        lat=p[1]
                        longi=p[0]

                        if p[0] in [np.nan, np.inf] or p[1] in [np.nan, np.inf]:
                                continue
                        geo_data=geohash2.encode(p[0],p[1],precision=6)
                        
                        if uid in geo_uid:
                                geo_uid[uid].append(geo_data)
                        else:
                                geo_uid[uid]=[geo_data]
                        


                traj_list_user_ad, user_temporal_thr_user_ad = segment_trajectories_user_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50,
                                                                              max_speed=0.07, gap=60, max_lim=3600 * 48,
                                                                              window=15, smooth_fun=moving_median, min_size=10,
                                                                              return_cut=True)
                avg_nbr_points_user_ad = np.mean([len(t) for t in traj_list_user_ad])

                print('NT %d - ANP %.2f' % (len(traj_list_user_ad), avg_nbr_points_user_ad))
                time_precision, dist_coverage, mobility_f1 = evalaute_segmentation(alltraj, traj_list_user_ad, print_report=True)
                eval_adaptive.append((time_precision, dist_coverage, mobility_f1))

                #points_user_ad, traj_from_to_user_ad = get_points_trajfromto_list(traj_list_user_ad)

                thr[uid]=user_temporal_thr_user_ad
                
                for m in range(len(traj_list_user_ad)):
                        traj=traj_list_user_ad[m].object #.traj perchè prendo l'oggetto traj (lista di punti)
                        p=traj[-1] #prendo l'ultimo punto della traj che è lo stop
                        lat=p[1]
                        longi=p[0]

                        if p[0] in [np.nan, np.inf] or p[1] in [np.nan, np.inf]:
                                continue
                        geo_data=geohash2.encode(p[0],p[1],precision=6)

                        if uid in point:
                                point[uid].append(geo_data)
                        else:
                                point[uid]=[geo_data]
                                
                
        with open('soglie_utenti_it24.json', 'w') as fp: #dizionario in cui per ogni utente ho la soglia user adaptive
                json.dump(thr, fp)
    
        with open('stop_utenti_it24.json', 'w') as fl: #dizionario in cui per ogni utente so le celle in cui si è fermato
                json.dump(point, fl)
                
        with open('celle_utenti_it24.json', 'w') as fd: #dizionario in cui per ogni utente so le celle in cui è passato (poco utile)
                json.dump(geo_uid, fd)
        
        conteggi_totali=list()        
        counts=dict()        
        for uid in point:
                celle=point[uid]
                celle_uniche=set(celle)
                conteggi=list()
                
                for k in celle_uniche:
                        count=celle.count(k) #mi dice quanti stop un utente fa in una cella
                        conteggi.append(count)
                        
                counts[uid]=conteggi #diz contiene la distrib dei conteggi degli stop
                
                conteggi_totali+=conteggi #estendo la lista
                
                
        pyplot.hist(conteggi_totali,bins=100,range=(0,50))
        pyplot.show()
        pyplot.title('conteggi per cella')
        #pyplot.yscale('log')
        pyplot.savefig('conteggi_cella_italyp4')

        pyplot.cla()
        
        quantile=np.quantile(conteggi_totali,0.25)
        percentile=np.percentile(conteggi_totali,25)
        print('quantile',quantile)        
        print('percentile',percentile)                 
                        
                
if __name__ == '__main__':
    main()
    
    

    
    
    
    
    
    
    
    
    
    
