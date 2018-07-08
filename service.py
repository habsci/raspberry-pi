from time import sleep
import RPi.GPIO as GPIO
from picamera import PiCamera
from datetime import datetime

from helpers import create_timer, map_value
from sensor import Sensors

HIGH = True
LOW = False
PUMP_ON_DURATION = 60
PUMP_OFF_DURATION = 60 * 120


class Services:
    PinStruct = namedtuple('Pins', ['lights', 'pump', 'fan'])

    def __init__(self, lights, pump, fan, sensors):
        self.image_number = 0
        self.camera = PiCamera()
        self.pins = PinStruct(lights=lights, pump=pump, fan=fan)
        self.sensors = sensors

        for pin in Pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, LOW)

        self.fan = GPIO.PWM(self.pins.fan, 100) # Fan PWM pin and frequency
        current_time = datetime.now()
        if current_time.hour <= 7 or 19 >= current_time.hour:
            self.toggle_service(self.pins.lights, HIGH)
        
    
    def start(self):
        # Start the pump
        self.service_interval(self.pins.pump, HIGH, PUMP_ON_DURATION, PUMP_OFF_DURATION)
        
        # Start the fan
        self.fan.start(0)
        self.update_fan()

    def toggle_service(self, pin, state):
        GPIO.output(pin, state)

    def service_interval(self, pin, state, on_interval, off_interval):
        interval = on_interval if state else off_interval # Pick the interval based on the state we're switching to
        GPIO.output(pin, state) # Change the state of the service

        create_timer(interval, service_interval, [ pin, not state, on_interval, off_interval ]) # Create a timer to toggle the service

    def capture_image(self):
        sleep(10)
        self.camera.start_preview()
        sleep(2)
        self.camera.capture("/home/pi/Desktop/Github/raspberry-pi/image%s.jpg" % self.imageNumber)
        self.camera.stop_preview()
        self.image_number += 1

    def update_fan(self):
        if self.sensors.humidity is None or self.sensors.temperature is None:
            print('DHT22 values were None, retrying in 5 seconds...')
            create_timer(5, updateFan)
            return

        fan_speed = map_value(self.sensors.temperature, 20, 28, 0, 100)

        if self.sensors.temperature < 20:
            fan_speed = 0

        fan.ChangeDutyCycle(fan_speed)
        create_timer(5, self.update_fan)
