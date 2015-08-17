#!/usr/bin/python
import os,sys,time,re

global_lr=[0,0]
global_pd=[0,0]

#all steps in micrometer (um)
def move_lr(x,y):
    cmd="./move_stage 1 %d 2 %d" % (x,y)
    r=os.system(cmd)
    if r!=0:
        print "move_lr failed!"
        sys.exit(-1)
    global_lr[0]+=x
    global_lr[1]+=y

def move_pd(x,y):
    cmd="./move_stage 3 %d 4 %d" % (x,y)
    r=os.system(cmd)
    if r!=0:
        print "move_lr failed!"
        sys.exit(-1)
    global_pd[0]+=x
    global_pd[1]+=y

def move_all(x1,x2,x3,x4):
    cmd="./move_stage 1 %d 2 %d 3 %d 4 %d" % (x1,x2,x3,x4)
    r=os.system(cmd)
    if r!=0:
        print "move_all failed!"
        sys.exit(-1)
    global_lr[0]+=x1
    global_lr[1]+=x2
    global_pd[0]+=x3
    global_pd[1]+=x4

def read_pico_dmm():
    max_read=1e-3
    read_count=0
    while True:
        r=os.popen("./meas_pico_dmm").read().strip().split()
        read_count=read_count+1
        if len(r)==3 and re.match("\+\d\.\d+E-\d\d",r[1]) and re.match("\+\d\.\d+E-\d\d",r[2]) and float(r[1])<max_read and float(r[2])<max_read:
            return r
        elif read_count>10:
            print "read_pico_dmm failed!"
            sys.exit(-1)
        else:
            time.sleep(3)

def scan_pd(nx, ny, stepx, stepy, f):
    vy=ny/abs(ny)
    for j in xrange(abs(ny)+1):
        scan_pd_line(0,nx,stepx,f)
        if j==abs(ny):
            break
        move_pd(0,vy*stepy)
        nx*=-1

#axis=0 for x, axis=1 for y
def scan_pd_line(axis, n, step, f):
    v=n/abs(n)
    for i in xrange(abs(n)+1):
        r=read_pico_dmm()
        print "%s %s %s %s %s" % (r[0],r[1],r[2],global_pd[0],global_pd[1])
        f.write("%s %s %s %s %s\n" % (r[0],r[1],r[2],global_pd[0],global_pd[1]))
        if i==abs(n):
            break
        if axis==0:
            move_pd(v*step,0)
        elif axis==1:
            move_pd(0,v*step)
        else:
            print "scan_pd_line: wrong axis!"
            sys.exit(-1)

def find_laser(steps=[(100, 500), (10, 50)], prev_move=(0,0,0,0)):
    ini_pos=(global_pd[0],global_pd[1])
    frac=0.5
    min_read=100e-6

    ini_pd=float(read_pico_dmm()[1])
    if ini_pd<min_read:
        print "Laser is too close to the edge!"
        sys.exit(-1)

    edge=[]
    edge_pos=(0,0)

    move_pd(prev_move[0],0)
    for step in steps:
        edge_pos=find_edge(0, 1, step, frac*ini_pd)
    edge.append(edge_pos)
    move_pd(ini_pos[0]-global_pd[0], ini_pos[1]-global_pd[1])

    move_pd(prev_move[1],0)
    for step in steps:
        edge_pos=find_edge(0, -1, step, frac*ini_pd)
    edge.append(edge_pos)
    move_pd(ini_pos[0]-global_pd[0], ini_pos[1]-global_pd[1])

    move_pd(0,prev_move[2])
    for step in steps:
        edge_pos=find_edge(1, 1, step, frac*ini_pd)
    edge.append(edge_pos)
    move_pd(ini_pos[0]-global_pd[0], ini_pos[1]-global_pd[1])

    move_pd(0,prev_move[3])
    for step in steps:
        edge_pos=find_edge(1, -1, step, frac*ini_pd)
    edge.append(edge_pos)
    move_pd(ini_pos[0]-global_pd[0], ini_pos[1]-global_pd[1])

    movement=(edge[0][0]-ini_pos[0],edge[1][0]-ini_pos[0],edge[2][1]-ini_pos[1],edge[3][1]-ini_pos[1])
    return movement

def find_edge(axis, phase, step, edge_read):
    r=float(read_pico_dmm()[1])
    print "pd: (%s,%s) r: %s" % (global_pd[0],global_pd[1],r*1e6)
    d=r-edge_read
    if axis==0:#x axis
        v=[phase*cmp(d,0), 0]
    elif axis==1:#y axis
        v=[0, phase*cmp(d,0)]
    prev=[global_pd[0], global_pd[1], d]
    while True:
        move_pd(v[0]*step[0],v[1]*step[1])
        r=float(read_pico_dmm()[1])
        print "pd: (%s,%s) r: %s" % (global_pd[0],global_pd[1],r*1e6)
        d=r-edge_read
        v[0]=phase*cmp(d,0)*abs(v[0])
        v[1]=phase*cmp(d,0)*abs(v[1])
        if d*prev[2]<0:
            if abs(d)>abs(prev[2]):
                move_pd(prev[0]-global_pd[0],prev[1]-global_pd[1])
                return (prev[0],prev[1])
            else:
                return (global_pd[0],global_pd[1])
        else:
            prev[0]=global_pd[0]
            prev[1]=global_pd[1]
            prev[2]=d

def scan_quartz(scan_route,f):
    for route in scan_route:
        move_lr(route[0],route[1])
        print "move_lr: (%s,%s)" % (route[0],route[1])
        move_pd(route[2],route[3])
        print "move_pd: (%s,%s)" % (route[2],route[3])

        m=find_laser()
        pos=((m[0]+m[1])/2,(m[2]+m[3])/2)
        move_pd(pos[0],pos[1])
        r=read_pico_dmm()
        move_pd(-pos[0],-pos[1])
        print "%s %s %s %s %s" % (r[0],r[1],r[2],pos[0],pos[1])
        f.write("%s %s %s %s %s\n" % (r[0],r[1],r[2],pos[0],pos[1]))
        f.flush()
        print ""

def calib(file1, file2):
    lx=[]
    sum_x=0
    n_x=0
    max=0
    max_x=0
    for line in open(file1).readlines():
        pd=float(line.split()[1])*1e6
        x=-float(line.split()[3])/1000

        if pd>max:
            max=pd
            max_x=x
        lx.append([x,pd])
        if x>-3 and x<3:
            sum_x+=pd
            n_x+=1

    ly=[]
    sum_y=0
    n_y=0
    max=0
    max_y=0
    for line in open(file2).readlines():
        pd=float(line.split()[1])*1e6
        y=-float(line.split()[4])/5000

        if pd>max:
            max=pd
            max_y=y
        ly.append([y,pd])
        if y>-3 and y<3:
            sum_y+=pd
            n_y+=1

    ave_x=sum_x/n_x
    ave_y=sum_y/n_y
    lx.sort()
    ly.sort()

    frac=0.5

    min1=10000
    min2=10000
    x1=0
    x2=0
    for item in lx:
        a=abs(item[1]-frac*ave_x)
        if item[0]<0:
            if a<min1:
                min1=a
                x1=item[0]
        else:
            if a<min2:
                min2=a
                x2=item[0]

    min1=10000
    min2=10000
    y1=0
    y2=0
    for item in ly:
        a=abs(item[1]-frac*ave_y)
        if item[0]<0:
            if a<min1:
                min1=a
                y1=item[0]
        else:
            if a<min2:
                min2=a
                y2=item[0]

    x0=(x1+x2)/2
    y0=(y1+y2)/2

    print "max_x:%s, max_y:%s" % (max_x,max_y)
    print "x1=%s, x2=%s, x0=%s" % (x1,x2,x0)
    print "y1=%s, y2=%s, y0=%s" % (y1,y2,y0)
    print "Laser Position: (%s, %s)" % (-x0, -y0)

