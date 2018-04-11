# import Adafruit_DHT, time, csv, schedule
# from CCS811 import CCS811
# from APDS9301 import APDS9301

# humidity_sensor = Adafruit_DHT.DHT11
# ccs811_sensor = CCS811()
# adps9300_sensor = APDS9301()
# DHT11_pin = 4

# ccs811_sensor.setup()

# def logSensorValues():
    # humidity, temperature = Adafruit_DHT.read_retry(humidity_sensor, DHT11_pin)
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
from collections import namedtuple
from time import sleep
import RPi.GPIO as GPIO
import Adafruit_DHT, requests, csv

humidity_sensor = Adafruit_DHT.DHT11

GPIO.setmode(GPIO.BOARD)
HIGH = True
LOW = False
PinStruct = namedtuple('Pins', ['lights', 'pump', 'fans', 'dht11'])
Pins = PinStruct(lights=11, pump=13, fans=15, dht11=7)


def createTimer(interval, function, args):
    t = Timer(interval, function, args)
    t.start()

def serviceToggle(pin, state, onInterval, offInterval):
    interval = onInterval if state else offInterval # Pick the interval based on the state we're switching to
    GPIO.output(pin, state) # Change the state of the service
    createTimer(interval, serviceToggle, [ pin, not state, onInterval, offInterval ]) # Create a timer to toggle the service

def storeSensorData():
    humidity, temperature = Adafruit_DHT.read_retry(humidity_sensor, Pins.dht11)

    if (humidity == None or temperature == None):
        createTimer(60 * 5, storeSensorData)
        return

    print(humdity)
    print(temperature)

    url = 'https://habsci.herokuapp.com/services'
    parameters = {
        'humidity': humidity,
        'temperature': temperature,
    }
    session = requests.Session()
    req = session.post(url, data = parameters)
    print(req.status_code)

    with open('data.csv', 'w') as file:
        fieldnames = [ 'humidity', 'temperature' ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'humidity': humidity, 'temperature': temperature})

    createTimer(60 * 5, storeSensorData)

def setup():
    for pin in Pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, LOW)

    serviceToggle(Pins.lights, HIGH, 60 * 60 * 14, 60 * 60 * 10)
    serviceToggle(Pins.pump, HIGH, 60, 60 * 120)
    serviceToggle(Pins.fans, HIGH, 60, 60 * 120)

    with open('data.csv', 'w') as file:
        fieldnames = [ 'humidity', 'temperature' ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    storeSensorData()

sleep(30)
setup()

