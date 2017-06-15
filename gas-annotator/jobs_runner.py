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



def retrieve_jobId():
	region_name = 'us-east-1' 
	client = boto3.client('sqs',region_name=region_name)
        response = client.receive_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_job_requests',MaxNumberOfMessages=1,VisibilityTimeout=20,WaitTimeSeconds=20)

        if response.has_key("Messages"):
		#print response
                data = response["Messages"][0]["Body"]
		receipt = response["Messages"][0]["ReceiptHandle"]
                parse = data.split("\\\"")

		#for index in range(len(parse)):
       			#print index,parse[index]

                username = parse[3]
                status = parse[7]
                jobid = parse[19]
		role = parse[15]
                key = parse[11]
                bucket = parse[31]
                filename = parse[23]
		filepath = "data/"+key.replace("/","%2").replace("~","%7")

		s3 = boto3.resource('s3',region_name=region_name)
		s3.meta.client.download_file(bucket,key,filepath)
		process(filepath[5:],jobid,role)
		response = client.delete_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/127134666975/liweitian_job_requests',ReceiptHandle=receipt)

def process(filename,job_id,role):
    filepath = "data/" + filename
    subprocess.call("mkdir " + "data/" + job_id, shell=True)
    subprocess.call("mv " + filepath + " " + "data/" + job_id, shell=True)

    region_name = 'us-east-1'
    dynamodb = boto3.resource('dynamodb',region_name=region_name)
    ann_table = dynamodb.Table('liweitian_annotations')
    primaryKey = {"job_id":job_id}
    Attributevalues = {':running':"RUNNING",":pending":"PENDING"}
    ann_table.update_item(Key=primaryKey,UpdateExpression="set job_status=:running",ConditionExpression="job_status=:pending",ExpressionAttributeValues=Attributevalues,ReturnValues="UPDATED_NEW")
    subprocess.Popen("python run.py " + "data/" + job_id + "/"+filename+" "+role, shell=True)
 
if __name__ == "__main__":
	while True:
		print "trying to get msg from msg queue"
		retrieve_jobId()

