from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime


class Detector(object):
    """
    Raspberry pi code to detect motion and record video and images
    """
    def __init__(self):
        self.pir = MotionSensor(4, threshold=0.5)
        self.camera = PiCamera()
        
    def start(self):
        """
        When motion is dected start camera until motion is no longer detected
        """
        while True:
            # The camera always start off detecting motion, so wait until it see no motion
            self.pir.wait_for_no_motion()
            self.pir.wait_for_motion()
            print("Motion detect!")
            self.start_camera()
            self.pir.wait_for_no_motion()
            print("No Motion")
            self.camera.stop_recording()
        
    def start_camera(self):
        """
        Record video
        """
        datename = "{0:%Y}-{0:%m}-{0:%d}:{0:%H}:{0:%M}:{0:%S}".format(datetime.now())
        filename = str(datename) + "video.h264"
        self.camera.resolution = (1920, 1080)
        self.camera.rotation = 180
        self.camera.start_recording(filename)


def main():
    obj = Detector()
    obj.start()
    

if __name__ == "__main__":
    main()
