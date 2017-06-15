#reference
#https://docs.python.org/2/library/
#https://bottlepy.org/docs/dev/
#http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingHTTPPOST.html
#https://boto3.readthedocs.io/en/latest/guide/migrations3.html
from bottle import route,post,run,request,response, template
import botocore
import boto3
import os
import sys
import time
import uuid
import json
import subprocess
import base64
import hmac, hashlib
import datetime
from boto3.dynamodb.conditions import Key, Attr
#from mpcs_utils import auth

def send_result(): 
	region_name = 'us-east-1' 
        client = boto3.client('sqs',region_name=region_name)
        response = client.receive_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_job_results',MaxNumberOfMessages=1,VisibilityTimeout=20,WaitTimeSeconds=20)

        if response.has_key("Messages"):
                #print response
                data = response["Messages"][0]["Body"]
                receipt = response["Messages"][0]["ReceiptHandle"]
                parse = data.split("\\\"")
                #print parse[0]
                #print parse[1]
		#print parse[2]
                #print parse[3]
		#print parse[4]
                #print parse[5]
                jobid =  parse[7]
		print jobid
		send_email(jobid)
		response = client.delete_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_job_results',ReceiptHandle=receipt)

def send_email(jobid):
	#get email addr from database.
	#can also be obtained from sqs message
	client = boto3.client('ses',region_name='us-east-1')
	
	dynamodb = boto3.resource('dynamodb',region_name="us-east-1")
        ann_table = dynamodb.Table('liweitian_annotations')
        response = ann_table.get_item(Key={"job_id":jobid})
	#print response
	#print "check"

        item = response['Item']
                #print items

        username = item["username"]
        job_status = item["job_status"]
        job_id = item["job_id"]
        s3_inputs_bucket = item["s3_inputs_bucket"]
        key = item["s3_key_input_file"]
        input_file_name = item["input_file_name"]
        submit_time = item["submit_time"]
	email = item["email"]
        print username
        print job_status
        print job_id
        print s3_inputs_bucket
        print key
	print email

	response = client.send_email(
        Destination={
            'ToAddresses': [
                email
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': 'Hi '+username+',<br>'+'Your job: '+ job_id +'is completed. Link: <a class="ulink" href="https://liweitian.ucmpcs.org/annotations" target="_blank">See my job</a>.',
                },
             },
             'Subject': {
                    'Charset': 'UTF-8',
                     'Data': 'Your job is completed',
             },
        },
        Source='liweitian@ucmpcs.org'
	)

if __name__ == "__main__":

	#while True:
		#print "trying to get msg from msg queue"
	send_result()
