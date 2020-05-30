import csv
import numpy as np
import database_io
import pandas as pd
import matplotlib
from matplotlib import pyplot

data= pd.read_csv("/home/agnese/PycharmProjects/TrajectorySegmentation/Results/"+"traj_seg_exp10.csv")

data.head()


print(data.columns)

print(data.query("'method'=ATS")['len(alltraj)'])

pyplot.plot(data.query("temporal_thr==600")['M1 len(traj_list)'].values,label="thr=600")
pyplot.plot(data.query("temporal_thr==120")['M1 len(traj_list)'].values,label="thr=120")
pyplot.plot(data.query("temporal_thr==120")['M1 len(traj_list)'].values,label="thr=1200")
#pyplot.plot(data.query("temporal_thr==240")['M1 len(traj_list)'].values,label="thr=240")
pyplot.legend(loc="lower right")
pyplot.savefig("traj_list1")
pyplot.cla()

pyplot.plot(data.query("temporal_thr==60")['M1 time_precision'].values,label="thr=60")
pyplot.plot(data.query("temporal_thr==120")['M1 time_precision'].values,label="thr=120")
pyplot.plot(data.query("temporal_thr==180")['M1 time_precision'].values,label="thr=180")
pyplot.plot(data.query("temporal_thr==240")['M1 time_precision'].values,label="thr=240")
pyplot.legend(loc="lower right")
pyplot.savefig("time_precision1")
pyplot.cla()

pyplot.plot(data.query("temporal_thr==60")['M1 time_precision'],label="method1 (smooth funct)")
pyplot.plot(data.query("temporal_thr==60")['M2 time_precision'],label="method2 (simple funct)")
pyplot.plot(data.query("temporal_thr==60")['time_precision_random'],label="method3 (random)")
pyplot.plot(data.query("temporal_thr==60")['time_precision_random4'],label="method4 (random2)")
pyplot.ylabel('time precision')
pyplot.legend(loc="upper left")
pyplot.savefig("time precision")
pyplot.cla()

pyplot.plot(data.query("temporal_thr==60")['M1 dist_coverage'],label="method1 (smooth funct)")
pyplot.plot(data.query("temporal_thr==60")['M2 dist_coverage'],label="method2 (simple funct)")
pyplot.plot(data.query("temporal_thr==60")['dist_coverage_random'],label="method3 (random)")
pyplot.plot(data.query("temporal_thr==60")['dist_coverage_random4'],label="method4 (random2)")
pyplot.title('dist_coverage')
pyplot.legend(loc="lower right")
pyplot.savefig("distance coverage")
pyplot.cla()

pyplot.plot(data['M1 mobility_f1'],label="method1 (smooth funct)")
pyplot.plot(data['M2 mobility_f1'],label="method2 (simple funct)")
pyplot.plot(data['mobility_random_f1'],label="method3 (random)")
pyplot.plot(data['mobility_random4_f1'],label="method4 (random2)")
pyplot.title('mobility_f1')
pyplot.legend(loc="upper left")
pyplot.savefig("mobilityf1")
pyplot.cla()