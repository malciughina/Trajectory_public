import math
import numpy as np
import json
from scipy import stats

from trajectory import Trajectory
import math

from xmeans import XMeans
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


def thompson_test(data, point, alpha=0.05):
    sd = np.std(data)
    mean = np.mean(data)
    delta = abs(point - mean)

    t_a2 = stats.t.ppf(1-(alpha/2.), len(data)-2)
    tau = (t_a2 * (len(data)-1)) / (math.sqrt(len(data)) * math.sqrt(len(data)-2 + t_a2**2))

    return delta > tau * 2*sd




def segment_trajectories(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07):
    # temporal_thr = 120 # seconds
    # spatial_thr = 50 # meters
    # max_speed = 0.07 # km/s
    spatial_thr = spatial_thr / 1000

    traj_list = list()

    tid = 0
    traj = list()
    is_a_new_traj = True
    p = None
    length = 0.0
    ref_p = None  # for stop detection
    first_iteration = True

    p_index = 0
    next_p_index = 0
    ref_p_index = 0

    for i in range(0, len(alltraj)):

        next_p = alltraj[i]
        next_p_index = i

        if first_iteration:  # first iteration
            p = next_p
            p_index = next_p_index
            ref_p = p  # for stop detection
            traj = [p]
            length = 0.0
            is_a_new_traj = True
            first_iteration = False
        else:                 # all the others
            spatial_dist = spherical_distance(p, next_p)
            temporal_dist = next_p[2] - p[2]

            ref_distance = spherical_distance(ref_p, next_p)  # for stop detection
            ref_time_diff = next_p[2] - ref_p[2]  # for stop detection

            # Ignore extreme jump (with speed > 250km/h = 0.07km/s)
            if ref_distance > max_speed * ref_time_diff:
                continue

            if temporal_dist > temporal_thr or (ref_time_diff > temporal_thr and ref_distance < spatial_thr):
                # ended trajectory (includes case with long time gap)
                if len(traj) > 1 and not is_a_new_traj:
                    start_time = traj[0][2]
                    end_time = traj[-1][2]
                    duration = end_time - start_time
                    traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid,
                                                length=length, duration=duration,
                                                start_time=start_time, end_time=end_time))

                # Create a new trajectory
                traj = [p[:2] + [next_p[2]]]  # 1st fake point with last position previous traj and new timestamp
                p = next_p
                p_index = next_p_index
                ref_p = p  # for stop detection
                ref_p_index = p_index
                traj.append(p)
                length = 0.0
                tid += 1
                is_a_new_traj = True
            else:
                if is_a_new_traj and len(traj) > 1:
                    traj[1] = [traj[1][0], traj[1][1], traj[0][2] +int((next_p[2] - traj[0][2])/2)]
                is_a_new_traj = False

                p = next_p
                p_index = next_p_index
                if ref_distance > spatial_thr:
                    ref_p = p  # for stop detection
                    ref_p_index = p_index
                traj.append(p)
                length += spatial_dist

    if len(traj) > 1 and not is_a_new_traj:
        start_time = traj[0][2]
        end_time = traj[-1][2]
        duration = end_time - start_time
        traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid, length=length, duration=duration,
                                    start_time=start_time, end_time=end_time))

    return traj_list

def segment_trajectories2(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07):   #questa è quella originale, l'altra è copiata dal file pcham
    # temporal_thr = 120 # seconds
    # spatial_thr = 50 # meters
    # max_speed = 0.07 # km/s
    spatial_thr = spatial_thr / 1000

    traj_list = list()

    tid = 0
    traj = list()
    is_a_new_traj = True
    p = None
    length = 0.0
    ref_p = None  # for stop detection
    first_iteration = True

    p_index = 0
    next_p_index = 0
    ref_p_index = 0

    for i in range(0, len(alltraj)):

        next_p = alltraj[i]
        next_p_index = i

        if first_iteration:  # first iteration
            p = next_p
            p_index = next_p_index
            ref_p = p  # for stop detection
            traj = [p]
            length = 0.0
            is_a_new_traj = True
            first_iteration = False
        else:                 # all the others
            spatial_dist = spherical_distance(p, next_p)
            temporal_dist = next_p[2] - p[2]

            ref_distance = spherical_distance(ref_p, next_p)  # for stop detection
            ref_time_diff = next_p[2] - ref_p[2]  # for stop detection

            # Ignore extreme jump (with speed > 250km/h = 0.07km/s)
            if ref_distance > max_speed * ref_time_diff:
                continue

            if temporal_dist > temporal_thr or (ref_time_diff > temporal_thr and ref_distance < spatial_thr):
                # ended trajectory (includes case with long time gap)
                if len(traj) > 1 and not is_a_new_traj:
                    start_time = traj[0][2]
                    end_time = traj[-1][2]
                    duration = end_time - start_time
                    traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid,
                                                length=length, duration=duration,
                                                start_time=start_time, end_time=end_time))

                # Create a new trajectory
                traj = [p[:2] + [next_p[2]]]  # 1st fake point with last position previous traj and new timestamp
                p = next_p
                p_index = next_p_index
                ref_p = p  # for stop detection
                ref_p_index = p_index
                traj.append(p)
                length = 0.0
                tid += 1
                is_a_new_traj = True
            else:
                if is_a_new_traj and len(traj) > 1:
                    traj[1] = [traj[1][0], traj[1][1], traj[0][2] +int((next_p[2] - traj[0][2])/2)]
                is_a_new_traj = False

                p = next_p
                p_index = next_p_index
                if ref_distance > spatial_thr:
                    ref_p = p  # for stop detection
                    ref_p_index = p_index
                traj.append(p)
                length += spatial_dist

    if len(traj) > 1 and not is_a_new_traj:
        start_time = traj[0][2]
        end_time = traj[-1][2]
        duration = end_time - start_time
        traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid, length=length, duration=duration,
                                    start_time=start_time, end_time=end_time))

    return traj_list
    

    
    
    


def segment_trajectories_random(alltraj, uid, nbr_traj_min=None, nbr_traj_max=None, nbr_traj=None):
    nbr_traj_min = 2 if nbr_traj_min is None else nbr_traj_min
    nbr_traj_max = int(len(alltraj) / 2) if nbr_traj_max is None else nbr_traj_max
    print('len(alltraj)',len(alltraj))
    print('nbr_traj_max',nbr_traj_max)
    print('nbr_traj_min',nbr_traj_min)
    nbr_traj = np.random.randint(nbr_traj_min, nbr_traj_max + 1) if nbr_traj is None else nbr_traj
    new_traj_marker = int(len(alltraj) / nbr_traj)

    traj_list = list()

    tid = 0
    traj = list()
    is_a_new_traj = True
    p = None
    first_iteration = True
    length = 0.0

    for i in range(0, len(alltraj)):

        next_p = alltraj[i]

        if first_iteration:  # first iteration
            p = next_p
            traj = [p]
            length = 0.0
            is_a_new_traj = True
            first_iteration = False
        else:  # all the others
            spatial_dist = spherical_distance(p, next_p)
            if new_traj_marker > 0 and i % new_traj_marker == 0:
                if len(traj) > 1 and not is_a_new_traj:
                    start_time = traj[0][2]
                    end_time = traj[-1][2]
                    duration = end_time - start_time
                    traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid,
                                                length=length, duration=duration,
                                                start_time=start_time, end_time=end_time))

                # Create a new trajectory
                p = next_p
                traj = [p]
                length = 0.0
                tid += 1
                is_a_new_traj = True
            else:
                is_a_new_traj = False
                p = next_p
                traj.append(p)
                length += spatial_dist

    if len(traj) > 1 and not is_a_new_traj:
        start_time = traj[0][2]
        end_time = traj[-1][2]
        duration = end_time - start_time
        traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid, length=length, duration=duration,
                                    start_time=start_time, end_time=end_time))

    return traj_list


def segment_trajectories_random2(alltraj, uid, nbr_traj):
    new_traj_marker = int(len(alltraj) / nbr_traj)

    traj_list = list()

    tid = 0
    traj = list()
    is_a_new_traj = True
    p = None
    first_iteration = True
    length = 0.0

    for i in range(0, len(alltraj)):

        next_p = alltraj[i]

        if first_iteration:  # first iteration
            p = next_p
            traj = [p]
            length = 0.0
            is_a_new_traj = True
            first_iteration = False
        else:  # all the others
            spatial_dist = spherical_distance(p, next_p)
            if new_traj_marker > 0 and i % new_traj_marker == 0:
                if len(traj) > 1 and not is_a_new_traj:
                    start_time = traj[0][2]
                    end_time = traj[-1][2]
                    duration = end_time - start_time
                    traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid,
                                                length=length, duration=duration,
                                                start_time=start_time, end_time=end_time))

                # Create a new trajectory
                p = next_p
                traj = [p]
                length = 0.0
                tid += 1
                is_a_new_traj = True
            else:
                is_a_new_traj = False
                p = next_p
                traj.append(p)
                length += spatial_dist

    if len(traj) > 1 and not is_a_new_traj:
        start_time = traj[0][2]
        end_time = traj[-1][2]
        duration = end_time - start_time
        traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid, length=length, duration=duration,
                                    start_time=start_time, end_time=end_time))

    return traj_list



def get_stop_times(traj_list):
    stop_time_list = list()
    for i in range(1, len(traj_list)):
        arrival_time = traj_list[i-1].end_time()
        leaving_time = traj_list[i].start_time()
        stop_time_list.append(leaving_time - arrival_time)
    return stop_time_list


def moving_avg(a, w=3):  #w=3 significa che fa la media a tre a tre
    ma = list()
    for i in range(0, len(a) - w):
        m = np.mean(a[i:i+w])
        ma.append(m)
    return ma


def moving_median(a, w=3): 
    ma = list()
    for i in range(0, len(a) - w):
        m = np.median(a[i:i+w])
        ma.append(m)
    return ma


def segment_trajectories_user_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07,
                                       gap=60, max_lim=3600*48, window=3, smooth_fun=moving_avg, min_size=10,
                                       return_cut=False):
    traj_list = segment_trajectories(alltraj, uid, temporal_thr, spatial_thr, max_speed)
    stop_time_list = get_stop_times(traj_list)

    time_stop_values = range(gap, max_lim + gap, gap)
    # time_stop_values = np.concatenate([np.arange(60, 60*10, 60), np.arange(60*10, max_lim + gap, gap)])
    stop_time_count, _ = np.histogram(stop_time_list, bins=time_stop_values)

    stop_time_count_ma = smooth_fun(stop_time_count[::-1], window)
    time_stop_values_ma = smooth_fun(time_stop_values[::-1], window)

    user_temporal_thr = 1200
    for cut in range(len(stop_time_count_ma) - 1, min_size, -1):
        if thompson_test(stop_time_count_ma[:cut], stop_time_count_ma[cut]):
            #  and time_stop_values_ma[cut] > time_stop_values_ma[cut]:
            # print(cut, stop_time_count_ma[cut], time_stop_values_ma[cut])
            user_temporal_thr = time_stop_values_ma[cut]
            break

    traj_list = segment_trajectories(alltraj, uid, user_temporal_thr, spatial_thr, max_speed)
    if return_cut:
        return traj_list, user_temporal_thr
    return traj_list



def segment_trajectories_geohash_adaptive2(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07,json='data',geohash_precision=6):

    spatial_thr = spatial_thr / 1000

    traj_list = list()

    tid = 0
    traj = list()
    is_a_new_traj = True
    p = None
    length = 0.0
    ref_p = None  # for stop detection
    first_iteration = True

    p_index = 0
    next_p_index = 0
    ref_p_index = 0

    for i in range(0, len(alltraj)):

        next_p = alltraj[i]
        next_p_index = i

        if first_iteration:  # first iterationh
            p = next_p
            p_index = next_p_index
            ref_p = p  # for stop detection
            traj = [p]
            length = 0.0
            is_a_new_traj = True
            first_iteration = False
        else:                 # all the others
            geo_p=geohash2.encode(p[0],p[1],precision=geohash_precision)
            
            if geo_p in json:
               temporal_thr_ad=json[geo_p]
            else:
               temporal_thr_ad=temporal_thr
            spatial_dist = spherical_distance(p, next_p)
            temporal_dist = next_p[2] - p[2]

            ref_distance = spherical_distance(ref_p, next_p)  # for stop detection
            ref_time_diff = next_p[2] - ref_p[2]  # for stop detection

            # Ignore extreme jump (with speed > 250km/h = 0.07km/s)
            if ref_distance > max_speed * ref_time_diff:
                continue

            if temporal_dist > temporal_thr_ad or (ref_time_diff > temporal_thr_ad and ref_distance < spatial_thr):
                # ended trajectory (includes case with long time gap)
                if len(traj) > 1 and not is_a_new_traj:
                    start_time = traj[0][2]
                    end_time = traj[-1][2]
                    duration = end_time - start_time
                    traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid,
                                                length=length, duration=duration,
                                                start_time=start_time, end_time=end_time))

                # Create a new trajectory
                traj = [p[:2] + [next_p[2]]]  # 1st fake point with last position previous traj and new timestamp
                p = next_p
                p_index = next_p_index
                ref_p = p  # for stop detection
                ref_p_index = p_index
                traj.append(p)
                length = 0.0
                tid += 1
                is_a_new_traj = True
            else:
                if is_a_new_traj and len(traj) > 1:
                    traj[1] = [traj[1][0], traj[1][1], traj[0][2] +int((next_p[2] - traj[0][2])/2)]
                is_a_new_traj = False

                p = next_p
                p_index = next_p_index
                if ref_distance > spatial_thr:
                    ref_p = p  # for stop detection
                    ref_p_index = p_index
                traj.append(p)
                length += spatial_dist

    if len(traj) > 1 and not is_a_new_traj:
        start_time = traj[0][2]
        end_time = traj[-1][2]
        duration = end_time - start_time
        traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid, length=length, duration=duration,
                                    start_time=start_time, end_time=end_time))

    return traj_list
                          
    
def segment_trajectories_usergeohash_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07,
                                       gap=60, max_lim=3600*48, window=3, smooth_fun=moving_avg, min_size=10,
                                       return_cut=False, file_moda='moda_stop_celle_it24.json',file_stop='stop_utenti_it24.json',file_soglie='soglie_utenti_it24.json'):
                                       
    with open(file_moda, 'r') as fb:
              data_celle=json.load(fb)
    print('num_celle',len(data_celle.keys()))
    with open(file_stop, 'r') as fl:
              data_stop= json.load(fl)
    print('num_utenti',len(data_stop.keys()))          
    with open(file_soglie, 'r') as fp:
              data_soglie = json.load(fp)
    print('num_utenti',len(data_soglie.keys()))
    
    if uid not in data_soglie :
        print("USER NOT FOUND, RETURN EMPTY")
        if return_cut: 
                return [], 0
        return 0
     
       
     
    moda_da_usare=dict()  
    user_temporal_thr= data_soglie[uid] 
    if uid in data_stop:
             
            celle=data_stop[uid]
            celle_uniche=set(celle)
            
                     
            for k in celle_uniche:
                count=celle.count(k)
                
                if (count<5):
                        moda_da_usare[k]=data_celle[k]
    
    traj_list= segment_trajectories_geohash_adaptive2(alltraj, uid, temporal_thr=user_temporal_thr, spatial_thr=50, max_speed=0.07,json=moda_da_usare,geohash_precision=5)
        
   
    
    if return_cut:
        return traj_list, user_temporal_thr
    return traj_list
    
        
    
    
    
    
def segment_trajectories_geohash_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07,json_file='data.json',geohash_precision=6):
    with open(json_file, 'r') as fp:
        data = json.load(fp)
        
    spatial_thr = spatial_thr / 1000

    traj_list = list()

    tid = 0
    traj = list()
    is_a_new_traj = True
    p = None
    length = 0.0
    ref_p = None  # for stop detection
    first_iteration = True

    p_index = 0
    next_p_index = 0
    ref_p_index = 0

    for i in range(0, len(alltraj)):

        next_p = alltraj[i]
        next_p_index = i

        if first_iteration:  # first iterationh
            p = next_p
            p_index = next_p_index
            ref_p = p  # for stop detection
            traj = [p]
            length = 0.0
            is_a_new_traj = True
            first_iteration = False
        else:                 # all the others
            geo_p=geohash2.encode(p[1],p[0],precision=geohash_precision)
            
            if geo_p in data:
               temporal_thr=data[geo_p]
            spatial_dist = spherical_distance(p, next_p)
            temporal_dist = next_p[2] - p[2]

            ref_distance = spherical_distance(ref_p, next_p)  # for stop detection
            ref_time_diff = next_p[2] - ref_p[2]  # for stop detection

            # Ignore extreme jump (with speed > 250km/h = 0.07km/s)
            if ref_distance > max_speed * ref_time_diff:
                continue

            if temporal_dist > temporal_thr or (ref_time_diff > temporal_thr and ref_distance < spatial_thr):
                # ended trajectory (includes case with long time gap)
                if len(traj) > 1 and not is_a_new_traj:
                    start_time = traj[0][2]
                    end_time = traj[-1][2]
                    duration = end_time - start_time
                    traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid,
                                                length=length, duration=duration,
                                                start_time=start_time, end_time=end_time))

                # Create a new trajectory
                traj = [p[:2] + [next_p[2]]]  # 1st fake point with last position previous traj and new timestamp
                p = next_p
                p_index = next_p_index
                ref_p = p  # for stop detection
                ref_p_index = p_index
                traj.append(p)
                length = 0.0
                tid += 1
                is_a_new_traj = True
            else:
                if is_a_new_traj and len(traj) > 1:
                    traj[1] = [traj[1][0], traj[1][1], traj[0][2] +int((next_p[2] - traj[0][2])/2)]
                is_a_new_traj = False

                p = next_p
                p_index = next_p_index
                if ref_distance > spatial_thr:
                    ref_p = p  # for stop detection
                    ref_p_index = p_index
                traj.append(p)
                length += spatial_dist

    if len(traj) > 1 and not is_a_new_traj:
        start_time = traj[0][2]
        end_time = traj[-1][2]
        duration = end_time - start_time
        traj_list.append(Trajectory(id=tid, object=traj, vehicle=uid, length=length, duration=duration,
                                    start_time=start_time, end_time=end_time))

    return traj_list
                                       
                                       
                                       
                                       
                                       
