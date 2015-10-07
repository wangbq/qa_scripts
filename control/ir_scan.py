import control
import os,sys,math,time

#time.sleep(120)

stage1=100
stage2=100
stage3=100
stage4=500
steps=((100, 500), (10, 50))

#-------------------------------config start----------------------
filename="" #output filename, e.g. 150729-1.txt
degree=None #incident angle, degree
minute=None #incident angle, minute
L0=1.25
bounce=None #number of bounces
bulk=None   #bulk transmittance
rat0=None   #main/ref ratio in air
n1=1.00
n2=1.47
scan_route=[(0,0,0,0),(0,-400,0,2000),(0,-400,0,2000),(0,-400,0,2000)]+[(500,1200,500,-6000),(0,-400,0,2000),(0,-400,0,2000),(0,-400,0,2000)]*(2*30)
#-------------------------------config end----------------------

angle1=math.radians(degree+1.0*minute/60)
angle2=math.asin(n1/n2*math.sin(angle1))
Rs1=math.pow((n1*math.cos(angle1)-n2*math.cos(angle2))/(n1*math.cos(angle1)+n2*math.cos(angle2)),2)
Rp1=math.pow((n1*math.cos(angle2)-n2*math.cos(angle1))/(n1*math.cos(angle2)+n2*math.cos(angle1)),2)
RR=(1-Rs1)*(1-Rs1)
L=L0/math.cos(angle2)

def mean(v):
    return 1.0*sum(v)/len(v)

def rms(v):
    m=mean(v)
    res=map(lambda x:(x-m)*(x-m),v)
    return math.sqrt(mean(res))

f=open(filename,"a")
f.write("#---------------------------------------------------------------------------------\n")
f.write("#IR scan starts at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
f.write("#degree: %s\n" % degree)
f.write("#minute: %s\n" % minute)
f.write("#L0: %s\n" % L0)
f.write("#angle1: %s\n" % math.degrees(angle1))
f.write("#angle2: %s\n" % math.degrees(angle2))
f.write("#reflect angle: %s\n" % (90.0-math.degrees(angle2)))
f.write("#L: %s\n" % L)
f.write("#bounce: %s\n" % bounce)
f.write("#bulk: %s\n" % bulk)
f.write("#rat0: %s\n" % rat0)

move_route=[]
reflect=[]
for i in xrange(len(scan_route)):
    control.move_all(scan_route[i])
    print "move_lr: (%s,%s)" % (scan_route[i][0],scan_route[i][1])
    print "move_pd: (%s,%s)" % (scan_route[i][2],scan_route[i][3])

    if i==0:
        print "first point"
        m=control.find_laser()
        #m=(0,0,0,0)
    else:
        print "in the quartz"
        m=control.find_laser([steps[-1]],move_route[0])
        #m=(0,0,0,0)

    pos=((m[0]+m[1])/2,(m[2]+m[3])/2)
    control.move_pd(pos[0],pos[1])
    mpd=[]
    rpd=[]
    for kkk in xrange(10):
        r=control.read_time_pico_dmm()
        mpd.append(float(r[1]))
        rpd.append(float(r[2]))
        print "%s %s %s %s %s %s %s %s %s" % (r[0],r[1],r[2],pos[0],pos[1],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1])
        f.write("%s %s %s %s %s %s %s %s %s\n" % (r[0],r[1],r[2],pos[0],pos[1],control.global_lr[0],control.global_lr[1],control.global_pd[0],control.global_pd[1]))
        f.flush()
    control.move_pd(-pos[0],-pos[1])
    rat=mean(mpd)/mean(rpd)
    if rat0<1e-6:
        print "Wrong rat0!"
        sys.exit(1)
    ir=math.pow(rat/rat0/RR/math.pow(bulk,L),1.0/bounce)
    corr0=Rs1*Rs1*math.pow(bulk,2*L)*math.pow(ir,2*bounce)/bounce
    print "Internal Reflectivity: ",(ir-corr0)*100,"%"
    reflect.append(ir)
    move_route.append(m)
    print ""

control.move_all([-control.global_lr[0], -control.global_lr[1], -control.global_pd[0], -control.global_pd[1])

corr=Rs1*Rs1*math.pow(bulk,2*L)*math.pow(mean(reflect),2*bounce)/bounce
#print "Correction: ",corr
print "Internal Reflectivity: ", mean(reflect)-corr, ", RMS: ", rms(reflect)
print "Scan Finished Successfully!"
f.write("#IR scan stops at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
f.write("#---------------------------------------------------------------------------------\n")
f.close()

os.system("~/backup.sh")
