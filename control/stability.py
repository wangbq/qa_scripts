import control
import os,time

#time.sleep(120)

filename="" #output filename
hours=12 #number of hours
repeat=5 #number of repeats per measurement

f=open(filename,"a")
f.write("#---------------------------------------------------------------------------------\n")
f.write("#Stability test starts at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
f.write("#repeat: %s\n" % repeat)
for i in xrange(60*hours):
    for j in xrange(repeat):
        r=control.read_time_pico_dmm()
        print "%s %s %s" % (r[0],r[1],r[2])
        f.write("%s %s %s\n" % (r[0],r[1],r[2]))
        f.flush()
    time.sleep(54)

f.write("#Stability test stops at %s\n" % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
f.write("#---------------------------------------------------------------------------------\n")
f.close()

os.system("~/backup.sh")
