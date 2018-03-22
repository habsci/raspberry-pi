from picamera import PiCamera
from time import sleep

camera = PiCamera()
imageNumber = 0

def captureImage():
    global imageNumber
    camera.start_preview()
    sleep(2)
    camera.capture("/home/pi/Desktop/Github/raspberry-pi/image%s.jpg" % imageNumber)
    camera.stop_preview()
    imageNumber += 1

captureImage()
