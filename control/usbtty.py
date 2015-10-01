import os,sys,termios,select

class USBTTY:
    def __init__(self, device, termtype='PICODMM'):
        self.device = device
        self.termtype = termtype
        self.fd = os.open(device, os.O_RDWR | os.O_NDELAY)
        if (not os.isatty(self.fd)):
            close(self.fd)
            print "%s is not a tty" % device
            sys.exit(-1)
        ios = termios.tcgetattr(self.fd)
        ios[0] = ios[0] & 0
        ios[1] = ios[1] & 0
        ios[2] = ios[2] & 0
        ios[2] = ios[2] | termios.CS8
        if (termtype=='STAGE'):
            ios[2] = ios[2] | termios.CRTSCTS
        ios[2] = ios[2] | termios.CLOCAL
        ios[2] = ios[2] | termios.CREAD
        ios[3] = ios[3] & 0
        ios[4] = termios.B9600
        ios[5] = termios.B9600
        ios[6][termios.VMIN] = 0
        ios[6][termios.VTIME] = 30
        termios.tcsetattr(self.fd, termios.TCSANOW, ios)

    def close232(self):
        os.close(self.fd)

    def send232(self, command):
        r,w,e = select.select([],[self.fd],[])
        if self.fd not in w:
            print "select error!"
            sys.exit(-1)
        os.write(self.fd, command+'\r\n')

    def recv232(self):
        buf=''
        while True:
            r,w,e = select.select([self.fd],[],[])
            if self.fd not in r:
                print "select error!"
                sys.exit(-1)
            rbuf = os.read(self.fd, 128)
            buf = buf + rbuf
            if (len(buf)>2 and buf[-2:]=='\r\n'):
                break
        return buf[:-2]

    def ready(self):
        while True:
            self.send232('!:')
            buf = self.recv232()
            if (buf[0]=='R'):
                break

    def status(self):
        self.send232('Q:')
        buf = self.recv232()
        return buf

    def move_stage(self, pulses=[0,0,0,0]):
        cmd = 'M:W'
        for i in xrange(4):
            if (pulses[i]>=0):
                cmd = cmd + '+P'
            elif (pulses[i]<0):
                cmd = cmd + '-P'
            cmd = cmd + ('%d' % abs(pulses[i]))
        self.send232(cmd)
        if (self.recv232() != 'OK'):
            print 'error sending command %s' % cmd
            sys.exit(-1)
        self.send232('G:')
        if (self.recv232() != 'OK'):
            print 'error sending command G:'
            sys.exit(-1)
        self.ready()

    def read_pico(self):
        self.send232("FORM:ELEM READ")
        self.send232("TRIG:COUN 5")
        self.send232("TRAC:POIN 5")
        self.send232("SENS:CURR:NPLC 1.0")
        self.send232("TRAC:FEED SENS")
        self.send232("TRAC:FEED:CONT NEXT")
        self.send232("INIT")
        self.send232("CALC3:FORM MEAN")
        self.send232("CALC3:DATA?")
        buf = self.recv232()
        return buf

    def read_dmm(self):
        self.send232("CONF:CURR:DC DEF")
        self.send232("SAMP:COUN 5")
        self.send232("TRIG:SOUR BUS")
        self.send232("SENS:CURR:NPLC 1.0")
        self.send232("CALC:FUNC AVER")
        self.send232("CALC:STAT ON")
        self.send232("INIT")
        self.send232("*TRG")
        self.send232("CALC:AVER:AVER?")
        buf = self.recv232()
        return buf
