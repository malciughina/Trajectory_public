import os
import datetime
import numpy as np
import database_io
import pandas as pd

from evaluation import evalaute_segmentation
from trajectory_segmenter import moving_median, moving_avg
from trajectory_segmenter_pycharm import segment_trajectories
from trajectory_segmenter import segment_trajectories_random, segment_trajectories_random2
from trajectory_segmenter import *

from DEBUG_trajectory_segmenter_pycharm import segment_trajectories_debug

from collections import defaultdict


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
    #points, traj_from_to_ = get_points_trajfromto_list(traj_list)
    #print(" eval get_points_trajfromto_list done")
    #loc = locations_detection(points, min_dist=50.0, nrun=1)
    #print(" eval locations_detection done")
    #print('loc',loc)
   #print(' len(loc)', len(loc['location_prototype'])), )
    res = [nbr_traj, avg_nbr_points, avg_length, avg_duration,
           avg_sampling_rate, std_sampling_rate, med_sampling_rate,
           time_precision, dist_coverage, mobility_f1]
           
    #res = [nbr_traj, avg_nbr_points, avg_length, avg_duration,
     #      avg_sampling_rate, std_sampling_rate, med_sampling_rate,
      #     time_precision, dist_coverage, mobility_f1,len(loc['location_prototype']) if loc!= None else -999]
    #print('res',res)
    print('res',res)
    return res




def run(cur, uid, input_table):
    results = list()
    imh = database_io.load_individual_mobility_history(cur, uid, input_table)
    trajectories = imh['trajectories']
    alltraj = merge_trajectories(trajectories)
    #print (alltraj)
    nbr_points = len(alltraj)
    if nbr_points <= 100:
        raise Exception
    
    sampling_rate_list = [alltraj[i+1][2] - alltraj[i][2] for i in range(0, len(alltraj)-1)]
    avg_sampling_rate = np.mean(sampling_rate_list)
    std_sampling_rate = np.std(sampling_rate_list)
    med_sampling_rate = np.median(sampling_rate_list)
    base_res = [input_table, uid, nbr_points, avg_sampling_rate, std_sampling_rate, med_sampling_rate]
    

    traj_list, user_temporal_thr = segment_trajectories_user_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50,
                                                                      max_speed=0.07, gap=60, max_lim=3600 * 48,
                                                                      window=15, smooth_fun=moving_median, min_size=10,return_cut=True)

    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['ATS'] + eval_res + [user_temporal_thr])
    nbr_traj_adaptive = len(traj_list)
    
    traj_list=segment_trajectories_geohash_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07,json_file='itthresholds5_bon.json',geohash_precision=5)
    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['GEO'] + eval_res + [user_temporal_thr])
   

    traj_list = segment_trajectories_random2(alltraj, uid, nbr_traj=nbr_traj_adaptive)
    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['RND2'] + eval_res + [-1])
    print('pippi',len(traj_list) )

  
    traj_list = segment_trajectories(alltraj, uid, temporal_thr=1200, spatial_thr=50, max_speed=0.07)
    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['FTS_1200'] + eval_res + [1200])
    

    traj_list = segment_trajectories(alltraj, uid, temporal_thr=120, spatial_thr=50, max_speed=0.07)
    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['FTS_120'] + eval_res + [120])

    traj_list = segment_trajectories_random(alltraj, uid)
    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['RND1'] + eval_res + [-1])
    
    traj_list,user_temporal_thr= segment_trajectories_usergeohash_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50, max_speed=0.07,
                                       gap=60, max_lim=3600*48, window=15, smooth_fun=moving_median, min_size=10,
                                       return_cut=True, file_moda='moda_stop_celle_itp5.json',file_stop='stop_utenti_itp5.json',file_soglie='soglie_utenti_itp5.json')
    eval_res = evaluate(alltraj, traj_list)
    results.append(base_res + ['ACTS'] + eval_res +  [user_temporal_thr])


    traj_list = segment_trajectories_random(alltraj, uid, nbr_traj=nbr_traj_adaptive)
    if len(traj_list) > 25:
        eval_res = evaluate(alltraj, traj_list)
        results.append(base_res + ['RND2'] + eval_res + [-1])

    return results


def main():
    input_table = 'tak.italy_traj'
    filename = 'Roma_29setp5.csv'

    header = ['input_table', 'uid', 'nbr_points', 'avg_sampling_rate', 'std_sampling_rate', 'med_sampling_rate',
              'method', 'nbr_traj', 'avg_nbr_points', 'avg_length', 'avg_duration',
              'avg_sampling_rate_traj', 'std_sampling_rate_traj', 'med_sampling_rate_traj',
              'time_precision', 'dist_coverage', 'mobility_f1', 'temporal_thr']

    processed_users = list()
    if os.path.isfile(filename):
        os.remove(filename)
        #df = pd.read_csv(filename)
        #processed_users = list(df['uid'])
        #fileout = open(filename, 'a')
   # else:
    fileout = open(filename, 'w')
    fileout.write('%s\n' % (','.join(header)))
    fileout.flush()

   # users_list = ['100966']
     
    #               '100022',
    #               '100026',
    #               '10008',
    #               '100086',
    #               '100087',
    #               '100088',
    #               '100090',
    #               '100100',
    #               '100117']

    con = database_io.get_connection()
    cur = con.cursor()
    users_list = database_io.extract_users_list('tak.italy_traj', cur)
    cur.close()
    con.close()
    con = database_io.get_connection()
    cur = con.cursor()

    print(len(users_list))

    count = 0
    nbr_exp = 2000

    for i, uid in enumerate(users_list):
        print(datetime.datetime.now(), uid, input_table, '[%s/%s]' % (i, len(users_list)))
        if uid in processed_users:
            count+=1
            if count>= nbr_exp:
                break
            continue
        #results = run(cur, uid, input_table)
        try:
           
           results = run(cur, uid, input_table)
           for j, res in enumerate(results):
               fileout.write('%s\n' % (','.join([str(r) for r in res])))
               fileout.flush()
        except Exception:
            print(datetime.datetime.now(), uid, input_table, 'Error')
            continue

        count += 1
        if count >= nbr_exp:
            break

    fileout.flush()
    cur.close()
    con.close()

    fileout.close()




if __name__ == '__main__':
    main()
