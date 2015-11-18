#!/usr/bin/python 
import control
import sys

f=None
if len(sys.argv)>1:
    f=open(sys.argv[1],"a")

m=control.find_laser()
pos=((m[0]+m[1])/2,(m[2]+m[3])/2)
print "pos: %s %s" % (pos[0],pos[1])
control.move_pd(pos[0],pos[1])
mpd=[]
rpd=[]
for kkk in xrange(10):
    r=control.read_time_pico_dmm()
    mpd.append(float(r[1])*1e6)
    rpd.append(float(r[2])*1e6)
    if f!=None:
        f.write("%s %s %s %s %s %s %s %s %s\n" % (r[0],r[1],r[2],pos[0],pos[1],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1]))
    print "%s %s %s %s %s %s %s %s %s" % (r[0],r[1],r[2],pos[0],pos[1],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1])
control.move_pd(-pos[0],-pos[1])

def mean(v):
    return 1.0*sum(v)/len(v)

mpd_mean=mean(mpd)
rpd_mean=mean(rpd)
print "Main:  ", mpd_mean
print "Ref:   ", rpd_mean
print "Ratio: ", mpd_mean/rpd_mean

if f!=None:
    f.write("#ratio: %s" % (mpd_mean/rpd_mean))
    f.close()
