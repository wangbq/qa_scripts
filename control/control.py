#!/usr/bin/python
import os,sys,time,re
import usbtty

max_read=1e-3

pico=usbtty.PICO("/dev/ttyUSB0")
dmm=usbtty.DMM("/dev/ttyUSB1")
stage=usbtty.STAGE("/dev/ttyUSB2")

global_lr=[0,0]
global_pd=[0,0]

#all steps in micrometer (um)
def move_lr(x,y):
    stage.move_stage([x,y,0,0])
    global_lr[0]+=x
    global_lr[1]+=y

def move_pd(x,y):
    stage.move_stage([0,0,x,y])
    global_pd[0]+=x
    global_pd[1]+=y

def move_all(x):
    stage.move_stage(x)
    global_lr[0]+=x[0]
    global_lr[1]+=x[1]
    global_pd[0]+=x[2]
    global_pd[1]+=x[3]

def read_pico():
    r=pico.read().strip()
    if re.match("\+\d\.\d+E-\d\d",r) and float(r)<max_read:
        return r
    else:
        print "read_pico failed!"
        sys.exit(-1)

def read_dmm():
    r=dmm.read().strip()
    if re.match("\+\d\.\d+E-\d\d",r) and float(r)<max_read:
        return r
    else:
        print "read_dmm failed!"
        sys.exit(-1)

def read_time_pico_dmm():
    p=read_pico()
    d=read_dmm()
    t=time.strftime('%H:%M:%S',time.localtime(time.time()))
    return [t,p,d]
    
def find_laser(steps=[(100, 500), (10, 50)], prev_move=(0,0,0,0)):
    ini_pos=(global_pd[0],global_pd[1])
    frac=0.5
    min_read=100e-6

    ini_pd=float(read_pico())
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
    r=float(read_pico())
    print "pd: (%s,%s) r: %s" % (global_pd[0],global_pd[1],r*1e6)
    d=r-edge_read
    if axis==0:#x axis
        v=[phase*cmp(d,0), 0]
    elif axis==1:#y axis
        v=[0, phase*cmp(d,0)]
    prev=[global_pd[0], global_pd[1], d]
    while True:
        move_pd(v[0]*step[0],v[1]*step[1])
        r=float(read_pico())
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

