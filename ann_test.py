import uuid
import boto3
import botocore.session
import datetime
import time
import json
while True:
    current_time = time.strftime('%Y-%m-%d;%H:%M',time.localtime(time.time()))
    data = {'job_id':"a689de02-9c1c-4585-a07f-91757b51f85a",'username':"lwt","input_file_name":"test.vcf","s3_inputs_bucket":"gas-input",'submit_time':current_time,"job_status":"PENDING","s3_key_input_file":"liweitian/lwt/a689de02-9c1c-4585-a07f-91757b51f85a~test.vcf","email":"liweitian93@outlook.com"}
    client = boto3.client('sns',region_name="us-east-1")
    topic_arn = "arn:aws:sns:us-east-1:127134666975:liweitian_job_request_notify"
    data["role"] = "free_user"
    message = json.dumps(data)
    subject = "a689de02-9c1c-4585-a07f-91757b51f85a"
    client = client.publish(TopicArn=topic_arn,Message=message,Subject=subject)
