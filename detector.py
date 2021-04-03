from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
import csv
import boto3
from time import sleep


class Detector(object):
    def __init__(self):
        # 4 = the pin on the Rasberry pi that the MotionSensor is connected to
        self.pir = MotionSensor(4, threshold=0.5)
        self.camera = PiCamera()
        self.source_photo = 'test.jpg'
        with open('new_user_credentials.csv', 'r') as input:
            csvreader = csv.DictReader(input)
            for row in csvreader:
                self.access_key_id = row['Access key ID']
                self.secret_key = row['Secret access key']
        
    def start(self):
        self.wait_for_motion()
        self.take_picture()
        self.wait_for_no_motion()
        photo = self.covert_img_to_bytes()
        results = self.aws_rekognition_image(photo)
        self.print_results(results)
            
    def wait_for_motion(self):
        self.pir.wait_for_no_motion()
        self.pir.wait_for_motion()
        print("Motion detect!")

    def wait_for_no_motion(self):
        self.pir.wait_for_no_motion()
        print("No Motion")
        
    def take_picture(self):
        self.camera.resolution = (1920, 1080)
        self.camera.rotation = 180
        self.camera.start_preview()
        sleep(2)
        self.camera.capture(self.source_photo)
        self.camera.stop_preview()

    def stop_camera(self):
        self.camera.stop_recording()

    def start_camera(self):
        datename = "{0:%Y}-{0:%m}-{0:%d}:{0:%H}:{0:%M}:{0:%S}".format(datetime.now())
        filename = str(datename) + "video.h264"
        self.camera.resolution = (640, 480)
        self.camera.rotation = 180
        self.camera.start_recording(filename)
        
    def aws_rekognition_image(self, photo):
        client = boto3.client('rekognition',
                              aws_access_key_id=self.access_key_id,
                              aws_secret_access_key=self.secret_key,
                              region_name='us-west-2')
        return client.detect_labels(Image={'Bytes': photo})
    
    def covert_img_to_bytes(self):
        with open(self.source_photo, 'rb') as photo:
            return photo.read()
    
    def print_results(self, results):
        for each in results['Labels']:
            print(each['Name'] + ": " + str(each['Confidence']))
        

def main():
    obj = Detector()
    obj.start()
    

if __name__ == "__main__":
    main()
