#!/usr/bin/python
import sys
import control

argc=len(sys.argv)
if argc != 3 and argc!=5 and argc!=7 and argc!=9:
    print "Wrong arguments!"
    sys.exit(-1)

pulses=[0,0,0,0]

pulses[int(sys.argv[1])-1]=int(sys.argv[2])
if (argc>=5):
    pulses[int(sys.argv[3])-1]=int(sys.argv[4])
if (argc>=7):
    pulses[int(sys.argv[5])-1]=int(sys.argv[6])
if (argc>=9):
    pulses[int(sys.argv[7])-1]=int(sys.argv[8])

print "pulses: ", pulses

control.initialize()
control.move_all(pulses)
control.finalize()
