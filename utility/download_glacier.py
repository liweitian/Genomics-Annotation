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

def download():
	region_name = 'us-east-1' 
        client = boto3.client('sqs',region_name=region_name)
        response = client.receive_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_archive_retrive",MaxNumberOfMessages=1,VisibilityTimeout=20,WaitTimeSeconds=20)
        if response.has_key("Messages"):
                data = response["Messages"][0]["Body"]
                receipt = response["Messages"][0]["ReceiptHandle"]
                parse = data.split("\\\"")
                for index in range(len(parse)):
                        print index,parse[index]
		job_id = parse[35]
		archive_id = parse[7]
                client.delete_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_archive_retrive",ReceiptHandle=receipt)
		client = boto3.client('glacier',region_name="us-east-1")
		response = client.get_job_output(
    			vaultName='ucmpcs',
                        jobId = job_id
		)


		dynamodb = boto3.resource('dynamodb',region_name="us-east-1")
                ann_table = dynamodb.Table('liweitian_annotations')
                dbdata = ann_table.scan(FilterExpression=Attr('results_file_archive_id').eq(archive_id))
                #print response
                count = dbdata["Count"]
                items = dbdata["Items"]
		s3 =  boto3.resource('s3',region_name="us-east-1")
                for i in range(0,count):
			key = items[i]["s3_key_result_file"]
			content =  response["body"].read()
                	fo = open(key,"w")
                	fo.write(content)
			resultkey = key.replace("%2","/").replace("%7","~")
	                print resultkey   
			s3.meta.client.upload_file(key,"gas-results",resultkey)
			subprocess.call("rm " + key, shell=True)

if __name__ == "__main__":
	download()
