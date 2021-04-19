import os
import datetime
import numpy as np
import database_io
import pandas as pd
import time
from matplotlib import pyplot as plt



def main():
        lista_file1=[200,400,600,800,1000,1250,1500,1750,2001]
        lista_file2=['_gen','_feb','_mar','_apr','_may','_june','_july','_agos','_sep','_ott','_nov','_dic']
        lista_ats=[]            
        lista_geo=[]
        lista_rnd=[]
        lista_fts=[]
        lista_acts=[]
        for t in lista_file2:
                nomefile='ROMAexecution_time'+str(t)+'.txt'
                fs=open(nomefile)
                lines=fs.readlines()
                ats_tot=0
                geo_tot=0
                rnd_tot=0
                fts_tot=0
                acts_tot=0
                for l in lines:
                        if 'ATS' in l:
                                continue
                        
                        ats=float(l.split(',')[0])
                        geo=float(l.split(',')[1])+float(l.split(',')[0])
                        rnd=float(l.split(',')[2])
                        fts=float(l.split(',')[3])
                        acts=float(l.split(',')[4])+float(l.split(',')[0])
                        
                        ats_tot+=ats
                        geo_tot+=geo
                        rnd_tot+=rnd
                        fts_tot+=fts
                        acts_tot+=acts
                        
                print(ats_tot)
                print(geo_tot)
                print(rnd_tot)
                print(fts_tot)
                print(acts_tot)
                
                lista_ats.append(ats_tot)           
                lista_geo.append(geo_tot)
                lista_rnd.append(rnd_tot)
                lista_fts.append(fts_tot)
                lista_acts.append(acts_tot)
        
        labels1= [200,400,600,800,1000,1250,1500,1750,2000]  
        labels2=[1,2,3,4,5,6,7,8,9,10,11,12]  
        x=[0,1,2,3,4,5,6,7,8,9,10,11] 
        f = plt.figure()
        f.set_figheight(6.3)
        f.set_figheight(4.6)  
        plt.plot(lista_ats,label='ATS',marker=".")
        plt.plot(lista_geo,label='$ACTS_{LOC}$',marker="^")
        plt.plot(lista_acts,label='$ACTS_{WOTC}$',marker="*")
        plt.plot(lista_rnd,label='RTS',marker="d")
        plt.plot(lista_fts,label='$FTS_{1200}$',marker="s")
        plt.show()
        plt.legend(loc="upper left", fontsize=13, frameon=False)
        plt.xticks(x,labels2, rotation='horizontal',fontsize=13)
        plt.yticks(fontsize=13)
        #plt.xlim(1,12)
        plt.title('Run Times (Rome)',fontsize=16)
        plt.xlabel('Time Span (months)',fontsize=14)
        plt.ylabel('Time (seconds)',fontsize=13)
        
        plt.savefig('Scalability_ROME')
        plt.cla()

if __name__ == '__main__':
    main()
