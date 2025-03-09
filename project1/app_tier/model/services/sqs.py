import boto3

client = boto3.client(
			'sqs',
			# aws_access_key_id=credentials.AWS_ACCESS_KEY_ID,
			# aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY,
			# region_name=credentials.AWS_REGION 
		)

def createQueue(queueName):
	response = client.create_queue(QueueName=queueName, Attributes = {"FifoQueue": "true"})
	if(response["ResponseMetadata"]["HTTPStatusCode"] == 200):
		return response['QueueUrl']
	else: 
		return "Something went wrong creating queue, please try again"

def listQueues():
	try:
		print("SQS Queues:")
		response = client.list_queues()
		queues = response.get('QueueUrls', [])
		for index, queue in enumerate(queues):
			print(f'{index+1}: Queue URL- {queue}')

		print('\n')
	except:
		print("Something went wrong, please try again")

def sendMessage(queueURL,  message):
	_ = client.send_message(
		QueueUrl=queueURL,
		MessageBody=message,
	)

def getNoOfMessages(queueURL):
	try:
		queue_attributes = client.get_queue_attributes(
			QueueUrl=queueURL,
			AttributeNames=['ApproximateNumberOfMessages']
		)
		message_count = queue_attributes['Attributes']['ApproximateNumberOfMessages']
		return message_count
	except:
		print("Something went wrong, please try again")


def processMessages(queueURL):
	response = client.receive_message(
		QueueUrl=queueURL,
		MaxNumberOfMessages=1,
		WaitTimeSeconds = 10,
		MessageAttributeNames=['All']
	)
	messages = response.get('Messages', [])
	return messages

def deleteMessage(queueUrl, receiptHandle):
	_ = client.delete_message(
		QueueUrl=queueUrl,
		ReceiptHandle=receiptHandle
	)

def deleteQueue(queueURL):
	_ = client.delete_queue(
		QueueUrl=queueURL
	)