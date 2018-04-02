# import Adafruit_DHT, time, csv, schedule
# from CCS811 import CCS811
# from APDS9301 import APDS9301

# humidity_sensor = Adafruit_DHT.DHT11
# ccs811_sensor = CCS811()
# adps9300_sensor = APDS9301()
# DHT11_pin = 4

# ccs811_sensor.setup()

# def logSensorValues():
#     humidity, temperature = Adafruit_DHT.read_retry(humidity_sensor, DHT11_pin)
#     lux = adps9300_sensor.read_lux()

#     if ccs811_sensor.data_available():
#         ccs811_sensor.read_logorithm_results()
#     elif ccs811_sensor.check_for_error():
#         ccs811_sensor.print_error()

#     output = "%d,%d,%d,%d,%d" % (temperature, humidity, lux, ccs811_sensor.CO2, ccs811_sensor.tVOC)
#     print(output)

#     with open('newfile.csv', 'a') as file:
#         file.write(output + "\n")
from threading import Timer
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
HIGH = True
LOW = False
pumpPin = 11
lightPin = 13
fanPin = 15


def createTimer(interval, function, args):
    t = Timer(interval, function, args)
    t.start()

def serviceToggle(pin, state, onInterval, offInterval):
    interval = onInterval if state else offInterval # Pick the interval based on the state we're switching to
    GPIO.output(pin, state) # Change the state of the service
    createTimer(interval, serviceToggle, [ pin, not state, onInterval, offInterval ]) # Create a timer to toggle the service

def setup():
    GPIO.setup(pumpPin, GPIO.OUT)
    GPIO.setup(lightPin, GPIO.OUT)
    GPIO.setup(fanPin, GPIO.OUT)

    GPIO.output(pumpPin, LOW)
    GPIO.output(lightPin, LOW)
    GPIO.output(fanPin, LOW)

    serviceToggle(lightPin, HIGH, 10, 10)
    #serviceToggle(pumpPin, HIGH, 60, 60 * 120)
    #serviceToggle(fanPin, HIGH, 60, 60 * 120)

setup()

