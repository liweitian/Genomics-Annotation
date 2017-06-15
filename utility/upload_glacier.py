#reference
#https://docs.python.org/2/library/
#https://bottlepy.org/docs/dev/
#http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingHTTPPOST.html
#https://boto3.readthedocs.io/en/latest/guide/migrations3.html
#import botocore
import boto3
#import os
#import sys
import time
import uuid
import json
import subprocess
#import base64
#import hmac, hashlib
import datetime
from boto3.dynamodb.conditions import Key, Attr

def sendTo_glacier():
	region_name = 'us-east-1' 
        client = boto3.client('sqs',region_name=region_name)
        response = client.receive_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_sendTo_glacier',MaxNumberOfMessages=1,VisibilityTimeout=20,WaitTimeSeconds=20)

        if response.has_key("Messages"):
                #print response
                data = response["Messages"][0]["Body"]
                receipt = response["Messages"][0]["ReceiptHandle"]
                parse = data.split("\\\"")
		for index in range(len(parse)):
			print index,parse[index]
		username = parse[3]
		result_key = parse[7]
		job_id = parse[11]
		complete_time = parse[15]

		#subprocess.call("mkdir " + "tmp", shell=True)
		
		complete_time = datetime.datetime.strptime(complete_time, "%Y-%m-%d;%H:%M")
		curtime = time.strftime('%Y-%m-%d;%H:%M',time.localtime(time.time())) 
		current_time = datetime.datetime.strptime(curtime, "%Y-%m-%d;%H:%M")
		diff_time =  (current_time-complete_time).total_seconds()
		if diff_time > 1800:
			key = result_key.replace("%2","/").replace("%7","~")
			print key
			s3 = boto3.resource('s3',region_name='us-east-1')
                	s3.meta.client.download_file("gas-results",key,"tmp/"+result_key)
			client = boto3.client('glacier',region_name="us-east-1")
			file = open("tmp/"+result_key)
			response = client.upload_archive(
    				body=file,
    				vaultName='ucmpcs',
			)
			print response["archiveId"]
			dynamodb = boto3.resource('dynamodb',region_name=region_name)
                	ann_table = dynamodb.Table('liweitian_annotations')
			primaryKey ={"job_id":job_id}
                	Attributevalues={':results_file_archive_id':response["archiveId"]}
                	ann_table.update_item(Key=primaryKey,UpdateExpression="set results_file_archive_id=:results_file_archive_id",ExpressionAttributeValues=Attributevalues,ReturnValues="UPDATED_NEW")
			
			client = boto3.client('s3',region_name="us-east-1")
			response = client.delete_object(
                                 Bucket='gas-results',
                                 Key=key,
				)
			client = boto3.client('sqs',region_name=region_name)
			client.delete_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_sendTo_glacier",ReceiptHandle=receipt)
			subprocess.call("rm tmp/"+result_key, shell=True)
if __name__ == "__main__":

	sendTo_glacier()
