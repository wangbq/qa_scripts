import math,os,sys
import numpy as np
import matplotlib.pyplot as plt

def sqsum(v):
    s=0.0
    for it in v:
        s=s+it*it
    return math.sqrt(s)

if len(sys.argv)<2:
    print "./ST.py data.txt"
    sys.exit(1)

filename=sys.argv[1]
n=0
mainpd=[]
refpd=[]
#files: 140219-1.txt 140220-1.txt 140220-4.txt
for line in open(filename).readlines():
    if line[0]=='#':
        continue
    #print line
    if n%5==0:
        mainpd.append([])
        refpd.append([])
    mainpd[-1].append(float(line.strip().split()[1]))
    refpd[-1].append(float(line.strip().split()[2]))
    n=n+1
print len(mainpd)

main_mean=[np.mean(item) for item in mainpd]
main_std=[np.std(item) for item in mainpd]
ref_mean=[np.mean(item) for item in refpd]
ref_std=[np.std(item) for item in refpd]
ratio=[main_mean[i]/ref_mean[i] for i in xrange(len(main_mean))]
ratio_err=[sqsum([main_std[i]/main_mean[i],ref_std[i]/ref_mean[i]])*ratio[i] for i in xrange(len(main_mean))]
x=[i*1 for i in xrange(len(ratio))]

f0,ax0 = plt.subplots()
f0.set_size_inches(8,6)
ax0.errorbar(x,map(lambda x:x*1e6,main_mean),yerr=map(lambda x:x*1e6, main_std),fmt='o')

f1,ax1 = plt.subplots()
f1.set_size_inches(8,6)
ax1.errorbar(x,map(lambda x:x*1e6,ref_mean),yerr=map(lambda x:x*1e6, ref_std),fmt='o')

f2,ax2 = plt.subplots()
f2.set_size_inches(16,12)
ax2.set_xlabel("Time [min]",fontsize=14,fontweight="bold")
ax2.set_ylabel("MainPD/RefPD",fontsize=14,fontweight="bold")
for tick in ax2.xaxis.get_major_ticks():
    tick.label1.set_fontsize(14)
for tick in ax2.yaxis.get_major_ticks():
    tick.label1.set_fontsize(14)
ax2.errorbar(x,ratio,ratio_err,fmt='o',linewidth=3)

print "main pd:"
print np.mean(main_mean),np.std(main_mean),np.std(main_mean)/np.mean(main_mean)
print max(main_mean),min(main_mean),(max(main_mean)-min(main_mean))/min(main_mean)
print "ref pd:"
print np.mean(ref_mean),np.std(ref_mean),np.std(ref_mean)/np.mean(ref_mean)
print max(ref_mean),min(ref_mean),(max(ref_mean)-min(ref_mean))/min(ref_mean)
print "ratio:"
print np.mean(ratio),np.std(ratio),np.std(ratio)/np.mean(ratio)
print max(ratio),min(ratio),(max(ratio)-min(ratio))/min(ratio)

f2.show()

raw_input()

if len(sys.argv)==3:
    plt.savefig(sys.argv[2])

