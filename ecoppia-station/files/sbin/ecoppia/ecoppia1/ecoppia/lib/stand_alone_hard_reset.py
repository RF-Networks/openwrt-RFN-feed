import os
import mraa
import time

cmd = '/etc/init.d/rfnwatchdogd stop'
os.system(cmd)           
time.sleep(1)
cmd = 'mt7688_pinmux set i2s gpio'
os.system(cmd)             
time.sleep(1)
pin=mraa.Gpio(0)
pin.dir(mraa.DIR_OUT)