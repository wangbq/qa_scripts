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
        buf=''
        while True:
            rbuf = self.fd.read(128)
            if (len(rbuf)!=0 and len(rbuf)>2):
                buf = buf + rbuf[:-2]
                break
            time.sleep(0.1)
        return buf
