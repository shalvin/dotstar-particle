import RPi.GPIO as GPIO

def gpio_init(callback):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(17, GPIO.FALLING, callback=callback, bouncetime=300)

def gpio_cleanup():
    GPIO.cleanup()
    
