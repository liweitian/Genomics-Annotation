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
def store_jobinfo(jobId,filename):
	if os.path.isfile("jobId_type.txt"):
		f = open("jobId_type.txt","a")
	else:
		f = open("jobId_type.txt","w")
	f.write(jobId+" "+filename+"\n")
	f.close()

@route('/annotations/<jobId>')
def read_jobinfo(jobId):
	if os.path.isfile("jobId_type.txt"):
		f = open("jobId_type.txt","r")
		filename = ""
		while 1:
			line = f.readline()
			if not line:
				break
			list = line.split();
			if list[0] == jobId:
				filename = list[1]
				f.close()
				response.status = 200
				dict = {"code": "200 OK", "data":{"Job_id":jobId,"filename":filename}}
				return json.dumps(dict)

		f.close()
		response.status = 404
		#name = filename[0:-3]

		#if os.path.isfile("data/"+jobId+"/"+name+"vcf.count.log"):
			#f = open("data/"+jobId+"/"+name+"vcf.count.log","r")
			#res = ""
			#while 1:
				#line = f.readline()
				#print line
				#if not line:
					#break
				#res+=line
			#f.close
			#response.status = 200
			#dict = {"code": "200 OK","data":{"Job_id":jobId,"log: ":res}}
			#return  json.dumps(dict)
	response.status = 404

@route('/annotations',method = "POST")
def retrieve_jobId():
	data =  request.json
	job_id = data["job_id"]
	username  = data["username"]
	job_status = data["job_status"]
	bucket = data["s3_inputs_bucket"]
	filename = data["filepath"]
	submittime = data["submit_time"]
	key = data["s3_key_input_file"]
	print type(filename)
	print filename
	print type(key)
	print key
	print type(bucket)
	print bucket
	#content = request.url.split("&")
	#urlplusbucket = content[0]
	#bucketstring = urlplusbucket.split("?")
	#bucketname = bucketstring[1]
	#bucket = bucketname.split("=")[1]
	#filepath = "data/" + username + "/" + job_id +"/"+filename
	#key = content[1].split("=")[1].replace("%2F","/").replace("%7E","~")
	#print bucket
	#print filename
	#print key
	#dict = {"code": "200 OK","Data":{"jobs":[]}}
        #response.status = 200
	#return json.dumps(dict)

	s3 = boto3.resource('s3')
	s3.meta.client.download_file(bucket,key,filename)
	process(filename[5:],job_id)

	dict = {"id":job_id, "input_file":key}
        response.status = 200
        return json.dumps({"code":response.status,"data":dict})
	#if os.path.isfile("jobId_type.txt"):
        #        f = open("jobId_type.txt","r")
	#	jobId = []
        #	while 1:
        #        	line = f.readline()
        #        	if not line:
        #                	break
        #        	list = line.split();
	#			jobId.append(list[0])
        #	f.close()
	#	if len(jobId) != 0:
	#		dict = {"code": "200 OK","Data":{"jobs":[]}}
	#		response.status = 200
	#		for str in jobId:
	#			dict['Data']["jobs"].append("job_id: "+str)
	#			dict['Data']["jobs"].append("url: "+request.url+"/"+str)
	#		return json.dumps(dict)
	#response.status = 404

@post('/')
def process(filename,job_id):
    print filename
    filepath = "data/" + filename
    subprocess.call("mkdir " + "data/" + job_id, shell=True)
    subprocess.call("mv " + filepath + " " + "data/" + job_id, shell=True)
    dynamodb = boto3.resource('dynamodb')
    ann_table = dynamodb.Table('liweitian_annotations')
    primaryKey = {"job_id":job_id}
    Attributevalues = {':running':"RUNNING",":pending":"PENDING"}
   #ann_table.update_item(Key=primaryKey,UpdateExpression="set job_status=:running",ConditionExpression="job_status=:pending",ExpressionAttributeValues=Attributevalues,ReturnValues="UPDATED_NEW")
    subprocess.Popen("python run.py " + "data/" + job_id + "/"+filename, shell=True)

@route('/input-files', method='GET')
def display_myfile():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("gas-inputs")
    info = {"code":"200 OK"}
    files = []
    for file in bucket.objects.filter(Prefix='liweitian/'):
        files.append(file.key)
    data = {"files":files}
    info["data"] = data
    data = json.dumps(info)
    response.status = 200
    return data

if __name__ == "__main__":
    run(host='0.0.0.0', port=8888, debug=True, reloader=True)


