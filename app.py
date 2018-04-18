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
from CCS811 import CCS811
# from APDS9301 import APDS9301
import Adafruit_DHT, requests, csv


GPIO.setmode(GPIO.BCM)
HIGH = True
LOW = False
PinStruct = namedtuple('Pins', ['lights', 'pump', 'fan', 'dht'])
fieldnames = [ 'humidity', 'temperature', 'CO2', 'tVOC' ]

Pins = PinStruct(lights=17, pump=27, fan=22, dht=4)
dht_sensor = Adafruit_DHT.DHT22
ccs811_sensor = CCS811()
# adps9300_sensor = APDS9301()

def createTimer(interval, function, args=[]):
    t = Timer(interval, function, args)
    t.start()

def defaultError(value):
    if value is None:
        return 'error'
    return value

def serviceToggle(pin, state, onInterval, offInterval):
    interval = onInterval if state else offInterval # Pick the interval based on the state we're switching to
    GPIO.output(pin, state) # Change the state of the service
    createTimer(interval, serviceToggle, [ pin, not state, onInterval, offInterval ]) # Create a timer to toggle the service

def writeSensorData(interval):
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, Pins.dht)
    temperature = defaultError(temperature)
    humidity = defaultError(humidity)
    # lux = defaultError(adps9300_sensor.read_lux())
    tVOC = None
    CO2 = None

    if ccs811_sensor.data_available():
        defaultError(ccs811_sensor.read_logorithm_results())
        CO2 = defaultError(ccs811_sensor.tVOC)
        tVOC = defaultError(ccs811_sensor.CO2)

    url = 'https://habsci-server.herokuapp.com/services'
    parameters = {
        'humidity': humidity,
        'temperature': temperature,
	    'lux': lux,
	    'air_quality': air_quality,
    }
    session = requests.Session()
    req = session.post(url, data = parameters)
    print(req.status_code)

    print(humidity)
    print(temperature)
    print(CO2)
    print(tVOC)

    with open('data.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({'humidity': humidity, 'temperature': temperature, 'CO2': CO2, 'tVOC': tVOC})

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

    if humidity is None or temperature is None:
        print('DHT22 values were None, retrying in 5 seconds...')
        createTimer(5, updateFan)
        return

    fan_speed = map_value(temperature, 20, 28, 0, 100)
    print("humidity: %d | temperature: %d | fan speed: %d" % (humidity, temperature, fan_speed))

    if temperature < 20:
        fan_speed = 0

    fan.ChangeDutyCycle(fan_speed)
    createTimer(1, updateFan)


def setup():
    ccs811_sensor.setup()
    for pin in Pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, LOW)

def main():
    serviceToggle(Pins.lights, HIGH, 60 * 60 * 14, 60 * 60 * 10)
    serviceToggle(Pins.pump, HIGH, 60, 60 * 120)

    with open('data.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    writeSensorData(60 * 5)
    fan.start(0)
    updateFan()

#sleep(30)
setup()
fan = GPIO.PWM(Pins.fan, 100) # Fan PWM pin and frequency
main()

