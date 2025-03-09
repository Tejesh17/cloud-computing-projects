__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import csv
import sys
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets
from torch.utils.data import DataLoader
from services import sqs, s3
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(filename='app_tier.log', encoding='utf-8', level=logging.INFO)


mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion
# test_image = sys.argv[1]
sqs_req_queue_url = os.environ['SQS_REQ_QUEUE_URL']
sqs_resp_queue_url = os.environ['SQS_RESP_QUEUE_URL']

s3_in_bucket = os.environ['S3_IN_BUCKET']
s3_out_bucket = os.environ['S3_OUT_BUCKET']


def face_match(img_path, data_path): # img_path= location of photo, data_path= location of data.pt
    # getting embedding matrix of the given img
    img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True) # returns cropped face and probability
    emb = resnet(face.unsqueeze(0)).detach() # detech is to make required gradient false

    saved_data = torch.load('data.pt') # loading data.pt file
    embedding_list = saved_data[0] # getting embedding data
    name_list = saved_data[1] # getting list of names
    dist_list = [] # list of matched distances, minimum distance is used to identify the person

    for idx, emb_db in enumerate(embedding_list):
        dist = torch.dist(emb, emb_db).item()
        dist_list.append(dist)

    idx_min = dist_list.index(min(dist_list))
    return (name_list[idx_min], min(dist_list))

if __name__ == '__main__':
    try:
        while(True):
            messages = sqs.processMessages(sqs_req_queue_url)
            if(len(messages)> 0):
                img_name =messages[0]["Body"] 
                logger.info("Message recieved- "+ img_name)
                img_path = f'../{img_name}'
                s3.downloadObject(s3_in_bucket, img_name, img_path )
                logger.info("Downloaded object- "+ img_name)
                img_path = f'../{img_name}'
                result = face_match(img_path, 'data.pt')
                os.remove(img_path)
                print(result[0])
                logger.info("Result- "+ result[0])
                text_file_name =img_name.split('.')[0] + ".txt" 
                with open(text_file_name, "w") as file:
                    file.write(result[0])
                s3.uploadObject(s3_out_bucket,f"./{text_file_name}", text_file_name )
                os.remove(f"./{text_file_name}")
                logger.info("Uploaded out bucket- "+ text_file_name)
                sqs.sendMessage(sqs_resp_queue_url, f"{img_name}:{result[0]}" )
                logger.info("Sent message response queue- "+ text_file_name)
                sqs.deleteMessage(sqs_req_queue_url, messages[0]["ReceiptHandle"])
                logger.info("Deleted message"+ img_name)
                logger.info("_____________")

    except Exception as e:
        print("something went wrong please try again", e)
        logger.error("Error", e)