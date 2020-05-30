import csv
import numpy as np
import database_io
import pandas as pd
import matplotlib
from matplotlib import pyplot

data= pd.read_csv("/home/agnese/PycharmProjects/TrajectorySegmentation/Results/"+"traj_seg_exp100.csv")

data.head()


print(data.columns)

print(data.query("method=='ATS'")['nbr_points'])

pyplot.plot(data.query("method=='ATS'")['nbr_points'])
pyplot.savefig("priva")
pyplot.cla()

pyplot.plot(data.query("method=='ATS'")['nbr_points'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['nbr_points'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['nbr_points'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['nbr_points'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['nbr_points'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/nbr_points")
pyplot.cla()

pyplot.plot(data.query("method=='ATS'")['nbr_traj'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['nbr_traj'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['nbr_traj'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['nbr_traj'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['nbr_traj'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.title('Number of trajectories')
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/nbr_traj")
pyplot.cla()

pyplot.plot(data.query("method=='ATS'")['time_precision'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['time_precision'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['time_precision'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['time_precision'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['time_precision'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.title('Time precision')
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/time_precision")
pyplot.cla()

pyplot.plot(data.query("method=='ATS'")['dist_coverage'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['dist_coverage'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['dist_coverage'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['dist_coverage'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['dist_coverage'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.title('Distance Coverage')
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/dist_coverage")
pyplot.cla()

pyplot.plot(data.query("method=='ATS'")['mobility_f1'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['mobility_f1'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['mobility_f1'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['mobility_f1'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['mobility_f1'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.title('Mobility F1')
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/mobility_f1")
pyplot.cla()


pyplot.plot(data.query("method=='ATS'")['avg_length'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['avg_length'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['avg_length'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['avg_length'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['avg_length'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.title('avg_lenght')
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/avg_length")
pyplot.cla()

pyplot.plot(data.query("method=='ATS'")['avg_duration'].values,label="ATS")
pyplot.plot(data.query("method=='FTS_1200'")['avg_duration'].values,label="FTS_1200")
pyplot.plot(data.query("method=='FTS_120'")['avg_duration'].values,label="FTS_120")
pyplot.plot(data.query("method=='RND1'")['avg_duration'].values,label="RND1")
pyplot.plot(data.query("method=='RND2'")['avg_duration'].values,label="RND2")
pyplot.legend(loc="lower right")
pyplot.title('avg_duration')
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/avg_duration")
pyplot.cla()

pyplot.errorbar(data.query("method=='ATS'")['nbr_points'],data.query("method=='ATS'")['avg_sampling_rate'].values,data.query("method=='ATS'")['std_sampling_rate'],label="ATS")
pyplot.savefig("/home/agnese/PycharmProjects/TrajectorySegmentation/plots/100utenti/sampling_rate")
pyplot.cla()