# Copyright (C) 2011-2016 Vas Vasiliadis
# University of Chicago
##
#reference https://boto3.readthedocs.io/en/latest/

__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import sys
import time
import driver
import boto3
import subprocess
import json
from boto3.dynamodb.conditions import Key, Attr
# A rudimentary timer for coarse-grained profiling
class Timer(object):
	def __init__(self, verbose=False):
		self.verbose = verbose

	def __enter__(self):
		self.start = time.time()
		return self

	def __exit__(self, *args):
		self.end = time.time()
		self.secs = self.end - self.start
		self.msecs = self.secs * 1000  # millisecs
		if self.verbose:
			print "Elapsed time: %f ms" % self.msecs

if __name__ == '__main__':
	# Call the AnnTools pipeline
	if len(sys.argv) > 1:
		input_file_name = sys.argv[1]
		role = sys.argv[2]
		with Timer() as t:
			driver.run(input_file_name, 'vcf')
		print "Total runtime: %f seconds" % t.secs
		
		#print "file name is:"
		#print input_file_name
		#get username
		content = input_file_name.split("%2")
		username = content[1]
		#print "content"
		#print content 
		job_id = content[0].split("/")[1]
		print job_id
		# Add code here to save results and log files to S3 results bucket	  ...
		region_name = 'us-east-1'
		s3 = boto3.resource('s3',region_name=region_name)
		content = input_file_name.split("/")
		deleteDir = content[1]
		prefix = content[2].replace("%2F","/").replace("%7E","~")[:-3]
		resultFile = input_file_name[0:-3]+"annot.vcf"
		#print "prefix"
		#print prefix
		#print resultFile
		#print prefix
		logFile = input_file_name+".count.log"
		#print logFile
		# Upload the results file
		#upload_file(Filename, Bucket, Key, ExtraArgs=None, Callback=None, Config=None)
		resultkey = prefix.replace("%2","/").replace("%7","~")+"annot.vcf"
		s3.meta.client.upload_file(resultFile,"gas-results",resultkey)
		# Upload the log file
		logkey = prefix.replace("%2","/").replace("%7","~")+"count.log"
		s3.meta.client.upload_file(logFile,"gas-results",logkey)
		# Clean up (delete) local job files
		subprocess.call("rm -rf data/"+deleteDir,shell = True)
		#update database
		dynamodb = boto3.resource('dynamodb',region_name=region_name)
		ann_table = dynamodb.Table('liweitian_annotations')
		#response = ann_table.query(IndexName='username_index',KeyConditionExpression=Key('username').eq(username))
		response = ann_table.get_item(Key={"job_id":job_id})
		item = response['Item']
		#print items

		username = item["username"]
		job_status = item["job_status"]
		job_id = item["job_id"]
		s3_inputs_bucket = item["s3_inputs_bucket"]
		key = item["s3_key_input_file"]
		input_file_name = item["input_file_name"]
		submit_time = item["submit_time"]
		complete_time = time.strftime('%Y-%m-%d;%H:%M',time.localtime(time.time()))
		resultKey = prefix+"annot.vcf"
		logKey = prefix+"count.log"
		primaryKey ={"job_id":job_id}
		Attributevalues={':complete_time':complete_time,':s3_key_result_file':resultKey,':s3_key_log_file':logKey,':result_bucket':"gas-results",':complete':"COMPLETED"}
		ann_table.update_item(Key=primaryKey,UpdateExpression="set complete_time=:complete_time,s3_key_result_file=:s3_key_result_file,s3_key_log_file=:s3_key_log_file,s3_results_bucket=:result_bucket,job_status=:complete",ExpressionAttributeValues=Attributevalues,ReturnValues="UPDATED_NEW")
		
		#publish a completed notification to topic
		client = boto3.client('sns',region_name=region_name)
		data = {'job_id':job_id,'username':username}
        	topic_arn =  "arn:aws:sns:us-east-1:127134666975:liweitian_job_results"
        	message = json.dumps(data)
        	subject = job_id
        	client.publish(TopicArn=topic_arn,Message=message,Subject=subject)
		if role=="free_user":
			data["complete_time"]=complete_time
			data["result_key"]=resultKey
			message = json.dumps(data)
			topic_arn ="arn:aws:sns:us-east-1:127134666975:liweitian_free_user_glacier"
			client.publish(TopicArn=topic_arn,Message=message,Subject=subject) 
	else:
		print 'A valid .vcf file must be provided as input to this program.'
