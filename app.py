import Adafruit_DHT

humidity_sensor = Adafruit_DHT.DHT11
DHT11_pin = 4
humidity, temperature = Adafruit_DHT.read_retry(humidity_sensor, DHT11_pin)

print(humidity)
print(temperature)