from services import s3, sqs


s3_in_bucket = ''
s3_out_bucket = ''

sqs_req_queue_url = ''
sqs_resp_queue_url = ''

sqs.purgeQueue(sqs_req_queue_url)
sqs.purgeQueue(sqs_resp_queue_url)

in_bucket_objects = s3.listObjects(s3_in_bucket)
for o in in_bucket_objects:
	s3.deleteObject(s3_in_bucket, o["Key"])

out_bucket_objects = s3.listObjects(s3_out_bucket)
for o in out_bucket_objects:
	s3.deleteObject(s3_out_bucket, o["Key"])