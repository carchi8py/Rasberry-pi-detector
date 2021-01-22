import csv
import boto3

with open('new_user_credentials.csv', 'r') as input:
    csvreader = csv.DictReader(input)
    for row in csvreader:
        access_key_id = row['Access key ID']
        secret_key = row['Secret access key']

photo = 'IMG_1733.JPG'
client = boto3.client('rekognition',
                      aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_key,
                      region_name='us-west-2')
with open(photo, 'rb') as source_photo:
    source_bytes = source_photo.read()

response = client.detect_labels(Image={'Bytes': source_bytes})
for each in response['Labels']:
    print(each['Name'] + ": " + str(each['Confidence']))
