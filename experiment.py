import csv
import numpy as np
import database_io
import pandas as pd

import matplotlib.pyplot as plt
from evaluation import evalaute_segmentation
from trajectory_segmenter import moving_median, moving_avg
from trajectory_segmenter import segment_trajectories
from trajectory_segmenter import segment_trajectories_random
from trajectory_segmenter import segment_trajectories_user_adaptive

import os

def merge_trajectories(trajectories):
    all_traj = []
    for tid in sorted(trajectories, key=lambda x: int(x)):
        traj = trajectories[tid]
        all_traj.extend(traj.object)
    return all_traj


def main():

    filename="exp.csv"
    if os.path.isfile(filename):
        os.remove(filename)

    with open(filename, 'a', newline='\n') as file:
        writer = csv.writer(file)
        writer.writerow(["initial_threshold","uid", "len(alltraj)", "M1 len(traj_list)" ,"M1 user_temporal_thresholds","M1 avg_nbr_points", "M1 time_precision", "M1 dist_coverage","M1 mobility_f1",
                         "M2 len(traj_list)" ,"M2 user_temporal_thresholds","M2 avg_nbr_points", "M2 time_precision", "M2 dist_coverage", "M2 mobility_f1",
                         "len(traj_list_random )","avg_nbr_points_random" ,"time_precision_random", "dist_coverage_random","mobility_random_f1",
                         "len(traj_list_random4 )","avg_nbr_points_random4" ,"time_precision_random4", "dist_coverage_random4","mobility_random4_f1"])


    input_table = 'tak.italy_traj'
    # con = database_io.get_connection()
    # cur = con.cursor()
    # users_list = database_io.extract_users_list('tak.italy_traj', cur)
    # cur.close()
    # con.close()

    users_list = ['100006',
                  '100022',
                  '100026',
                  '10008',
                  '100086',
                  '100087',
                  '100088',
                  '100090',
                  '100100',
                  '100117']

    # uid = users_list[0]
    # con = database_io.get_connection()
    # cur = con.cursor()
    # imh = database_io.load_individual_mobility_history(cur, uid, input_table)
    # cur.close()
    # con.close()

    con = database_io.get_connection()
    cur = con.cursor()

    #users_list = database_io.extract_users_list('tak.italy_traj', cur)

    eval_adaptive = list()
    eval_fix1200 = list()
    eval_random = list()
    eval_random2 = list()
    traj_number = list()

    thresholds=[60,120,180,240]

    for t in thresholds:
        for uid in users_list:

            print(uid, input_table)
            imh = database_io.load_individual_mobility_history(cur, uid, input_table)

            trajectories = imh['trajectories']
            alltraj = merge_trajectories(trajectories)

  #metodo 1: funzione che usa la mediana mobile
            traj_list1, user_temporal_thr1 = segment_trajectories_user_adaptive(alltraj, uid, temporal_thr=t, spatial_thr=50,
                                                                          max_speed=0.07, gap=60, max_lim=3600 * 48,
                                                                          window=15, smooth_fun=moving_median, min_size=10,
                                                                          return_cut=True)


            avg_nbr_points1 = np.mean([len(t) for t in traj_list1])
            print('user_temporal_thr', user_temporal_thr1)
            print('NT %d - ANP %.2f' % (len(traj_list1), avg_nbr_points1))
            time_precision1, dist_coverage1, mobility1_f1 = evalaute_segmentation(alltraj, traj_list1, print_report=True)
            eval_adaptive.append((time_precision1, dist_coverage1, mobility1_f1))




#metodo 2: funzione semplice
            traj_list2 = segment_trajectories(alltraj, uid, temporal_thr=1200, spatial_thr=50, max_speed=0.07)
            avg_nbr_points2 = np.mean([len(t) for t in traj_list2])
            user_temporal_thr2=1200
            print('NT %d - ANP %.2f' % (len(traj_list2), avg_nbr_points2))
            time_precision2, dist_coverage2, mobility2_f1 = evalaute_segmentation(alltraj, traj_list2, print_report=True)
            eval_fix1200.append((time_precision2, dist_coverage2, mobility2_f1))


#metodo 3: funzione random
            traj_list_random = segment_trajectories_random(alltraj, uid, nbr_traj=2000)
            avg_nbr_points_random = np.mean([len(t) for t in traj_list_random])
            print('NT %d - ANP %.2f' % (len(traj_list_random), avg_nbr_points_random))
            time_precision_random, dist_coverage_random,mobility_random_f1 = evalaute_segmentation(alltraj, traj_list_random, print_report=True)
            eval_random.append((time_precision_random, dist_coverage_random, mobility_random_f1))

#metodo 4: funzione random con nbr_traj_max dato dal primo metodo
            traj_list_random4 = segment_trajectories_random(alltraj, uid, nbr_traj_min=2, nbr_traj_max=len(traj_list2))
            avg_nbr_points_random4 = np.mean([len(t) for t in traj_list_random4])
            print('NT %d - ANP %.2f' % (len(traj_list_random4), avg_nbr_points_random4))
            time_precision_random4, dist_coverage_random4,mobility_random4_f1 = evalaute_segmentation(alltraj, traj_list_random4, print_report=True)
            eval_random2.append((time_precision_random4, dist_coverage_random4,mobility_random4_f1))

            #riempire file

            with open(filename, 'a', newline='\n') as file:
                writer = csv.writer(file)
                writer.writerow([t,uid,len(alltraj),  len(traj_list1),user_temporal_thr1, avg_nbr_points1, time_precision1, dist_coverage1, mobility1_f1,
                                 len(traj_list2),user_temporal_thr2, avg_nbr_points2, time_precision2, dist_coverage2, mobility2_f1,
                                 len(traj_list_random ),avg_nbr_points_random ,time_precision_random, dist_coverage_random,mobility_random_f1,
                                 len(traj_list_random4 ),avg_nbr_points_random4 ,time_precision_random4, dist_coverage_random4,mobility_random4_f1])


if __name__ == '__main__':
    main()

import os
print (os.getcwd())
