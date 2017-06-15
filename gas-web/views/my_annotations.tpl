<!--
upload.tpl - Direct upload to Amazon S3 using signed POST request
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">

	<div class="page-header">
		<h2>My requests</h2>
	</div>
	
	<div class="container">
		<div class="row clearfix">
			<div class="col-md-6 column">
			         Job ID
                	</div>
			<div class="col-md-2 column">
                        	 Submit Time                       
			</div>
			<div class="col-md-2 column">
		        	Input File Name
                	</div>
                	<div class="col-md-2 column">
		        	Status
               		</div>
		</div>
		<div class="row clearfix">
			%for i in range(0,count):
			<div class="col-md-6 column">
				<a href=https://liweitian.ucmpcs.org/annotations/{{items[i]["job_id"]}}>{{items[i]["job_id"]}}</a>
			</div>
			<div class="col-md-2 column">
				{{items[i]["submit_time"]}}
			</div>
			<div class="col-md-2 column">
				{{items[i]["input_file_name"]}}
			</div>
               		<div class="col-md-2 column">
				{{items[i]["job_status"]}}		
			</div>
			%end
		</div>
	</div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Annotate')
