__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import imutils
import cv2
import json
import boto3
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
from shutil import rmtree
import numpy as np
import torch
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)


TEMP_DIR = '/tmp'

os.environ['TORCH_HOME'] = TEMP_DIR
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20, device='cpu', keep_all=True)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def download_file(bucket, key, local_path):
    try:
        s3_client.download_file(bucket, key, local_path)
        return True
    except ClientError as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        return False

def upload_file(file_path, bucket, key):
    try:
        s3_client.upload_file(file_path, bucket, key)
        return True
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return False

def face_recognition_function(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
            
        boxes, _ = mtcnn.detect(img)
        
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        faces = mtcnn(img, return_prob=True)
        
        if isinstance(faces, tuple):
            face, prob = faces
        else:
            logger.warning(f"No face detected in image: {image_path}")
            return None
            
        if face is None:
            logger.warning(f"No face detected in image: {image_path}")
            return None
            
        data_path = os.path.join(TEMP_DIR, 'data.pt')
        if not os.path.exists(data_path):
            logger.error("data.pt not found in /tmp/")
            return None
            
        saved_data = torch.load(data_path, map_location='cpu')
        
        if len(face.shape) == 4: 
            face_tensor = face
        else:
            face_tensor = face.unsqueeze(0)
            
        emb = resnet(face_tensor).detach()
        
        embedding_list = saved_data[0]
        name_list = saved_data[1]
        
        dist_list = []
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
            
        idx_min = dist_list.index(min(dist_list))
        return name_list[idx_min]
        
    except Exception as e:
        logger.error(f"Error in face recognition: {str(e)}")
        return None



def handler(event, context):
    try:
        if not isinstance(event, dict):
            event = json.loads(event)
            
        bucket_name = event.get('bucket_name')
        image_file_name = event.get('image_file_name')
        
        if not bucket_name or not image_file_name:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required parameters: bucket_name or image_file_name')
            }
            
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        
        for file in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Error deleting file {file_path}: {str(e)}")
            
        data_bucket = f"{bucket_name.split('-')[0]}-data-file" 
        data_path = os.path.join(TEMP_DIR, 'data.pt')
        if not download_file(data_bucket, 'data.pt', data_path):
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to download data.pt')
            }
            
        local_image_path = os.path.join(TEMP_DIR, image_file_name)
        if not download_file(bucket_name, image_file_name, local_image_path):
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to download input image')
            }
            
        recognized_name = face_recognition_function(local_image_path)
        
        if recognized_name is None:
            return {
                'statusCode': 404,
                'body': json.dumps('No face detected or recognition failed')
            }
            
        output_filename = f"{os.path.splitext(image_file_name)[0]}.txt"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        with open(output_path, 'w') as f:
            f.write(recognized_name)
            
        output_bucket = f"{bucket_name.split('-')[0]}-output" 
        if not upload_file(output_path, output_bucket, output_filename):
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to upload result file')
            }
            
        for file in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Error deleting file {file_path}: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Face recognition completed successfully',
                'recognized_name': recognized_name,
                'output_file': output_filename
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing request: {str(e)}')
        }