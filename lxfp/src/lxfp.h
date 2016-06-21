#ifndef LXFP_H_
#define LXFP_H_

#define PACKAGE_STRING "lxfp UC.00.04"

#define VERSION_MSG \
    PACKAGE_STRING "\n" \
    "Copyright (C) 2015 Telit Communications S.p.A.\n" \
    "All rights reserved.\n\n"

#define HELP_MSG \
    "\n" \
    "Usage: lxfp <stream name> <serial port> <options>\n" \
    "\n" \
    "--verbose: enable verbose output\n" \
    "--version, -v: print version\n" \
    "--device, -d: choose device\n" \
    "\t 1 - HE910, HE863, UE910 families\n" \
    "\t 2 - GSM V2, GSM V3 families\n" \
    "\t 3 - UC family\n" \
    "\t 4 - GE910\n" \
    "\t 5 - DE family\n" \
    "\t 6 - HE910-V2/HE920/UE910-V2 \n" \
    "\t 7 - LE family\n" \
    "\t 8 - Altair family (LE866)\n" \
    "\t 9 - LE V2 family\n" \
    "--speed, -s: choose physical serial port speed\n" \
    "\t 1 - 115200 (default)\n" \
    "\t 2 - 230400\n" \
    "\t 3 - 460800\n" \
    "--usb, -u: enable flashing through usb\n" \
    "--timeinterval, -t: force boot delay value in ms\n" \
    "--bootloadercheck, -b: wait for bootloader device to connect\n" \
    "--restart, -r: use AT#SHDN command for restarting the device\n" \
    "\t <serial port> - serial port to be used for sending the command\n" \

#define DEVICE_HE863_SELECTION      '1'
#define DEVICE_V2_SELECTION         '2'
#define DEVICE_UC_SELECTION         '3'
#define DEVICE_GE_SELECTION         '4'
#define DEVICE_DE_SELECTION         '5'
#define DEVICE_xE910V2_SELECTION    '6'
#define DEVICE_LE_SELECTION         '7'
#define DEVICE_ALTAIR_SELECTION     '8'
#define DEVICE_LEV2_SELECTION       '9'

#define DEVICE_HE863    1
#define DEVICE_V2       2
#define DEVICE_UC       3
#define DEVICE_GE       4
#define DEVICE_DE       5
#define DEVICE_xE910V2  6
#define DEVICE_LE       7
#define DEVICE_ALTAIR   8
#define DEVICE_LEV2     9

#define DEVICE_SPEED_SELECTION_115200     '1'
#define DEVICE_SPEED_SELECTION_230400     '2'
#define DEVICE_SPEED_SELECTION_460800     '3'

#define DEVICE_SPEED_115200     1
#define DEVICE_SPEED_230400     2
#define DEVICE_SPEED_460800     3

#define SUPPORTED_CONNECTIONS	2

#endif /* LXFP_H_ */
