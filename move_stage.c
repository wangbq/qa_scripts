#include<termios.h>
#include<fcntl.h>
#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int Open232C0(char* tty){
	int fd0;
	int t;
	
	struct termios ios;

	if((fd0 = open(tty, O_RDWR|O_NDELAY))== -1){
		printf("can not open %s\n", tty);
		exit(-1);
	}

	if(!isatty(fd0)){
		close(fd0);
		printf("%s is not a tty\n", tty);
		exit(-1);
	}
	
	if(tcgetattr(fd0,&ios) < 0){
		close(fd0);
		printf("Error: tcgetattr\n");
		exit(-1);
	}

	ios.c_iflag &= 0; // input mode flag
	ios.c_oflag &= 0; // output mode flag
	ios.c_cflag &= 0; // control mode flag
	ios.c_cflag |= CS8;
	ios.c_cflag |= CRTSCTS;
	ios.c_cflag |= CLOCAL;
	ios.c_cflag |= CREAD;
	ios.c_lflag &= 0; // local mode flag
	ios.c_cc[VMIN] = 0;
	ios.c_cc[VTIME] = 30;

	cfsetispeed(&ios,B9600);
	cfsetospeed(&ios,B9600);

	if(tcsetattr(fd0,TCSANOW,&ios)<0){
		close(fd0);
		printf("Error: tcsetattr\n");
		exit(-1);
	}
	return fd0;
}

int Close232C0(int fd0){
	close(fd0);
	return 0;
}

int Send232C0(int fd0, char* command){
	char sbuf[128]="";
	strcpy(sbuf,command);
	strcat(sbuf,"\r\n");
	int nbuf=strlen(sbuf);

	int nout = 0;
	while((unsigned int)nout < nbuf){
		const int nbytes = write(fd0, sbuf+nout, strlen(sbuf+nout));
		if(nbytes < 0){
			printf("Writing failed.\n");
			break;
		}
		nout += nbytes;
	}

	return nbuf;
}

int Recv232C0(int fd0,int t_sleep){
	char buf[128] = "";
	char rbuf[128] = "";

	int i,n;

	int nloop = 0;
	while(1){
		nloop++;
		n = read(fd0,buf,128);
		if(n != -1 && n > 2){
			for(i=0;i < n-2;i++)
                rbuf[i] = buf[i];
			break;
		}else if(nloop%50000 == 0)
			printf(".");
		usleep(t_sleep);
	}

	return n;
}

int Recvr232C0(int fd0,char *l,int t_sleep){
	char nbuf[128]="";
	char nrbuf[128]="";

	int ni,nn=0,nloop=0;
	while(1){
		nloop++;
		nn = read(fd0,nbuf,128);
		if(nn!=-1 && nn > 2){
			for(ni=0;ni < nn-2;ni++)
                nrbuf[ni] = nbuf[ni];
			break;
		}else if(nloop%50000 == 0)
			printf(".");
		usleep(t_sleep);
	}

	strcpy(l,nrbuf);
	return nn;
}

int Check232C0(int fd0,int t_sleep){
	char buf[128]="";

	while(buf[0] != 'R'){
		Send232C0(fd0,"!:");
		Recvr232C0(fd0,buf,t_sleep);
	}
	return 0;
}

int Move232C0(int fd0,char* command,int t_sleep){
	Send232C0(fd0,command);
	Recv232C0(fd0,t_sleep);

	Send232C0(fd0,"G:");
	Recv232C0(fd0,t_sleep);

	Check232C0(fd0,t_sleep);
	Close232C0(fd0);
	return 0;
}
	
int main(int argc ,char *argv[]){
    if (argc!=3 && argc!=5 && argc!=7 && argc!=9) {
        printf("usage: \n");
        exit(1);
    }
    int pulses[4]={0,0,0,0};
    int mode=atoi(argv[1])-1;
    int plnum=atoi(argv[2]);
    pulses[mode]=plnum;
    if (argc>=5) {
        mode=atoi(argv[3])-1;
        plnum=atoi(argv[4]);
        pulses[mode]=plnum;
    }
    if (argc>=7) {
        mode=atoi(argv[5])-1;
        plnum=atoi(argv[6]);
        pulses[mode]=plnum;
    }
    if (argc>=9) {
        mode=atoi(argv[7])-1;
        plnum=atoi(argv[8]);
        pulses[mode]=plnum;
    }
    char cmd[128]="";
    strcpy(cmd,"M:W");
    int i;
    for (i=0;i<4;i++) {
        if (pulses[i]>=0)
            strcat(cmd,"+P");
        else
            strcat(cmd,"-P");
        char t[32]="";
        sprintf(t,"%d",abs(pulses[i]));
        strcat(cmd,t);
    }

	int tmp = Open232C0("/dev/ttyUSB2");
	Move232C0(tmp,cmd,100000);
	
	return 0;
}

