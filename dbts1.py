import math
import os
import datetime
import numpy as np
import database_io
import pandas as pd
import time
from sklearn.cluster import DBSCAN, OPTICS
from dbts2 import alltraj
from experiment import*
import matplotlib.pyplot as plt
from evaluation import*

from trajectory import Trajectory

def spherical_distance(a, b):
    lat1 = a[1]
    lon1 = a[0]
    lat2 = b[1]
    lon2 = b[0]
    R = 6371000
    rlon1 = lon1 * math.pi / 180.0
    rlon2 = lon2 * math.pi / 180.0
    rlat1 = lat1 * math.pi / 180.0
    rlat2 = lat2 * math.pi / 180.0
    dlon = (rlon1 - rlon2) / 2.0
    dlat = (rlat1 - rlat2) / 2.0
    lat12 = (rlat1 + rlat2) / 2.0
    sindlat = math.sin(dlat)
    sindlon = math.sin(dlon)
    cosdlon = math.cos(dlon)
    coslat12 = math.cos(lat12)
    f = sindlat * sindlat * cosdlon * cosdlon + sindlon * sindlon * coslat12 * coslat12
    f = math.sqrt(f)
    f = math.asin(f) * 2.0 # the angle between the points
    f *= R
    return f
    
def evaluate(alltraj, traj_list):
    nbr_traj = len(traj_list)
    nbr_points_list = list()
    length_list = list()
    duration_list = list()
    sampling_rate_list = list()
    for t in traj_list:
        nbr_points_list.append(len(t))
        length_list.append(t.length())
        duration_list.append(t.duration())
        sampling_rate_list.extend([t.object[i+1][2] - t.object[i][2] for i in range(0, len(t)-1)])

    avg_nbr_points = np.mean(nbr_points_list)
    avg_length = np.mean(length_list)
    avg_duration = np.mean(duration_list)
    avg_sampling_rate = np.mean(sampling_rate_list)
    std_sampling_rate = np.std(sampling_rate_list)
    med_sampling_rate = np.median(sampling_rate_list)

    time_precision, dist_coverage, mobility_f1 = evalaute_segmentation(alltraj, traj_list, print_report=False)
    print(" eval segm done")
    points, traj_from_to_ = get_points_trajfromto_list(traj_list)
    print(" eval get_points_trajfromto_list done")
    loc = locations_detection(points, min_dist=50.0, nrun=1)
    #loc=None
    print(" eval locations_detection done")
    #print('loc',loc)

    res = [nbr_traj, avg_nbr_points, avg_length, avg_duration,
           avg_sampling_rate, std_sampling_rate, med_sampling_rate,
           time_precision, dist_coverage, mobility_f1]
    print('res',res)
    return res

	
	
class DBTS:
    
    def __init__(self, min_pts=5, eps=50, alg='optics', metric='spatial', q=210, k=2):
        
        self.min_pts = min_pts
        self.eps = eps
        self.alg = alg
        self.metric = metric
        self.q = q
        self.k = k
        
        if self.metric == 'spatial':
            self.metric = spherical_distance
        
        if self.alg == 'dbscan':
            self.clus = DBSCAN(eps=self.eps, min_samples=self.min_pts, metric=self.metric)
        else:
            self.clus = OPTICS(eps=self.eps, min_samples=self.min_pts, metric=spherical_distance)
        
    
    def transform(self, X):
        
        k=self.k 
        # Step 1: run desnity-based clustering
        self.clus.fit(X[:,[0,1]])
        labels = self.clus.labels_
        #print('A', np.unique(labels, return_counts=True))
        
        
        # Step 2: separate clusters with respect to time
        cluster_labels = np.unique(labels)
        
        for cid in cluster_labels:
            if cid == -1:
                continue

            Xi = X[np.where(labels == cid)[0]]
            new_labels_i = list()
            new_cid = max(labels)
            new_cid += 1
            new_labels_i.append(new_cid)
            for i in range(len(Xi)-1):
                t1 = Xi[i][2]
                t2 = Xi[i+1][2]
                delta_t = t2 - t1
                if delta_t <= self.q:
                    new_labels_i.append(new_cid)
                else:
                    new_cid += 1
                    new_labels_i.append(new_cid)

            labels[np.where(labels == cid)[0]] = new_labels_i
        
        #print('B', np.unique(labels, return_counts=True))
        
        # Step 3: turn to noise points 
        cluster_labels = np.unique(labels)
        new_labels = -np.ones(len(labels))

        for cid in cluster_labels:
            idx_same_cluster = np.where(labels == cid)[0] 
            if cid != -1 and len(idx_same_cluster) > k:
                new_labels_cluster = (max(new_labels)+1) * np.ones(len(idx_same_cluster))
                new_labels[idx_same_cluster] = new_labels_cluster
        
        #print('C', np.unique(new_labels, return_counts=True))
        
        # Step 4: split data into trajectories according to labels
        trajectories = list()
        traj = list()
        last_l = -1
        # last_p = None
        for i in range(len(X)):
            p = X[i]
            l = new_labels[i]

            if l == -1:
                #if last_l != -1 and last_p is not None:
                #    traj.append((last_p, last_l))
                # traj.append((p, l))
                traj.append(p)

            elif l != -1 and last_l == -1:
                #traj.append((p, l))
                traj.append(p)
                trajectories.append(traj)
                traj = list()

            last_l = l
            last_p = p
            
        return trajectories
		
	
def main():

        print("extracting users list from db")

        con = database_io.get_connection()
        cur = con.cursor()
        users_list = database_io.extract_users_list('tak.italy_traj', cur)
        #users_list = ['100966']
             
            #               '100022',
            #               '100026',
            #               '10008',
            #               '100086',
            #               '100087',
            #               '100088',
            #               '100090',
            #               '100100',
            #               '100117']
            
            
        cur.close()
        con.close()

        print("done with users list from db")

        con = database_io.get_connection()
        cur = con.cursor()
        input_table='tak.italy_traj'
        
        
        filename = 'Roma_cluster_optics.csv'
        f1_average=list()
        
        header = ['input_table', 'uid', 'nbr_points', 'avg_sampling_rate', 'std_sampling_rate', 'med_sampling_rate',
               'nbr_traj', 'avg_nbr_points', 'avg_length', 'avg_duration', 'time_precision', 'dist_coverage', 'mobility_f1']
        

        processed_users = list()
        if os.path.isfile(filename):
        #os.remove(filename)
                df = pd.read_csv(filename)
                processed_users = list(df['uid'])
                fileout = open(filename, 'a')
                
        else:
                fileout = open(filename, 'w')
                fileout.write('%s\n' % (','.join(header)))
                fileout.flush()
                print('len(header',len(header))
                print('%s\n' % (','.join(header)))
                
                
        for k in range(2,3):
                results = list()
                f1=list()

                for uid in users_list:
                        imh = database_io.load_individual_mobility_history(cur, uid, input_table)
                        trajectories = imh['trajectories']
                        alltraj = merge_trajectories(trajectories)
                        nbr_points = len(alltraj)
                        
                        dbts = DBTS(min_pts=5, eps=50, alg='optics', metric='spatial', q=210, k=k) #alg='optics'dbscan
                        trajectories = dbts.transform(np.array(alltraj))
                        if (len(trajectories)<1): 
                                continue
                        print(len(trajectories))
                        print(trajectories[0])
                        print('alltraj',alltraj[0])
                        print(dbts.clus.labels_)

                        traj_list=[]
                        tid=0
                       
                        sampling_rate_list = [alltraj[i+1][2] - alltraj[i][2] for i in range(0, len(alltraj)-1)]
                        avg_sampling_rate = np.mean(sampling_rate_list)
                        std_sampling_rate = np.std(sampling_rate_list)
                        med_sampling_rate = np.median(sampling_rate_list)
                        
                        base_res = [input_table, uid, nbr_points]
                        
                        for t in trajectories:
                                length=len(t)
                                start_time = t[0][2]
                                end_time = t[-1][2]
                                duration = end_time - start_time
                                traj_list.append(Trajectory(id=tid, object=t, vehicle=uid, length=length, duration=duration,
                                                            start_time=start_time, end_time=end_time))

                                tid=tid+1
                                
                        res_cluster=evaluate(alltraj,traj_list)
                        print('res_cluster',res_cluster)
                        fileout.write('%s\n' % (','.join([str(r) for r in base_res + res_cluster])))
                        fileout.flush()
                        print('base',len(base_res))
                        print('len(res_cluster)',len(res_cluster))
                        print('%s\n' % (','.join([str(r) for r in base_res +res_cluster])))
                        
                        results.append(base_res  + res_cluster)
                        f1.append(res_cluster[9])
                f1_average.append(np.mean(f1))    
         

                      
       
                
        #labels1= [2,3,4,5,6]  
        #x=[0,1,2,3,4]                       
        #plt.plot(f1_average)
        #plt.xticks(x,labels1, rotation='vertical')
        #plt.savefig('mobilityf1_cluster_optics')
        
        #plt.cla()
        #hist, bins = np.histogram(dbts.clus.labels_,bins=range(-1, len(set(dbts.clus.labels_)) + 1))
        #plt.plot(hist)
        #plt.savefig('cluster_prova')
        #print('labels', dict(zip(bins, hist)))
        fileout.close()
        cur.close()
        con.close()

        print("final connection close up")


if __name__ == "__main__":
    main()
