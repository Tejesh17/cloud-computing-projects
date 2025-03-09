import boto3
import os

client = boto3.client(
			's3',
			# aws_access_key_id=credentials.AWS_ACCESS_KEY_ID,
			# aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY,
			# region_name=credentials.AWS_REGION 
		)

def createBucket(bucketName):
	response = client.create_bucket(
		Bucket=bucketName,
	)

	if(response['ResponseMetadata']['HTTPStatusCode'] == 200):
		return response["Location"]
	print("Something went wrong creating an S3 bucket, please try again\n")
	return

def downloadObject(bucket, key, download_path):
	try:
		client.download_file(bucket, key, download_path)
	except Exception as e:
		print("download failed" + e)


def deleteBucket(bucketName: str) -> None :
	response = client.delete_bucket(
		Bucket=bucketName,
	)
	return response

def listBuckets():
	response = client.list_buckets(
		MaxBuckets=10,
	)
	try:
		buckets = response.get("Buckets", [])
		print("S3 Buckets:")
		for index, bucket in enumerate(buckets):
			print(f'{index+1}: Name- {bucket['Name']}')
		print('\n')
	except:
		print("Something went wrong, please try again\n")


def uploadObject(bucket, path, key):
	try:
		pathToFile = os.path.abspath(path)
		with open(pathToFile, 'rb') as file:
			response = client.put_object(
				Body= file,
				Bucket=bucket,
				Key=key,
			)
		if(response['ResponseMetadata']['HTTPStatusCode'] == 200):
			return "Successfully uploaded file"
	except:
		print("Something went wrong, please try again\n")

def uploadBinaryObject(bucket, data, key):
	try:
		client.upload_fileobj(data, bucket, key)
	except Exception as e:
		print("Exception- " + e)

def deleteObject(bucket, key):
	_ = client.delete_object(
		Bucket=bucket,
		Key=key,
	)

def listObjects(bucket):
	response = client.list_objects(Bucket = bucket)
	return response.get("Contents", [])