#include <iostream>
#include <pthread.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <syslog.h>
#include <algorithm>
#include <string>
#include <string.h>
#include <signal.h>
#include "GPIO.h"

#define DAEMON_NAME "RFNWatchdogDaemon"
#define SOFTWARE_VERSION	"1.0.0.0"
#define WD_GPIO 0 // Watchdog GPIO - GPIO 0

using namespace std;

pthread_t wd_thread;
GPIO *wdgpio;
volatile bool is_running = true;

void sig_term_handler(int signal) {
	if (signal == SIGTERM)
	    is_running = false;
}

void *WDThread(void *t) {
	bool val = true;
	syslog (LOG_NOTICE, "Started...");
	while(is_running) {
		try {
			//syslog (LOG_NOTICE, "Reset GPIO...");
			wdgpio->Value((val)? GPIO_HIGH : GPIO_LOW);
			val = !val;
			sleep(1);
		} catch (exception &ex) {
			syslog (LOG_NOTICE, "Exception: %s", ex.what());
		}
	}
	pthread_exit(NULL);
}

int main() {
	void *status;

	//Set our Logging Mask and open the Log
	setlogmask(LOG_UPTO(LOG_NOTICE));
	openlog(DAEMON_NAME, LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);

	pid_t pid, sid;

	//Fork the Parent Process
	pid = fork();

	if (pid < 0) { exit(EXIT_FAILURE); }

	//We got a good pid, Close the Parent Process
	if (pid > 0) { exit(EXIT_SUCCESS); }

	//Change File Mask
	umask(0);

	//Create a new Signature Id for our child
	sid = setsid();
	if (sid < 0) { exit(EXIT_FAILURE); }

	//Change Directory
	//If we cant find the directory we exit with failure.
	if ((chdir("/")) < 0) { exit(EXIT_FAILURE); }

	// Initialize watchdog GPIO
	wdgpio = new GPIO(WD_GPIO);
	wdgpio->Direction(GPIO_OUT);

	syslog(LOG_NOTICE, "Starting RFN Watchdog Daemon (version:%s)", SOFTWARE_VERSION);

	signal(SIGTERM, sig_term_handler);

	// Create network thread
	if (pthread_create(&wd_thread, NULL, WDThread, (void *)NULL)) {
		syslog(LOG_ERR, "Can't create network thread!!!");
		return -1;
	}

	// Wait threads to finish
	pthread_join(wd_thread, &status);

	wdgpio->Direction(GPIO_IN);
	wdgpio->~GPIO();
	syslog(LOG_NOTICE, "RFN Watchdog Daemon stopped.");
	//Close the log
	closelog ();
	return 0;
}


