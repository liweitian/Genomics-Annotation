Reference:
#https://docs.python.org/2/library/
#https://bottlepy.org/docs/dev/
#http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingHTTPPOST.html
#https://boto3.readthedocs.io/en/latest/guide/migrations3.html

All my code refer from the above four links if necessary.


file "answer" includes answers to (Q7 Archive Free user data to Glacier Q9 Restore data for users that upgrade to Premium. Q13. Test under load using Locust)

ann_test.py is used to test auto scaling annotator. 
Note: this script may cause program in the annotator instance stop. Hence, please use this script at last. Or terminate liweitian-capstone-annotator, then it will launch two new instances automatically.

gas-annotator is for capstone-annotator.
gas-web is for capstone-webserver, where you can find all templates and configuration file.

utility is for some utility scripts.


Bonus part: I also implements the file size limited when free_user uploads. I used Amazon policy condition.

One more thing: when you register a new user. You will receive an email, which includes a link for confirmation. When you click the link, you may see an error.(The last time I test, this error was gone) This error does not affect you register a new user. You can go on to login.

When a job is finished, a notification will be sent to your email. Please double check your email spam folder.
