from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
import csv
import cv2
import boto3
from time import sleep

class Detector(object):
    def __init__(self):
        #4 = the pin on the Rasberry pi that the MotionSensor is connected to
        self.pir = MotionSensor(4, threshold=0.5)
        self.camera = PiCamera()
        self.source_photo = 'test.jpg'
        self.image_width = 1920
        self.image_height = 1080
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
        self.draw_bounding_box(results)
            
    def wait_for_motion(self):
        self.pir.wait_for_no_motion()
        self.pir.wait_for_motion()
        print("Motion detect!")

    def wait_for_no_motion(self):
        self.pir.wait_for_no_motion()
        print("No Motion")
        
    def take_picture(self):
        self.camera.resolution = (self.image_width, self.image_height)
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
        self.camera.resolution = (self.image_width, self.image_height)
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
                
    def draw_bounding_box(self, results):
        for each in results['Labels']:
            if 'Instances' in each:
                for instance in each['Instances']:
                    if 'BoundingBox' in instance:
                        box = self.covert_bounding_box(instance['BoundingBox']['Left'],
                                                       instance['BoundingBox']['Top'],
                                                       instance['BoundingBox']['Width'],
                                                       instance['BoundingBox']['Height'])
                        con = str(each['Confidence']).split('.')[0]
                        label = each['Name'] + ": " + str(con) + '%'
                        self.draw_box(box, label)

    def draw_box(self, box, label):
        imgData = cv2.imread(self.source_photo)
        imgHeight, imgWidth, _ = imgData.shape
        left = int(box[2])
        top = int(box[3])
        right = left + int(box[0])
        bottom = top + int(box[1])
        thick = (imgHeight + imgWidth) // 900
        color = (0,255,0)
        print(left, right, top, bottom)
        print(thick)
        print(thick//4)
        print(imgHeight)
        print(imgWidth)
        cv2.rectangle(imgData, (left, top), (right, bottom), color, thick)
        cv2.putText(imgData, label, (left, top - 12), 0, 1e-3 * imgHeight, color, 2)
        cv2.imwrite(self.source_photo, imgData)
        


    def covert_bounding_box(self, left, top, width, height):
        left_box = left * self.image_width
        top_box = top * self.image_height
        width_box = width * self.image_width
        height_box = height * self.image_height
        return [width_box, height_box, left_box, top_box]
    
def main():
    obj = Detector()
    obj.start()
    

if __name__ == "__main__":
    main()