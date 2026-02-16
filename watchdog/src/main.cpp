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
#include <gpiod.h>

#define DAEMON_NAME "RFNWatchdogDaemon"
#define SOFTWARE_VERSION	"1.0.0.0"
#define WD_GPIO 0 // Watchdog GPIO - GPIO 0

using namespace std;

pthread_t wd_thread;
enum gpiod_line_value value = GPIOD_LINE_VALUE_INACTIVE;
struct gpiod_line_request *request;
volatile bool is_running = true;

void sig_term_handler(int signal) {
	if (signal == SIGTERM)
	    is_running = false;
}

void *WDThread(void *t) {
	syslog (LOG_NOTICE, "Started...");
	while(is_running) {
		try {
			//syslog (LOG_NOTICE, "Reset GPIO...");
			value = (value == GPIOD_LINE_VALUE_ACTIVE) ? GPIOD_LINE_VALUE_INACTIVE :
						    GPIOD_LINE_VALUE_ACTIVE;
			gpiod_line_request_set_value(request, WD_GPIO, value);		
			sleep(1);
		} catch (exception &ex) {
			syslog (LOG_NOTICE, "Exception: %s", ex.what());
		}
	}
	pthread_exit(NULL);
}

static struct gpiod_line_request *
request_output_line(const char *chip_path, unsigned int offset,
		    enum gpiod_line_value value, const char *consumer)
{
	struct gpiod_request_config *req_cfg = NULL;
	struct gpiod_line_request *request = NULL;
	struct gpiod_line_settings *settings;
	struct gpiod_line_config *line_cfg;
	struct gpiod_chip *chip;
	int ret;

	chip = gpiod_chip_open(chip_path);
	if (!chip)
		return NULL;

	settings = gpiod_line_settings_new();
	if (!settings)
		goto close_chip;

	gpiod_line_settings_set_direction(settings,
					  GPIOD_LINE_DIRECTION_OUTPUT);
	gpiod_line_settings_set_output_value(settings, value);

	line_cfg = gpiod_line_config_new();
	if (!line_cfg)
		goto free_settings;

	ret = gpiod_line_config_add_line_settings(line_cfg, &offset, 1,
						  settings);
	if (ret)
		goto free_line_config;

	if (consumer) {
		req_cfg = gpiod_request_config_new();
		if (!req_cfg)
			goto free_line_config;

		gpiod_request_config_set_consumer(req_cfg, consumer);
	}

	request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

	gpiod_request_config_free(req_cfg);

free_line_config:
	gpiod_line_config_free(line_cfg);

free_settings:
	gpiod_line_settings_free(settings);

close_chip:
	gpiod_chip_close(chip);

	return request;
}

static int reconfigure_as_input_line(struct gpiod_line_request *request,
				      unsigned int offset)
{
	struct gpiod_request_config *req_cfg = NULL;
	struct gpiod_line_settings *settings;
	struct gpiod_line_config *line_cfg;
	int ret = -1;

	settings = gpiod_line_settings_new();
	if (!settings)
		return -1;

	gpiod_line_settings_set_direction(settings,
					  GPIOD_LINE_DIRECTION_INPUT);

	line_cfg = gpiod_line_config_new();
	if (!line_cfg)
		goto free_settings;

	ret = gpiod_line_config_add_line_settings(line_cfg, &offset, 1,
						  settings);
	if (ret)
		goto free_line_config;

	ret = gpiod_line_request_reconfigure_lines(request, line_cfg);

	gpiod_request_config_free(req_cfg);

free_line_config:
	gpiod_line_config_free(line_cfg);

free_settings:
	gpiod_line_settings_free(settings);

	return ret;
}

int main() {
	static const char *const chip_path = "/dev/gpiochip0";
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
	request = request_output_line(chip_path, WD_GPIO, value,
				      "toggle-line-value");
	 if (!request) {
		syslog(LOG_ERR, "Failed to request line: %s!!!", strerror(errno));
		return EXIT_FAILURE;
	}

	syslog(LOG_NOTICE, "Starting RFN Watchdog Daemon (version:%s)", SOFTWARE_VERSION);

	signal(SIGTERM, sig_term_handler);

	// Create watchdog thread
	if (pthread_create(&wd_thread, NULL, WDThread, (void *)NULL)) {
		syslog(LOG_ERR, "Can't create watchdog thread!!!");
		return -1;
	}

	// Wait threads to finish
	pthread_join(wd_thread, &status);

	reconfigure_as_input_line(request, WD_GPIO);
	gpiod_line_request_release(request);
	syslog(LOG_NOTICE, "RFN Watchdog Daemon stopped.");
	//Close the log
	closelog ();
	return 0;
}
