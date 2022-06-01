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
for reset_pin in (12, 0):
    try:
        pin = mraa.Gpio(reset_pin)
        pin.dir(mraa.DIR_OUT)
    except Exception as ex:
        print('error in reset (pin {}): {}'.format(reset_pin, ex))

# AP: sometimes hard reset just fails, we need a fallback
print('sleep 7s then reboot!')
time.sleep(7)
print('rebooting!')
os.system('reboot')

