#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"
import boto3
import os
import subprocess
import json

def handler(event, context):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ['AWS_REGION']
    )

    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ['AWS_REGION']
    )
    
    try:
        ASU_ID = os.environ['ASU_ID']
        in_bucket_name = f'{ASU_ID}-input'
        out_bucket_name = f'{ASU_ID}-stage-1'
        output_bucket_name = f'{ASU_ID}-output'
        
        for record in event["Records"]:
            video_filename = record["s3"]["object"]["key"]
            print("Processing file:", video_filename)
            
            download_path = f'/tmp/{video_filename}'
            s3.download_file(in_bucket_name, video_filename, download_path)
            
            outfile = os.path.splitext(video_filename)[0] + '.jpg'
            
            split_cmd = f'ffmpeg -i {download_path} -vframes 1 /tmp/{outfile}'
            
            try:
                subprocess.run(split_cmd, shell=True, check=True, stderr=subprocess.PIPE)
                
                frame_path = f'/tmp/{outfile}'
                if os.path.exists(frame_path):
                    with open(frame_path, 'rb') as file:
                        s3.put_object(
                            Body=file,
                            Bucket=out_bucket_name,
                            Key=outfile 
                        )
                    payload = {
                        "bucket_name": out_bucket_name,
                        "image_file_name": outfile
                    }
                    
                    lambda_client.invoke(
                        FunctionName='face-recognition',
                        InvocationType='Event', 
                        Payload=json.dumps(payload)
                    )
                    
                    print(f"Invoked face-recognition function with payload: {payload}")

                
                subprocess.run(f'rm -rf /tmp/*', shell=True)
                
            except subprocess.CalledProcessError as e:
                print(f"Error processing video: {str(e)}")
                print(f"ffmpeg stderr: {e.stderr.decode()}")
                raise e
            
        return {
            'statusCode': 200,
            'body': 'Video processing completed successfully'
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error processing video: {str(e)}'
        }