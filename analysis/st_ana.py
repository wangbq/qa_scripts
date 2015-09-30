import math,os,sys
import numpy as np
import matplotlib.pyplot as plt
import argparse

def sqsum(v):
    return reduce(lambda x,y:math.sqrt(x*x+y*y),v)

parser = argparse.ArgumentParser(description='Process stability files.')
parser.add_argument('filename', type=str, help='input filename')
parser.add_argument('-o','--output',metavar='output', dest='output', type=str, help='save output image')
args = parser.parse_args()

n=0
mainpd=[]
refpd=[]
for line in open(args.filename).readlines():
    if line[0]=='#':
        continue
    if line.strip()=='':
        continue
    if n%5==0:
        mainpd.append([])
        refpd.append([])
    mainpd[-1].append(float(line.strip().split()[1]))
    refpd[-1].append(float(line.strip().split()[2]))
    n=n+1
print "Total number of data points: ", len(mainpd)

main_mean=[np.mean(item) for item in mainpd]
main_std=[np.std(item) for item in mainpd]
ref_mean=[np.mean(item) for item in refpd]
ref_std=[np.std(item) for item in refpd]
ratio=[main_mean[i]/ref_mean[i] for i in xrange(len(main_mean))]
ratio_err=[sqsum([main_std[i]/main_mean[i],ref_std[i]/ref_mean[i]])*ratio[i] for i in xrange(len(main_mean))]
x=[i*1 for i in xrange(len(ratio))]

f,(ax0,ax1,ax2) = plt.subplots(3,sharex=True)
f.set_size_inches(8,6)

ax0.set_title("MainPD",fontsize=14,fontweight="bold")
ax0.set_ylabel("MainPD [uA]",fontsize=14,fontweight="bold")
ax1.set_title("RefPD",fontsize=14,fontweight="bold")
ax1.set_ylabel("RefPD [uA]",fontsize=14,fontweight="bold")
ax2.set_title("MainPD / RefPD",fontsize=14,fontweight="bold")
ax2.set_ylabel("Ratio",fontsize=14,fontweight="bold")
ax2.set_xlabel("Time [min]",fontsize=14,fontweight="bold")

ax0.errorbar(x,map(lambda x:x*1e6,main_mean),yerr=map(lambda x:x*1e6, main_std),fmt='o')
ax1.errorbar(x,map(lambda x:x*1e6,ref_mean),yerr=map(lambda x:x*1e6, ref_std),fmt='o')
ax2.errorbar(x,ratio,ratio_err,fmt='o',linewidth=3)

print "main pd:"
print "mean: ",np.mean(main_mean),", err: ",np.std(main_mean), ", relative err: ",np.std(main_mean)/np.mean(main_mean)*100," %"
print "max: ",max(main_mean),", min: ",min(main_mean),", (max-min)/min: ", (max(main_mean)-min(main_mean))/min(main_mean)*100, "%"

print "ref pd:"
print "mean: ",np.mean(ref_mean),", err: ",np.std(ref_mean), ", relative err: ",np.std(ref_mean)/np.mean(ref_mean)*100," %"
print "max: ",max(ref_mean),", min: ",min(ref_mean),", (max-min)/min: ", (max(ref_mean)-min(ref_mean))/min(ref_mean)*100, "%"

print "ratio:"
print "mean: ",np.mean(ratio),", err: ",np.std(ratio), ", relative err: ",np.std(ratio)/np.mean(ratio)*100," %"
print "max: ",max(ratio),", min: ",min(ratio),", (max-min)/min: ", (max(ratio)-min(ratio))/min(ratio)*100, "%"

f.show()

raw_input()

if args.output!=None:
    plt.savefig(args.output)

