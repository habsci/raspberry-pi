from collections import namedtuple
from time import sleep
import RPi.GPIO as GPIO
from datetime import datetime
import requests, csv

from helpers import create_timer
from sensor import Sensors
from service import Services


GPIO.setmode(GPIO.BCM)
fieldnames = [ 'humidity', 'temperature' ]

FAN_PIN = 22
LIGHTS_PIN = 17
PUMP_PIN = 27
DHT_PIN = 4

SENSOR_WRITE_INTERVAL = 5 * 60

def default_error(value):
    if value is None:
        return 'error'
    return value


class App:
    def __init__(self):
        self.sensor = Sensors(DHT_PIN)
        self.services = Services(LIGHTS_PIN, PUMP_PIN, FAN_PIN)


    def write_sensor_data(self, interval):
        temperature = default_error(self.sensor.temperature)
        humidity = default_error(self.sensor.humidity)

        url = 'https://habsci-server.herokuapp.com/services'
        parameters = {
            'humidity': humidity,
            'temperature': temperature,
        }
        session = requests.Session()
        req = session.post(url, data = parameters)
        print(req.status_code)

        print(humidity)
        print(temperature)

        with open('data.csv', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow({'humidity': humidity, 'temperature': temperature})

        create_timer(interval, write_sensor_data, [interval])

    def start(self):
        with open('data.csv', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

        write_sensor_data(SENSOR_WRITE_INTERVAL)


sleep(30)
app = App()
app.start()