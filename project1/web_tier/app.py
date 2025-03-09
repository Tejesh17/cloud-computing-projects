from flask import Flask, request
from collections import deque
from services import s3, sqs, ec2
import time
import os
import threading

app = Flask(__name__)

s3_in_bucket = os.environ['S3_IN_BUCKET']
s3_out_bucket = os.environ['S3_OUT_BUCKET']

sqs_req_queue_url = os.environ['SQS_REQ_QUEUE_URL']
sqs_resp_queue_url = os.environ['SQS_RESP_QUEUE_URL']

autoscale_flag = False

ec2_machines = []
ec2_instance_no = 0

def start_autoscale():
    global autoscale_flag 
    autoscale_flag = True
    time.sleep(300)
    autoscale_flag = False

def autoscale():
    global ec2_instance_no
    global ec2_machines
    global autoscale_flag
    while(True):
        if(autoscale_flag):
            print("Running autoscaling")
            req_q_messages = sqs.getNoOfMessages(sqs_req_queue_url)
            resp_q_messages = sqs.getNoOfMessages(sqs_resp_queue_url)
            if(ec2_instance_no <20): 
                if(int(req_q_messages) > 0 and ec2_instance_no < int(req_q_messages)  ): 
                    for _ in range( int(req_q_messages) - ec2_instance_no): 
                        ec2_instance_no += 1 
                        instance_id = ec2.createInstance(f'app-tier-instance-{ec2_instance_no}') 
                        ec2_machines.append((ec2_instance_no, instance_id))
            if(int(req_q_messages) == 0 and int(resp_q_messages) == 0  and len(ec2_machines)>0):
                time.sleep(5)
                ec2.terminateInstance([ec2_machines[-1][1]])
                ec2_instance_no-=1
                ec2_machines.pop()
            print(ec2_instance_no, ec2_machines)
        time.sleep(2)


def start_background_task():
    task_thread = threading.Thread(target=autoscale)
    task_thread.daemon = True 
    task_thread.start()

def toggle_autoscale_thread():
    task_thread = threading.Thread(target=start_autoscale)
    task_thread.daemon = True 
    task_thread.start()

@app.route("/", methods=['POST'])
def process_image():
    global autoscale_flag
    if 'inputFile' not in request.files:
        return 'No file part'
    
    file = request.files['inputFile']

    if file:
        toggle_autoscale_thread()
        filename = file.filename
        print(filename)
        s3.uploadBinaryObject(s3_in_bucket, file, filename)
        sqs.sendMessage(sqs_req_queue_url, filename)
        while(True):
            messages = sqs.processMessages(sqs_resp_queue_url)
            if(len(messages) > 0):
                for m in messages:
                    res = m["Body"] 
                    if(res.split(':')[0] == filename):
                        sqs.deleteMessage(sqs_resp_queue_url, m["ReceiptHandle"])
                        return res

if __name__ == '__main__':
    start_background_task()
    app.run(debug=True, use_reloader = False)
else:
    start_background_task()
    gunicorn_app = app