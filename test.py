import numpy as np
import database_io

from evaluation import evalaute_segmentation
from trajectory_segmenter import moving_median, moving_avg
from trajectory_segmenter import segment_trajectories
from trajectory_segmenter import segment_trajectories_random
from trajectory_segmenter import segment_trajectories_user_adaptive


def merge_trajectories(trajectories):
    all_traj = []
    for tid in sorted(trajectories, key=lambda x: int(x)):
        traj = trajectories[tid]
        all_traj.extend(traj.object)
    return all_traj


def main():
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

    eval_adaptive = list()
    eval_fix1200 = list()
    eval_random = list()

    for uid in users_list:

        print(uid, input_table)
        imh = database_io.load_individual_mobility_history(cur, uid, input_table)


        trajectories = imh['trajectories']
        alltraj = merge_trajectories(trajectories)
        # print(len(alltraj))

        traj_list, user_temporal_thr = segment_trajectories_user_adaptive(alltraj, uid, temporal_thr=60, spatial_thr=50,
                                                                          max_speed=0.07, gap=60, max_lim=3600 * 48,
                                                                          window=15, smooth_fun=moving_median, min_size=10,
                                                                          return_cut=True)
        avg_nbr_points = np.mean([len(t) for t in traj_list])
        print('user_temporal_thr', user_temporal_thr)
        print('NT %d - ANP %.2f' % (len(traj_list), avg_nbr_points))
        time_precision, dist_coverage, mobility_f1 = evalaute_segmentation(alltraj, traj_list, print_report=True)
        eval_adaptive.append((time_precision, dist_coverage, mobility_f1))

        print('------')

        traj_list = segment_trajectories(alltraj, uid, temporal_thr=1200, spatial_thr=50, max_speed=0.07)
        avg_nbr_points = np.mean([len(t) for t in traj_list])
        print('NT %d - ANP %.2f' % (len(traj_list), avg_nbr_points))
        time_precision, dist_coverage, mobility_f1 = evalaute_segmentation(alltraj, traj_list, print_report=True)
        eval_fix1200.append((time_precision, dist_coverage, mobility_f1))

        print('------')

        traj_list = segment_trajectories(alltraj, uid, temporal_thr=120, spatial_thr=50, max_speed=0.07)
        avg_nbr_points = np.mean([len(t) for t in traj_list])
        print('NT %d - ANP %.2f' % (len(traj_list), avg_nbr_points))
        time_precision, dist_coverage, mobility_f1 = evalaute_segmentation(alltraj, traj_list, print_report=True)

        print('------')

        traj_list = segment_trajectories_random(alltraj, uid, nbr_traj=2000)
        avg_nbr_points = np.mean([len(t) for t in traj_list])
        print('NT %d - ANP %.2f' % (len(traj_list), avg_nbr_points))
        time_precision, dist_coverage, mobility_f1 = evalaute_segmentation(alltraj, traj_list, print_report=True)
        eval_random.append((time_precision, dist_coverage, mobility_f1))

    cur.close()
    con.close()
    print('')

    print('ADP - TP: %.3f - DC: %.3f - F1: %.3f' % (np.median([v[0] for v in eval_adaptive]),
                                                    np.median([v[1] for v in eval_adaptive]),
                                                    np.median([v[2] for v in eval_adaptive])))

    print('FIX - TP: %.3f - DC: %.3f - F1: %.3f' % (np.median([v[0] for v in eval_fix1200]),
                                                    np.median([v[1] for v in eval_fix1200]),
                                                    np.median([v[2] for v in eval_fix1200])))

    print('ADP - TP: %.3f - DC: %.3f - F1: %.3f' % (np.mean([v[0] for v in eval_adaptive]),
                                                    np.mean([v[1] for v in eval_adaptive]),
                                                    np.mean([v[2] for v in eval_adaptive])))

    print('FIX - TP: %.3f - DC: %.3f - F1: %.3f' % (np.mean([v[0] for v in eval_fix1200]),
                                                    np.mean([v[1] for v in eval_fix1200]),
                                                    np.mean([v[2] for v in eval_fix1200])))

    print('ADP - TP: %.3f - DC: %.3f - F1: %.3f' % (np.std([v[0] for v in eval_adaptive]),
                                                    np.std([v[1] for v in eval_adaptive]),
                                                    np.std([v[2] for v in eval_adaptive])))

    print('FIX - TP: %.3f - DC: %.3f - F1: %.3f' % (np.std([v[0] for v in eval_fix1200]),
                                                    np.std([v[1] for v in eval_fix1200]),
                                                    np.std([v[2] for v in eval_fix1200])))

    # print('RND - TP: %.3f - DC: %.3f - F1: %.3f' % (np.median([v[0] for v in eval_random]),
    #                                                 np.median([v[1] for v in eval_random]),
    #                                                 np.median([v[2] for v in eval_random])))

if __name__ == '__main__':
    main()

