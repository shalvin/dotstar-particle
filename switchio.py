import RPi.GPIO as GPIO


def io_callback(channel):
    print "neyh"

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(17, GPIO.FALLING, callback=io_callback, bouncetime=300)

def gpio_cleanup():
    GPIO.cleanup()
