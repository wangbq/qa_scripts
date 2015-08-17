#include<termios.h>
#include<fcntl.h>
#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<time.h>
#include<pthread.h>

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
	//ios.c_cflag |= CRTSCTS;
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

void* read_pico(void* ptr) {
  int tmp = Open232C0("/dev/ttyUSB0");
  // picoammeter setting //  
  Send232C0(tmp,"FORM:ELEM READ");
  Send232C0(tmp,"TRIG:COUN 5");
  Send232C0(tmp,"TRAC:POIN 5");
  Send232C0(tmp,"SENS:CURR:NPLC 1.0");
  Send232C0(tmp,"TRAC:FEED SENS");
  Send232C0(tmp,"TRAC:FEED:CONT NEXT");
  usleep(200000);//wait for finish to set up
  // measurement start //
  Send232C0(tmp,"INIT");
  // reading picoammeter //
  Send232C0(tmp,"CALC3:FORM MEAN");
  Send232C0(tmp,"CALC3:DATA?"); 
  char buff01[128];
  Recvr232C0(tmp,buff01,200000);
  strncpy((char*)ptr,buff01,strlen(buff01)+1);
  Close232C0(tmp);
}

void* read_dmm(void* ptr) {
  int tmp2 = Open232C0("/dev/ttyUSB1");
  // DMM setting //
  Send232C0(tmp2,"CONF:CURR:DC DEF");
  Send232C0(tmp2,"SAMP:COUN 5");
  Send232C0(tmp2,"TRIG:SOUR BUS");
  Send232C0(tmp2,"SENS:CURR:NPLC 1.0");
  Send232C0(tmp2,"CALC:FUNC AVER");
  Send232C0(tmp2,"CALC:STAT ON");
  Send232C0(tmp2,"INIT");
  usleep(200000);//wait for finish to set up
  Send232C0(tmp2,"*TRG");
  // reading DMM //
  Send232C0(tmp2,"CALC:AVER:AVER?");
  char buff02[128];
  Recvr232C0(tmp2,buff02,200000);
  strncpy((char*)ptr,buff02,strlen(buff02)+1);
  Close232C0(tmp2);
}

int main(int argc, char *argv[]){
  pthread_t thread1, thread2;
  char result1[128];
  char result2[128];
  int iret1,iret2;
  iret1=pthread_create(&thread1,NULL,read_pico,(void*)result1);
  iret2=pthread_create(&thread2,NULL,read_dmm,(void*)result2);
  pthread_join(thread1,NULL);
  pthread_join(thread2,NULL);
  //////////////////////
  /* Get Current Time */
  //////////////////////
  time_t now = time(NULL);
  struct tm *pnow = localtime(&now);
  char currtime[128] = "";
  sprintf(currtime,"%d:%d:%d",pnow->tm_hour,pnow->tm_min,pnow->tm_sec);
    
  printf("%s\t%s\t%s\n",currtime,result1,result2);
  
  return 0;
}
