#!/usr/bin/python 
import control

m=control.find_laser()
pos=((m[0]+m[1])/2,(m[2]+m[3])/2)
print "pos: %s %s" % (pos[0],pos[1])
control.move_pd(pos[0],pos[1])
mpd=[]
rpd=[]
for kkk in xrange(10):
    r=[time.strftime('%H:%M:%S',time.localtime(time.time())),control.read_pico(),control.read_dmm()]
    mpd.append(float(r[1])*1e6)
    rpd.append(float(r[2])*1e6)
    print "%s %s %s %s %s %s %s %s %s" % (r[0],r[1],r[2],pos[0],pos[1],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1])
control.move_pd(-pos[0],-pos[1])

def mean(v):
    return 1.0*sum(v)/len(v)

mpd_mean=mean(mpd)
rpd_mean=mean(rpd)
print "Main:  ", mpd_mean
print "Ref:   ", rpd_mean
print "Ratio: ", mpd_mean/rpd_mean

