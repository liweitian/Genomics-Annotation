# mpcs_app.py
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
#
# Application logic for the GAS
#
##
#reference
#http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
#https://boto3.readthedocs.io/en/latest/
#http://bottlepy.org/docs/dev/

__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import base64
import datetime
import hashlib
import hmac
import json
import sha
import string
import time
import urllib
import urlparse
import uuid
import boto3
import botocore.session
import datetime
from boto3.dynamodb.conditions import Key, Attr

from mpcs_utils import log, auth
from bottle import route, request, redirect, template, static_file

import  stripe

'''
*******************************************************************************
Set up static resource handler - DO NOT CHANGE THIS METHOD IN ANY WAY
*******************************************************************************
'''
@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
  # Tell Bottle where static files should be served from
  return static_file(filename, root=request.app.config['mpcs.env.static_root'])

'''
*******************************************************************************
Home page
*******************************************************************************
'''
@route('/', method='GET', name="home")
def home_page():
  return template(request.app.config['mpcs.env.templates'] + 'home', auth=auth)

'''
*******************************************************************************
Registration form
*******************************************************************************
'''
@route('/register', method='GET', name="register")
def register():
  log.info(request.url)
  return template(request.app.config['mpcs.env.templates'] + 'register',
    auth=auth, name="", email="", username="", 
    alert=False, success=True, error_message=None)

@route('/register', method='POST', name="register_submit")
def register_submit():
  try:
    auth.register(description=request.POST.get('name').strip(),
                  username=request.POST.get('username').strip(),
                  password=request.POST.get('password').strip(),
                  email_addr=request.POST.get('email_address').strip(),
                  role="free_user")
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register', 
      auth=auth, alert=True, success=False, error_message=error)  

  return template(request.app.config['mpcs.env.templates'] + 'register', 
    auth=auth, alert=True, success=True, error_message=None)

@route('/register/<reg_code>', method='GET', name="register_confirm")
def register_confirm(reg_code):
  log.info(request.url)
  try:
    auth.validate_registration(reg_code)
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
      auth=auth, success=False, error_message=error)

  return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
    auth=auth, success=True, error_message=None)

'''
*******************************************************************************
Login, logout, and password reset forms
*******************************************************************************
'''
@route('/login', method='GET', name="login")
def login():
  log.info(request.url)
  redirect_url = "/annotations"
  # If the user is trying to access a protected URL, go there after auhtenticating
  if request.query.redirect_url.strip() != "":
    redirect_url = request.query.redirect_url
  return template(request.app.config['mpcs.env.templates'] + 'login', 
    auth=auth, redirect_url=redirect_url, alert=False)

@route('/login', method='POST', name="login_submit")
def login_submit():
  #redirect to /annotations if successful
  auth.login(request.POST.get('username'),
             request.POST.get('password'),
             #success_redirect=request.POST.get('redirect_url'), need modify
             success_redirect="/annotate",
	     fail_redirect='/login')

@route('/logout', method='GET', name="logout")
def logout():
  log.info(request.url)
  auth.logout(success_redirect='/login')


'''
*******************************************************************************
*
CORE APPLICATION CODE IS BELOW...
*
*******************************************************************************
'''

'''
*******************************************************************************
Subscription management handlers
*******************************************************************************
'''
import stripe

# Display form to get subscriber credit card info
@route('/subscribe', method='GET', name="subscribe")
def subscribe():
	auth.require(fail_redirect='/login?redirect_url=' + request.url)
	if auth.current_user.role != "free_user":
		return template(request.app.config['mpcs.env.templates'] + 'profile',
                auth=auth,success=True, error_message=None)
	return template(request.app.config['mpcs.env.templates'] + 'subscribe',
        auth=auth,success=True, error_message=None)

# Process the subscription request
@route('/subscribe', method='POST', name="subscribe_submit")
def subscribe_submit():
	stripe_token = request.forms.get("stripe_token")
	stripe.api_key = request.app.config['mpcs.stripe.secret_key']
	

	customer_obj = stripe.Customer.create(source=stripe_token)
	stripe.Subscription.create(customer=customer_obj["id"],plan="premium_plan")

	auth.current_user.update(role="premium_user")
	region_name=request.app.config['mpcs.aws.app_region']

	username = auth.current_user.username
	dynamodb = boto3.resource('dynamodb',region_name="us-east-1")
	ann_table = dynamodb.Table('liweitian_annotations')
	response = ann_table.query(IndexName="username_index",KeyConditionExpression=Key("username").eq(username))
	count = response["Count"]
	items = response["Items"]
	
	for i in range(0,count):
		if items[i].has_key("results_file_archive_id"):
			print items[i]["results_file_archive_id"]
			client = boto3.client('glacier',region_name="us-east-1")
			response = client.initiate_job(
                           vaultName='ucmpcs',
                           jobParameters={'Type': "archive-retrieval",'ArchiveId': items[i]["results_file_archive_id"],'Description': items[i]["s3_key_result_file"],'SNSTopic': "arn:aws:sns:us-east-1:127134666975:liweitian_archive_retrive",'Tier':"Expedited"})

	return template(request.app.config['mpcs.env.templates'] + 'profile',
                auth=auth,success=True, error_message=None)
'''
*******************************************************************************
Display the user's profile with subscription link for Free users
*******************************************************************************
'''
@route('/profile', method='GET', name="profile")
def user_profile():
	auth.require(fail_redirect='/login?redirect_url=' + request.url)
	return template(request.app.config['mpcs.env.templates'] + 'profile',
        auth=auth,success=True, error_message=None)


'''
*******************************************************************************
Creates the necessary AWS S3 policy document and renders a form for
uploading an input file using the policy document
*******************************************************************************
'''
@route('/annotate', method='GET', name="annotate")
def upload_input_file():
  log.info(request.url)
  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  username = auth.current_user.username
  # Use the boto session object only to get AWS credentials
  session = botocore.session.get_session()
  aws_access_key_id = str(session.get_credentials().access_key)
  aws_secret_access_key = str(session.get_credentials().secret_key)
  aws_session_token = str(session.get_credentials().token)

  # Define policy conditions
  bucket_name = request.app.config['mpcs.aws.s3.inputs_bucket']
  encryption = request.app.config['mpcs.aws.s3.encryption']
  acl = request.app.config['mpcs.aws.s3.acl']

  # Generate unique ID to be used as S3 key (name)
  key_name = request.app.config['mpcs.aws.s3.key_prefix']+username+"/" + str(uuid.uuid4())
  # Redirect to a route that will call the annotator
  redirect_url = str(request.url) + "/job"

  # Define the S3 policy doc to allow upload via form POST
  # The only required elements are "expiration", and "conditions"
  # must include "bucket", "key" and "acl"; other elements optional
  # NOTE: We also must inlcude "x-amz-security-token" since we're
  # using temporary credentials via instance roles
  print key_name
  limit = 99999999
  if auth.current_user.role=="free_user":
	limit = 153600
  policy_document = str({
    "expiration": (datetime.datetime.utcnow() + 
      datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "conditions": [
      {"bucket": bucket_name},
      ["starts-with","$key", key_name],
      ["starts-with", "$success_action_redirect", redirect_url],
      {"x-amz-server-side-encryption": encryption},
      {"x-amz-security-token": aws_session_token},
      ["content-length-range",0,limit],
      {"acl": acl}]})

  # Encode the policy document - ensure no whitespace before encoding
  policy = base64.b64encode(policy_document.translate(None, string.whitespace))

  # Sign the policy document using the AWS secret key
  signature = base64.b64encode(hmac.new(aws_secret_access_key, policy, hashlib.sha1).digest())

  # Render the upload form
  # Must pass template variables for _all_ the policy elements
  # (in addition to the AWS access key and signed policy from above)
  return template(request.app.config['mpcs.env.templates'] + 'upload',
    auth=auth, bucket_name=bucket_name, s3_key_name=key_name,
    aws_access_key_id=aws_access_key_id,
    aws_session_token=aws_session_token, redirect_url=redirect_url,
    encryption=encryption, acl=acl, policy=policy, signature=signature)


'''
*******************************************************************************
Accepts the S3 redirect GET request, parses it to extract 
required info, saves a job item to the database, and then
publishes a notification for the annotator service.
*******************************************************************************
'''
@route('/annotate/job', method='GET')
def create_annotation_job_request():
	content = request.url.split("&")
        urlplusbucket = content[0]
        bucketstring = urlplusbucket.split("?")
        bucketname = bucketstring[1]
        bucket = bucketname.split("=")[1]
        filepath = "data/" + content[1].split("=")[1]
        key = content[1].split("=")[1].replace("%2F","/").replace("%7E","~")
        jobid = key.split("/")[2].split("~")[0]
        filename = key.split("/")[2].split("~")[1]
        print bucket
        print key
        print jobid
        print filename
	region_name = request.app.config['mpcs.aws.app_region']
	username = auth.current_user.username
	email = auth.current_user.email_addr
	dynamodb = boto3.resource('dynamodb',region_name=region_name)
 	ann_table = dynamodb.Table('liweitian_annotations')
        current_time = time.strftime('%Y-%m-%d;%H:%M',time.localtime(time.time()))
	data = {'job_id':jobid,'username':username,"input_file_name":filename,"s3_inputs_bucket":bucket,'submit_time': current_time,"job_status":"PENDING","s3_key_input_file":key,"email":email}
	ann_table.put_item(Item=data)

        client = boto3.client('sns',region_name=region_name)
        topic_arn = "arn:aws:sns:us-east-1:127134666975:liweitian_job_request_notify"
        data["role"] = auth.current_user.role
	message = json.dumps(data)
        subject = jobid
        client = client.publish(TopicArn=topic_arn,Message=message,Subject=subject)

	return get_annotations_list()
'''
*******************************************************************************
List all annotations for the user
*******************************************************************************
'''
@route('/annotations', method='GET', name="annotations_list")
def get_annotations_list():
	auth.require(fail_redirect='/login?redirect_url=' + request.url)
	username = auth.current_user.username
	region_name=request.app.config['mpcs.aws.app_region']
	table_name = request.app.config['mpcs.aws.dynamodb.annotations_table']
        dynamodb = boto3.resource('dynamodb',region_name=region_name)
        
	print username
	print region_name
	print table_name

	ann_table = dynamodb.Table(table_name)
        response = ann_table.query(IndexName='username_index',KeyConditionExpression=Key('username').eq(username))
	print response
	count = response['Count']
	items = response['Items']
	i = 0
	return template(request.app.config['mpcs.env.templates'] + 'my_annotations',
               auth=auth,items=items,count=count ,success=True, error_message=None)

'''
*******************************************************************************
Display details of a specific annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>', method='GET', name="annotation_details")
def get_annotation_details(job_id):
	auth.require(fail_redirect='/login?redirect_url=' + request.url)
        username = auth.current_user.username
        region_name=request.app.config['mpcs.aws.app_region']
        table_name = request.app.config['mpcs.aws.dynamodb.annotations_table']
        dynamodb = boto3.resource('dynamodb',region_name=region_name) 
	ann_table = dynamodb.Table(table_name)
	response = ann_table.get_item(Key={'job_id':job_id})
	#print response
	count = -1
	item={}
	if response.has_key("Item"):
        	item = response['Item']
		count = 1

	if count > 0 and item.has_key("complete_time"):
		 complete_time = item["complete_time"]
	else:
		if count > 0:
			item["complete_time"] = "Waiting to be done"
	url = ""
	in_glacier = False

	if count > 0 and item["job_status"]=="COMPLETED":
		session = botocore.session.get_session()
 		aws_access_key_id = str(session.get_credentials().access_key)
  		aws_secret_access_key = str(session.get_credentials().secret_key)
  		aws_session_token = str(session.get_credentials().token)
		s3 = boto3.client('s3',region_name=region_name)
		input_file_name = item["input_file_name"]
		input_file_name = input_file_name.replace(".vcf",".annot.vcf")
		url = s3.generate_presigned_url(
      				ClientMethod='get_object',
              			Params={
                  		'Bucket':request.app.config['mpcs.aws.s3.results_bucket'],
                  		'Key':request.app.config['mpcs.aws.s3.key_prefix']+username+"/"+job_id+"~"+input_file_name
              	      })
        	dateStr = item["complete_time"]
        	complete_time = datetime.datetime.strptime(dateStr, "%Y-%m-%d;%H:%M")
        	curtime = time.strftime('%Y-%m-%d;%H:%M',time.localtime(time.time())) 
        	current_time = datetime.datetime.strptime(curtime, "%Y-%m-%d;%H:%M")
        	diff_time =  (current_time-complete_time).total_seconds() 
		if diff_time > 1800 and auth.current_user.role=="free_user":
			in_glacier = True
	return template(request.app.config['mpcs.env.templates'] + 'my_jobs_details',
               auth=auth,count=count,item=item,url=url,in_glacier=in_glacier ,success=True, error_message=None)

'''
*******************************************************************************
Display the log file for an annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>/log', method='GET', name="annotation_log")
def view_annotation_log(job_id):
	auth.require(fail_redirect='/login?redirect_url=' + request.url)
        username = auth.current_user.username
        region_name=request.app.config['mpcs.aws.app_region']
        table_name = request.app.config['mpcs.aws.dynamodb.annotations_table']
        dynamodb = boto3.resource('dynamodb',region_name=region_name) 
        ann_table = dynamodb.Table(table_name)
        response = ann_table.get_item(Key={'job_id':job_id})
	count = -1
	item = {}
	if response.has_key("Item"):
        	item = response['Item']
        	count = 1
        
	if count > 0 and item.has_key("complete_time"):
                 complete_time = item["complete_time"]
        else:
                if count > 0:
                        item["complete_time"] = "Waiting to be done"
        data = ""
        if count > 0 and item["job_status"]=="COMPLETED":
                session = botocore.session.get_session()
                aws_access_key_id = str(session.get_credentials().access_key)
                aws_secret_access_key = str(session.get_credentials().secret_key)
                aws_session_token = str(session.get_credentials().token)
                s3 = boto3.resource('s3',region_name=region_name)
                input_file_name = item["input_file_name"]
                input_file_name = input_file_name.replace(".vcf",".count.log")
		obj = s3.Object(request.app.config['mpcs.aws.s3.results_bucket'],request.app.config['mpcs.aws.s3.key_prefix']+username+"/"+job_id+"~"+input_file_name)
		data = obj.get()['Body'].read().decode('utf-8')
        #print data

	return template(request.app.config['mpcs.env.templates'] + 'my_job_log',
               auth=auth,count=count,item=item,data=data ,success=True, error_message=None)


#This is used to test my app.
#You can also use this to test my app.
@route('/downgrade', method='GET')
def downgrade():
	 auth.current_user.update(role="free_user")
### EOF
