import math,os,sys
import numpy as np
import matplotlib.pyplot as plt
import argparse

def sqsum(v):
    return reduce(lambda x,y:math.sqrt(x*x+y*y),v)

def calc_rat_err(v_m,v_r):
    m=np.mean(v_m)
    r=np.mean(v_r)
    cov=np.cov(np.vstack((v_m,v_r)))
    sm=math.sqrt(cov[0][0])
    sr=math.sqrt(cov[1][1])
    rm=sm/m
    rr=sr/r
    rho=cov[0][1]/(sm*sr)
    rat=m/r
    rat_err=math.sqrt(rm*rm + rr*rr - 2*rm*rr*rho)*rat
    return [rat, rat_err]

class DataPoint:
    def __init__(self, repeat):
        self.raw_data_lines=[]
        self.repeat=repeat
        self.mpd=[]
        self.rpd=[]
        self.ratio=[]
        self.laser=None

    def add_line(self, line):
        self.raw_data_lines.append(line)

    def process(self, filter_func=None):
        if len(self.raw_data_lines) != self.repeat:
            print "number of raw data is wrong: ", len(self.raw_data_lines)
        for line in self.raw_data_lines:
            lp=line.strip().split()
            self.mpd.append(float(lp[1]))
            self.rpd.append(float(lp[2]))
            self.ratio.append(self.mpd[-1]/self.rpd[-1])
            pos=(int(lp[5]),int(lp[6]))
            if self.laser==None:
                self.laser=pos
            else:
                if self.laser!=pos:
                    print "wrong laser position"
        if filter_func!=None:
            filter_func(self.mpd, self.rpd, self.ratio)
        self.main_mean=np.mean(self.mpd)
        self.main_rms=np.std(self.mpd)
        self.ref_mean=np.mean(self.rpd)
        self.ref_rms=np.std(self.rpd)
        self.ratio_mean=np.mean(self.ratio)
        self.ratio_rms=np.std(self.ratio)
        [self.rat, self.rat_err]=calc_rat_err(self.mpd,self.rpd)
        self.n=len(self.ratio)

class Experiment:
    def __init__(self, filename, **kwargs):
        self.filename=filename
        self.bar_no=os.path.abspath(filename).split('/')[-2]
        datalines=open(self.filename).readlines()

        for line in datalines:
            p=line.strip().split()
            if p[0][0]!="#":
                continue
            if p[0][-1]!=':':
                continue
            if len(p)!=2:
                continue
            name=p[0][1:-1]
            value=p[1]
            if name=="degree":
                self.degree=int(value)
            if name=="minute":
                self.minute=int(value)
            if name=='bounce':
                self.bounce=int(value)
            if name=='bulk':
                self.bulk=float(value)

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

        self.data_points=[]
        n=0
        for line in datalines:
            if line.strip()[0]=='#':
                continue
            if n%self.repeat_read==0:
                self.data_points.append(DataPoint(self.repeat_read))
            self.data_points[-1].add_line(line)
            n=n+1
        [item.process() for item in self.data_points]
        if n%self.repeat_read!=0:
            print "number of data lines is wrong: %s" % n

    def calc_RR(self): 
        self.angle1=(self.degree+1.0*self.minute/60)*math.pi/180
        self.angle2=math.asin(self.n1/self.n2*math.sin(self.angle1))
        self.Rs1=math.pow((self.n1*math.cos(self.angle1)-self.n2*math.cos(self.angle2))/(self.n1*math.cos(self.angle1)+self.n2*math.cos(self.angle2)),2)
        self.Rp1=math.pow((self.n1*math.cos(self.angle2)-self.n2*math.cos(self.angle1))/(self.n1*math.cos(self.angle2)+self.n2*math.cos(self.angle1)),2)
        self.RR=self.f_s*(1-self.Rs1)*(1-self.Rs1)+(1-self.f_s)*(1-self.Rp1)*(1-self.Rp1)
        self.L=self.L0/math.cos(self.angle2)

    def analyze(self):
        self.calc_RR()
        if self.scan_type=='bt':
            self.bt_ana()
        elif self.scan_type=='ir':
            self.ir_ana()
        else:
            print "wrong scan type!"
            sys.exit(1)

    def bt_ana(self):
        self.plot_lines=[[] for j in xrange(self.rows-1)]
        self.plot_lines_err=[[] for j in xrange(self.rows-1)]
        for i in xrange(len(self.data_points)):
            if i%self.rows==0:
                continue
            dp=self.data_points[i]
            dp0=self.data_points[i/self.rows*self.rows]
            bt=math.pow(dp.rat/dp0.rat/self.RR,1.0/self.L)
            bt_err=sqsum([dp.rat_err/dp.rat, dp0.rat_err/dp0.rat, 0.0003])/self.L*bt
            dp.bt=bt
            dp.bt_err=bt_err
            self.plot_lines[i%self.rows-1].append(bt*100)
            self.plot_lines_err[i%self.rows-1].append(bt_err*100)
        self.bt_result=[item.bt for item in self.data_points if hasattr(item,'bt')]
        self.bt_result_filter=[item for item in self.bt_result if item>0.99]
    
    def ir_ana(self):
        self.plot_lines=[[] for j in xrange(self.rows)]
        self.plot_lines_err=[[] for j in xrange(self.rows)]
        dp0=self.data_points[0]
        points=self.data_points[1:]
        for i in xrange(len(points)):
            dp=points[i]
            ir=math.pow(dp.rat/dp0.rat/self.RR/math.pow(self.bulk,self.L),1.0/self.bounce)
            ir_err=sqsum([dp.rat_err/dp.rat, dp0.rat_err/dp0.rat, 0.0003])/(1.0*self.bounce)*ir
            corr=(1-math.sqrt(self.RR))**2*math.pow(self.bulk,2*self.L)*math.pow(ir,2*self.bounce)/self.bounce
            dp.ir=ir-corr
            dp.ir_err=ir_err
            dp.corr=corr
            self.plot_lines[i%self.rows].append((ir-corr)*100)
            self.plot_lines_err[i%self.rows].append(ir_err*100)
        self.ir_result=[item.ir for item in self.data_points if hasattr(item,'ir')]
        self.ir_result_filter=[item for item in self.ir_result if item>0.9990]

    def report(self):
        print "scan type: ", self.scan_type
        print "total number of points: ", len(self.data_points)
        print "incident angle: ", self.degree, 'd', self.minute,'m'
        print "L0: ", self.L0
        print "L: ", self.L
        print "RR: ", self.RR
        if self.scan_type=='bt':
            print "BT: ", np.mean(self.bt_result), ", RMS: ",np.std(self.bt_result)
            print "after filter (bt > 99.0%):"
            print "number of points: ", len(self.bt_result_filter)
            print "BT: ", np.mean(self.bt_result_filter), ", RMS: ", np.std(self.bt_result_filter)
        elif self.scan_type=='ir':
            print "bounce: ", self.bounce
            print "reflection angle: ", 90-self.angle2/math.pi*180
            print "bulk: ", self.bulk
            print "IR: ", np.mean(self.ir_result), ", RMS: ",np.std(self.ir_result)
            print "after filter (ir > 99.90%):"
            print "number of points: ", len(self.ir_result_filter)
            print "IR: ", np.mean(self.ir_result_filter), ", RMS: ", np.std(self.ir_result_filter)

    def plot(self):
        f0,ax0 = plt.subplots()
        f0.set_size_inches(16,12)
        for tick in ax0.xaxis.get_major_ticks():
            tick.label1.set_fontsize(14)
        for tick in ax0.yaxis.get_major_ticks():
            tick.label1.set_fontsize(14)
        [i.set_linewidth(3) for i in ax0.spines.itervalues()]

        if self.scan_type=='bt':
            ax0.set_ylim([99,100])
            ax0.set_xlim([0,30])
            ax0.set_title("Bar No. = %s, Bulk Transmittance = (%.2f +- %.2f) %%/m" % (self.bar_no, 100*np.mean(self.bt_result_filter),100*np.std(self.bt_result_filter)),fontsize=14,fontweight="bold")
            ax0.set_xlabel("Distance [cm]",fontsize=14,fontweight="bold")
            ax0.set_ylabel("BT [%/m]",fontsize=14,fontweight="bold")
        elif self.scan_type=='ir':
            ax0.set_ylim([99.90,100.02])
            ax0.set_xlim([0,30])
            ax0.set_title("Bar No. = %s, Internal Reflectivity = (%.3f +- %.3f) %% for N = %s" % (self.bar_no, 100*np.mean(self.ir_result_filter),100*np.std(self.ir_result_filter), self.bounce),fontsize=14,fontweight="bold")
            ax0.set_xlabel("Distance [cm]",fontsize=14,fontweight="bold")
            ax0.set_ylabel("IR [%/m]",fontsize=14,fontweight="bold")

        plot_list=[]
        title_list=[]
        x=[i*self.step_x for i in xrange(len(self.plot_lines[0]))]
        for i in xrange(len(self.plot_lines)):
            line=self.plot_lines[i]
            line_err=self.plot_lines_err[i]
            plot=ax0.errorbar(x,line,yerr=line_err,fmt='o',linewidth=3)
            plot_list.append(plot[0])
            title_list.append("line%s" % (i+1))

        plt.legend(plot_list,title_list,fontsize=14)
        if self.quiet==False:
            f0.show()

        if self.output!=None:
            f0.savefig(self.output)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Process data files.')
    parser.add_argument('filename', type=str, help='input filename')
    parser.add_argument('-t','--type',metavar='type', dest='type', type=str, required=True,help='analysis type')
    parser.add_argument('-o','--output',metavar='output', dest='output', type=str, help='analysis type')
    parser.add_argument('-q','--quiet', dest='quiet',action='store_true',help='quiet mode')

    args = parser.parse_args()

    if args.type == 'bt':
        exp=Experiment(filename=args.filename,scan_type='bt',n1=1.00,n2=1.47,L0=1.25,f_s=0.5,repeat_read=10,rows=5,step_x=0.5,step_y=0.4,output=args.output,quiet=args.quiet)
    elif args.type == 'ir':
        exp=Experiment(filename=args.filename,scan_type='ir',n1=1.00,n2=1.47,L0=1.25,f_s=1.0,repeat_read=10,rows=4,step_x=0.5,step_y=0.4,output=args.output,quiet=args.quiet)

    exp.analyze()
    exp.plot()
    if args.quiet==False:
        exp.report()
        raw_input()

