from folium.plugins import MarkerCluster
# sys is required to use the open function to write on file
import sys
# pandas is needed to read the csv file and to perform some basic operations on dataframes
import pandas as pd
# matplotlib is used to draw graphs
from matplotlib import pyplot
import matplotlib
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
from evaluation import evalaute_segmentation
from trajectory_segmenter import moving_median, moving_avg
from trajectory_segmenter import segment_trajectories
from trajectory_segmenter import segment_trajectories_random
from trajectory_segmenter import segment_trajectories_user_adaptive
from trajectory_segmenter import segment_trajectories_geohash_adaptive
import os


def get_list_traj(cursor, stop, v_id):
    cursor.execute("SELECT ST_AsGeoJSON(traj) as trajcoord FROM tak.vodafone_zel1_traj_" + stop +
                   "min WHERE vehicle = '" + v_id + "'")
    traj_list = []
    for t in cursor:
        y = json.loads(t[0])
        c = swap_xy(y["coordinates"])
        traj_list.append(c)
    return traj_list



def merge_trajectories(trajectories):
    all_traj = list()
    for tid in sorted(trajectories, key=lambda x: int(x)):
        traj = trajectories[tid]
        all_traj.extend(traj.object)
    return all_traj




def load_individual_mobility_history(con, uid, input_table, min_length=0, min_duration=0):

    query = """SELECT tid, ST_AsGeoJSON(traj) AS object, uid, length, duration, start_time, end_time
        FROM %s
        WHERE uid = '%s'""" % (input_table, uid)
    cur=con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    trajectories = dict()

    for r in rows:
        # trajectories[str(r[0])] = Trajectory(id=str(r[0]), object=json.loads(r[1])['coordinates'], vehicle=uid)
        traj = [[p[0], p[1], p[2] * 1000] for p in json.loads(r[1])['coordinates']]
        traj = Trajectory(id=str(r[0]), object=traj, vehicle=uid, length=float(r[3]), duration=float(r[4]),
                          start_time=r[5], end_time=r[6])

        if traj.length() > min_length and traj.duration() > min_duration:
            trajectories[str(r[0])] = traj
        # if len(trajectories) >= 100:
        #     break

    imh = {'uid': uid, 'trajectories': trajectories}

    return imh



def get_points_trajfromto(imh):

        trajectories = imh['trajectories']

        points = dict()
        traj_from_to = dict()

        for tid, traj in trajectories.items():

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




def traj_dict(df_v):
    trajectories = dict()
    for _, row in df_v.iterrows():
        tid = row["tid"]
        y = json.loads(row["trajcoord"])
        c = swap_xy(y["coordinates"])
        trajectories[tid] = c
    return trajectories


def get_points_trajfromto(imh):

    trajectories = imh['trajectories']

    points = dict()
    traj_from_to = dict()
    traj_list=list()

    for tid, traj in trajectories.items():

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
    


    
        return points,traj_from_to



def decodeTraj(jsondict):
     return Trajectory(jsondict['id'],jsondict['object'],jsondict['vehicle'],jsondict['_length'],jsondict['_duration'],jsondict['_start_time'],jsondict['_end_time'])


def stop_time(traj_list_classic):
    stop_points=[]
    #print(alltraj[0])
    print(traj_list_classic[0])
    
    for i in range(len(traj_list_classic)-1): #scorro fino alla penulultima
        mytraj=traj_list_classic[i]
        uid=mytraj.id
        next_traj=traj_list_classic[i+1]
        point=mytraj.object
        lastpoint=point[-1]
        next_point=next_traj.object[0] #primo punto della successiva

        time_range=next_point[2]-lastpoint[2]
        lat=lastpoint[1]
        long=lastpoint[0]
        stop_points.append([uid,lat,long,time_range])
    
    return stop_points

def stop_time_bis(points,uid, distance_thr=50):
    stop_points=[]
    #print(alltraj[0])
    #print(points[0])
    
    
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

        input_table = 'tak.uk_traj'
        con = database_io.get_connection()
        cur = con.cursor()
        users_list = database_io.extract_users_list('tak.uk_traj', cur)
        cur.close()
        con.close()
        count=0

        sosta=[]  
        con=database_io.get_connection()
        cur = con.cursor()   
        for uid in users_list:
                #if uid=='100221':
                 #       continue

                print(uid, input_table)
                imh = load_individual_mobility_history(con, uid, input_table)

                trajectories = imh['trajectories']
                alltraj = merge_trajectories(trajectories)
                print('alltraj')
                provv=stop_time_bis(alltraj,uid,50)
                sosta.extend(provv)
                tempi_plt=[p[2] for p in provv]

            #    pyplot.hist(tempi_plt,bins=100,range=(0,86400))
             #   pyplot.show()
              #  pyplot.yscale('log')
               # pyplot.title('stop time distribution per utente: '+uid)
                #pyplot.savefig('user50/plot_'+uid)
                
                #pyplot.cla()
                #count=count+1

        cur.close()
        con.close()

        geo_point= dict() #creato un dizionario che ha come chiave geohash e come valore la lista dei punti di stop in quella cella e l'identificativo utente
        geo_uid= dict()
        for p in list(sosta):
                if p[0] in [np.nan, np.inf] or p[1] in [np.nan, np.inf]:
                        continue
                key=geohash2.encode(p[0],p[1],precision=6)
                if key in geo_point:
                        geo_point[key].append(p[0:3])
                        geo_uid[key].append(p[3])
                else:
                        geo_point[key]=[p[0:3]]
                        geo_uid[key]=[p[3]]
                        
        myfile=open('geohashp6_londra.txt','w')
        
                             
        for g in geo_point:
                 #line=json.dumps(g.__dict__)
                 line = g+ " : " + str(geo_point[g])
                 myfile.write(line+'\n')
        
        myfile.close()
        
        with open('londrauid.json', 'w') as fp:
                json.dump(geo_uid, fp)
        


if __name__ == '__main__':
    main()
