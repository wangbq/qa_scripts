import os,sys,termios,time

class USBTTY:
    def __init__(self, device, termtype='PICODMM'):
        self.device = device
        self.termtype = termtype
        self.fd = open(device, os.O_RDWR | O_NDELAY)
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
        close(self.fd)

    def send232(self, command):
        self.fd.write(command+'\r\n')

    def recv232(self):
        buf = ''
        while True:
            rbuf = self.fd.read(128)
            if (len(rbuf)!=0 and len(rbuf)>2):
                buf = buf + rbuf[:-2]
                break
            time.sleep(0.1)
        return buf

    def check232(self):
        self.send232('!:')
        buf = self.recv232()
        if (buf[0]=='R'):
            return True
        else:
            return False

    def move_stage(self, pulses=[0,0,0,0]):
        cmd = 'M:W'
        for i in xrange(4):
            if (pulses[i]>=0):
                cmd = cmd + '+P'
            elif (pulses[i]<0):
                cmd = cmd + '-P'
            cmd = cmd + ('%d' % abs(pulse[i]))
        self.send232(cmd)
        self.recv232()
        self.send232('G:')
        self.recv232()
        self.check232()

    def read_pico(self):
        self.send232("FORM:ELEM READ")
        self.send232("TRIG:COUN 5")
        self.send232("TRAC:POIN 5")
        self.send232("SENS:CURR:NPLC 1.0")
        self.send232("TRAC:FEED SENS")
        self.send232("TRAC:FEED:CONT NEXT")
        time.sleep(0.2)
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
        time.sleep(0.2)
        self.send232("*TRG")
        self.send232("CALC:AVER:AVER?")
        buf = self.recv232()
        return buf
