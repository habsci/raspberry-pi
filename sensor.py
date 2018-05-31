import Adafruit_DHT

class Sensors:
    PinStruct = namedtuple('Pins', ['dht'])
    humidity = 0
    temperature = 0

    def __init__(self, dht):
        self.pins = PinStruct(dht=dht)
        self.dht_sensor = Adafruit_DHT.DHT22

    def read(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, Pins.dht)