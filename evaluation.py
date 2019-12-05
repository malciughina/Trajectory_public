import numpy as np

from mobility_distance_functions import spherical_distance


def time_precision_score(alltraj, traj_list):
    allmoves_time = alltraj[-1][2] - alltraj[0][2]
    move_time = np.sum(t.duration() for t in traj_list)
    return 1-move_time/allmoves_time


def dist_coverage_score(alltraj, traj_list):
    allmoves_dist = np.sum([spherical_distance(alltraj[i + 1], alltraj[i]) for i in range(len(alltraj) - 1)])
    move_dist = np.sum([t.length() for t in traj_list])
    # move_dist2 = np.sum([spherical_distance(traj_list[i + 1].start_point(), traj_list[i].end_point()) for i in range(len(traj_list) - 1)])
    # move_dist += move_dist2
    # print('move_dist', move_dist, 'allmoves_dist', allmoves_dist, 'div', move_dist/allmoves_dist)
    return move_dist/allmoves_dist


def mobility_f1_score(dist_coverage, time_precision, beta=1.0):
    return (1+beta**2)*time_precision*dist_coverage/((beta**2)*time_precision + dist_coverage)


def evalaute_segmentation(alltraj, traj_list, print_report=False):
    time_precision = time_precision_score(alltraj, traj_list)
    dist_coverage = dist_coverage_score(alltraj, traj_list)
    mobility_f1 = mobility_f1_score(dist_coverage, time_precision, beta=0.25)
    if print_report:
        print('TP: %.3f - DC: %.3f - F1: %.3f' % (time_precision, dist_coverage, mobility_f1))
    return time_precision, dist_coverage, mobility_f1
