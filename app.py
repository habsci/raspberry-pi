import Adafruit_DHT
import time
from CCS811 import CCS811
from APDS9301 import APDS9301

humidity_sensor = Adafruit_DHT.DHT11
ccs811_sensor = CCS811()
adps9300_sensor = APDS9301()
DHT11_pin = 4

ccs811_sensor.setup()

while True:
	humidity, temperature = Adafruit_DHT.read_retry(humidity_sensor, DHT11_pin)
	lux = adps9300_sensor.read_lux()

	if ccs811_sensor.data_available():
		ccs811_sensor.read_logorithm_results()
	elif ccs811_sensor.check_for_error():
		ccs811_sensor.print_error()
	print("Humidity: %d | Temperature: %d" % (humidity, temperature))
	print("Lux: %s" % lux)
	print("CO2: %d | tVOC: %d" % (ccs811_sensor.CO2, ccs811_sensor.tVOC))
##	time.sleep(0.1)