
import time

deployed = False

try:
    import RPi.GPIO as gpio
    deployed = True
except ImportError:
    pass 


def reset():
    if deployed:
        gpio.setmode(gpio.BCM)
        gpio.setup(18, gpio.OUT)
        gpio.output(18, gpio.HIGH)
        time.sleep(1)
        gpio.output(18, gpio.LOW)
        gpio.output(18, gpio.HIGH)
        time.sleep(5)

def close():
    if deployed:
        gpio.cleanup()