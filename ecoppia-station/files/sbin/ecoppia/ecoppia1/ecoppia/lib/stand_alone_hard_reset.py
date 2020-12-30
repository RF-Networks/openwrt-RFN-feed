import os
import mraa
import time

cmd = '/etc/init.d/rfnwatchdogd stop'
os.system(cmd)           
time.sleep(1)
cmd = 'mt7688_pinmux set i2s gpio'
os.system(cmd)             
time.sleep(1)

# support different mraa pins for old/new stations
for reset_pin in (0, 12):
    try:
        pin = mraa.Gpio(reset_pin)
        pin.dir(mraa.DIR_OUT)
    except Exception as ex:
        print('error in reset (pin {}): {}'.format(reset_pin, ex))
