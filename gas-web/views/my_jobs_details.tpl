<!--
upload.tpl - Direct upload to Amazon S3 using signed POST request
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">

	<div class="page-header">
		<h2>Annotation Details</h2>
	</div>
	
	<div class="container">
		%if count > 0 and auth.current_user.username==item["username"]:
		<ul>
 			<li>Request ID: {{item["job_id"]}}</li>
  			<li>Request Time:{{item["submit_time"]}}</li>
  			<li>VCF Input File:{{item["input_file_name"]}}</li>
			<li>Status:{{item["job_status"]}}</li>
			<li>Complete Time:{{item["complete_time"]}}</li>
		</ul>
		<hr>
		<ul>
			%if url != "":
				%if in_glacier:
					<a href="{{get_url('subscribe')}}">Upgrade to download result file</a>
				%else:
					<li>Annotated Results File:<a href={{url}}>Download</a>
				%end
			<li>Annotation Log File:<a href="/annotations/{{item["job_id"]}}/log">View</a>
			%else:
			<li>Annotated Results File: Please Wait
			<li>Annotation Log File: Please Wait
			%end
			<hr>
		</ul>
		%else:
			<h3>Not authorized to view this job</h3>
		%end
		
		<a href="{{get_url('annotations_list')}}">back to annotations list</a>
	</div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Annotate')
