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
			<p>{{data}}</p>
		%else:
			<h3>Not authorized to view this job</h3>
		%end
		
		<a href="{{get_url('annotations_list')}}">back to annotations list</a>
	</div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Annotate')
