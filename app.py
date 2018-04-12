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


GPIO.setmode(GPIO.BOARD)
HIGH = True
LOW = False
PinStruct = namedtuple('Pins', ['lights', 'pump', 'fans', 'dht'])
fieldnames = [ 'humidity', 'temperature' ]

Pins = PinStruct(lights=11, pump=13, fan=15, dht=7)
dht_sensor = Adafruit_DHT.DHT11
fan = GPIO.PWM(Pins.fan, 100) # Fan PWM pin and frequency


def createTimer(interval, function, args=[]):
    t = Timer(interval, function, args)
    t.start()

def serviceToggle(pin, state, onInterval, offInterval):
    interval = onInterval if state else offInterval # Pick the interval based on the state we're switching to
    GPIO.output(pin, state) # Change the state of the service
    createTimer(interval, serviceToggle, pin, not state, onInterval, offInterval) # Create a timer to toggle the service

def writeSensorData(interval):
    if humidity is not None and temperature is not None:
        print('DHT22 values were None, retrying in 5 seconds...')
        createTimer(5, writeSensorData)
        return

    url = 'https://habsci.herokuapp.com/services'
    parameters = {
        'humidity': humidity,
        'temperature': temperature,
    }
    session = requests.Session()
    req = session.post(url, data = parameters)
    print(req.status_code)

    with open('data.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({'humidity': humidity, 'temperature': temperature})

    createTimer(interval, writeSensorData)

def map_value(value, fromMin, fromMax, toMin, toMax):
    # Figure out how 'wide' each range is
    fromSpan = fromMax - fromMin
    toSpan = toMax - toMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - fromMin) / float(fromSpan)

    # Convert the 0-1 range into a value in the right range.
    return toMin + (valueScaled * toSpan)

def updateFan():
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, Pins.dht)

    if humidity is not None and temperature is not None:
        print('DHT22 values were None, retrying in 5 seconds...')
        createTimer(5, updateFan)
        return

    print(humidity)
    print(temperature)

    fan_speed = map_value(temperature, 20, 28, 0, 100)

    if temperature < 20
        fan_speed = 0

    fan.ChangeDutyCycle(fan_speed)
    createTimer(1, updateFan)


def setup():
    for pin in Pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, LOW)

    serviceToggle(Pins.lights, HIGH, 60 * 60 * 14, 60 * 60 * 10)
    serviceToggle(Pins.pump, HIGH, 60, 60 * 120)
    serviceToggle(Pins.fans, HIGH, 60, 60 * 120)

    with open('data.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    writeSensorData(60 * 5)
    fan.start(0)
    updateFan()

sleep(30)
setup()

