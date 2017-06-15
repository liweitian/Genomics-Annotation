import download_glacier
import results_notify
import upload_glacier

if __name__ == "__main__":
	while True:
		print "start sending email"
		results_notify.send_result()
		print "upload to glacier"
		upload_glacier.sendTo_glacier()
		print "downfrom glacier"
		download_glacier.download()
