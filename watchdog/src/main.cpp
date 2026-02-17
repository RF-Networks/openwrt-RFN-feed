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
#define SOFTWARE_VERSION "1.0.0.0"
#define WD_GPIO 0 

using namespace std;

pthread_t wd_thread;
struct gpiod_line *wd_line = NULL;
struct gpiod_chip *chip = NULL;
int current_value = 0;
volatile bool is_running = true;

void sig_term_handler(int signal) {
    if (signal == SIGTERM)
        is_running = false;
}

void *WDThread(void *t) {
    syslog(LOG_NOTICE, "Watchdog thread started...");
    while(is_running) {
        // Toggle value
        current_value = !current_value;
        if (gpiod_line_set_value(wd_line, current_value) < 0) {
            syslog(LOG_ERR, "Failed to set GPIO value: %s", strerror(errno));
        }
        sleep(1);
    }
    pthread_exit(NULL);
}

int main() {
    static const char *const chip_path = "/dev/gpiochip0";
    
    setlogmask(LOG_UPTO(LOG_NOTICE));
    openlog(DAEMON_NAME, LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);

    // Daemonize
    pid_t pid = fork();
    if (pid < 0) exit(EXIT_FAILURE);
    if (pid > 0) exit(EXIT_SUCCESS);
    umask(0);
    if (setsid() < 0) exit(EXIT_FAILURE);
    if ((chdir("/")) < 0) exit(EXIT_FAILURE);

    // libgpiod v1.6.3 Logic
    chip = gpiod_chip_open(chip_path);
    if (!chip) {
        syslog(LOG_ERR, "Failed to open chip: %s", strerror(errno));
        return EXIT_FAILURE;
    }

    wd_line = gpiod_chip_get_line(chip, WD_GPIO);
    if (!wd_line) {
        syslog(LOG_ERR, "Failed to get line: %s", strerror(errno));
        gpiod_chip_close(chip);
        return EXIT_FAILURE;
    }

    if (gpiod_line_request_output(wd_line, DAEMON_NAME, 0) < 0) {
        syslog(LOG_ERR, "Failed to request output: %s", strerror(errno));
        gpiod_chip_close(chip);
        return EXIT_FAILURE;
    }

    syslog(LOG_NOTICE, "Starting RFN Watchdog Daemon (version:%s)", SOFTWARE_VERSION);
    signal(SIGTERM, sig_term_handler);

    if (pthread_create(&wd_thread, NULL, WDThread, NULL)) {
        syslog(LOG_ERR, "Can't create watchdog thread!!!");
        return -1;
    }

    pthread_join(wd_thread, NULL);

    // Cleanup: Reconfigure to input and release
    gpiod_line_set_direction_input(wd_line);
    gpiod_line_release(wd_line);
    gpiod_chip_close(chip);

    syslog(LOG_NOTICE, "RFN Watchdog Daemon stopped.");
    closelog();
    return 0;
}