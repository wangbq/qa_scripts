#!/usr/bin/python 
import control
import time,math

nstep=100 #number of steps

#step=(10,0,10,0) #step for BT scan
#step=(0,10,0,-50) #step for IR scan

start=(0,0) #starting position
filename="" #output filename, e.g. 150727-2.txt

f=open(filename,"a")
f.write("#---------------------------------------------------------------------------------\n")
f.write("#edge scan starts at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
f.write("#start point: %s %s\n" % (start[0],start[1]))
f.write("#step: %s %s %s %s\n" % (step[0],step[1],step[2],step[3]))

mpd=[]
pos=[]
for iii in xrange(nstep):
    control.move_all(step)
    r=control.read_time_pico_dmm()
    mpd.append(float(r[1])*1e6)
    x=control.global_lr[0]
    y=control.global_lr[1]
    pos.append(math.sqrt(x*x+y*y)/100.0)
    f.write("%s %s %s %s %s %s %s\n" % (r[0],r[1],r[2],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1]))
    print r[0],r[1],r[2],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1]

control.move_all([-control.global_lr[0], -control.global_lr[1], -control.global_pd[0], -control.global_pd[1])

f.write("#edge scan stops at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
f.write("#---------------------------------------------------------------------------------\n")
f.close()

def avg(v):
    return sum(v)/len(v)

up=avg(mpd[:10])
down=avg(mpd[(len(mpd)-10):])
print "up: ",up,"uA, down: ",down,"uA"
index=0
for i in xrange(len(mpd)):
    if (mpd[i]-down)<0.5*(up-down):
        index=i
        break
print "index: ",index,", position: ",pos[index],"mm, current: ",mpd[index],"uA"
