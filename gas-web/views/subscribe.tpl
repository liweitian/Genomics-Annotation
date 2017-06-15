<!--
subscribe.tpl - Get user's credit card details to send to Stripe service
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')
<!-- Captures the user's credit card information and uses Javascript to send to Stripe -->

<div class="container">
	<div class="page-header">
		<h2>Subscribe</h2>
	</div>

	<p>You are subscribing to the GAS Premium plan. Please enter your credit card details to complete your subscription.</p><br />

		<form role="form" action="{{get_url('subscribe_submit')}}" method="post" id="subscribe_form" name="subscribe_submit">
			Credit Card Number<input class="form-control input-lg required" type="text" size="20" data-stripe="number" />
			Your Name<input class="form-control input-lg required" type="text" size="20" data-stripe="name" />
			CVC<input class="form-control input-lg required" type="text" size="20" data-stripe="cvc" />
			Expiration Month<input class="form-control input-lg required" type="text" size="20" data-stripe="exp-month" />
			Expiration Year<input class="form-control input-lg required" type="text" size="20" data-stripe="exp-year" />
			<input id="bill-me" class="btn btn-lg btn-primary" type="submit" value="Subscribe"/>	
</div> <!-- container -->


%rebase('views/base', title='GAS - Subscribe')
