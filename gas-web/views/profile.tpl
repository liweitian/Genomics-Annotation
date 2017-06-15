<!--
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<div class="container">

	<div class="page-header">
		<h2>Annotation Details</h2>
	</div>
	
	<div class="container">
		<ul>
 			<li>Username: {{auth.current_user.username}}</li>
  			<li>Level:{{auth.current_user.role}}</li>
  			<li>Full name:{{auth.current_user.description}}</li>
			<li>Email:{{auth.current_user.email_addr}}</li>
		</ul>
		<hr>
		%if auth.current_user.role == "free_user":		
			<h3>Upgrade now to have extra privileges</h3>
			<button onClick="window.open('/subscribe')">Upgrade</button>
 		%end		
	</div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Annotate')
