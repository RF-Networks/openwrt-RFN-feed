#ifndef LRFFP_H_
#define LRFFP_H_

#define PACKAGE_STRING "lrffp 1.00.00"

#define VERSION_MSG \
    PACKAGE_STRING "\n" \
    "Copyright (C) 2016 RF Networks\n" \
    "All rights reserved.\n\n"

#define HELP_MSG \
    "\n" \
    "Usage: lrffp <stream name> <serial port> <options>\n" \
    "\n" \
    "--verbose: enable verbose output\n" \
    "--version, -v: print version\n" \
    "--device, -d: choose device\n" \
    "\t 1 - RFN\n" \
    "\t 2 - Mesh\n" \
	"\t 3 - Star\n" \
	"--speed, -s: choose serial port speed\n" \
    "\t 1 - 19200\n" \
    "\t 2 - 115200\n" \
    "--enterbootloader, -b: enter device to bootloader mode\n" \

#define DEVICE_TAG_READER_ROUTER_SELECTION      '1'
#define DEVICE_COORDINATOR_SELECTION            '2'
#define DEVICE_STAR_SELECTION		            '3'

#define DEVICE_TAG_READER_ROUTER			     1
#define DEVICE_COORDINATOR				         2
#define DEVICE_STAR						         3

#define DEVICE_SPEED_SELECTION_19200            '1'
#define DEVICE_SPEED_SELECTION_115200           '2'

#define DEVICE_SPEED_19200     					 1
#define DEVICE_SPEED_115200     				 2

#endif /* LRFFP_H_ */

