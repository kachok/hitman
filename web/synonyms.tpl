<html>
<head>
  <title>Find synonyms for English words</title>
  <link rel="stylesheet" href="/static/main.css" type="text/css" />
    
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>

  <!--script type="text/javascript" src="static/mturk.js"></script-->
  <script type="text/javascript" src="/static/jquery.cookie.js"></script>
  
  
</head>
<body>
  <script>
	var HITtype="{{params['hit_type']}}";
	var IP="74.125.45.100";
	
 $.getJSON("http://api.ipinfodb.com/v3/ip-city/?key={{params["ipinfodb_key"]}}&ip=74.125.45.100&format=json&callback=?",function(data) {
    //alert("Location Data: " + data['cityName']+", "+data['regionName']);
	$("#debug").html($("#debug").html()+"city: "+data['cityName']+"<br/>");
	$("#debug").html($("#debug").html()+"region: "+data['regionName']+"<br/>");
	
	$("#ip").val(data['ipAddress']);
	$("#city").val(data['cityName']);
	$("#region").val(data['regionName']);
	
	//countryCode, countryName, zipCode, 
	/* Format of JSON response from IP Info DB
	{
		"statusCode" : "OK",
		"statusMessage" : "",
		"ipAddress" : "74.125.45.100",
		"countryCode" : "US",
		"countryName" : "UNITED STATES",
		"regionName" : "CALIFORNIA",
		"cityName" : "MOUNTAIN VIEW",
		"zipCode" : "94043",
		"latitude" : "37.3956",
		"longitude" : "-122.076",
		"timeZone" : "-08:00"
	}
	*/
    }); 

	//add show/hide events to words/help (3 sentences with word usage)
	function add_wordhandler(i){
		$("#word"+i+"in").focus(function(){
			$("#word"+i+"help").show();
			
		});
		$("#word"+i+"in").blur(function(){
			$("#word"+i+"help").hide();
			validate_form();
		});
		$("#word"+i+"in").keypress(function(){
			validate_form();
		});
	};


 $.getJSON("/words?hitid={{params['hitid']}}", function(data) {
	for (word in data["words"]){
		//alert(data["words"][word]["word"]);
		$("#word"+word).html(data["words"][word]["word"]);


		html='<tr><td id="word'+word+'">'+data["words"][word]["word"]+'</td><td><input id="word'+word+'in" type="text" name="word'+word+'" size="50"></input><br/><div id="word'+word+'help" style="display:none">help</div></td></tr>';
		//alert(html);
		
		$("#word_table").html($("#word_table").html()+html);


	}
	for (i=0;i<10;i++){
		add_wordhandler(i);

	}


    }); 

    
 $.getJSON("/ip", function(json) {
    //alert("JSON Data: " + json.ip);
	$("#debug").html($("#debug").html()+"IP: "+json.ip+"<br/>");
    }); 

		function getParameterByName(name)
		{
		  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
		  var regexS = "[\\?&]" + name + "=([^&#]*)";
		  var regex = new RegExp(regexS);
		  var results = regex.exec(window.location.href);
		  if(results == null)
		    return "";
		  else
		    return decodeURIComponent(results[1].replace(/\+/g, " "));
		};


 		$(document).ready(function() {
			// Handler for .ready() called.
			//alert(getParameterByName("assignmentId"));
		    //alert(getParameterByName("hitId"));
              //alert("?");
              //debugger;
			var assignmentId=getParameterByName("assignmentId");
			
			if (assignmentId=="ASSIGNMENT_ID_NOT_AVAILABLE" || assignmentId=='')
			{
				$("#preview_panel").show();
				$("#submitbutton").hide();
			}


			$("#assignmentId").val(getParameterByName("assignmentId"));
			$("#hitId").val(getParameterByName("hitId"));
			//alert(getParameterByName("assignmentId"));
			
			$("#debug").html($("#debug").html()+"assignmentId: "+getParameterByName("assignmentId")+"<br/>");
			$("#debug").html($("#debug").html()+"hitId: "+getParameterByName("hitId")+"<br/>");


			$('#mainform').submit(function(){
			  // your validation code
			});
			
			
			//disable/enable form submit (when input is valid)
			function form_valid(param)
			{
				if (param){
					$("#submitbutton").removeAttr('disabled');
					$("#form_validation").hide();
				}
				else{
					$("#submitbutton").attr("disabled", "disabled");
					$("#form_validation").show();
				}
				
			};
			
			//function with form validation for translation of 10 words
			function validate_form(){
				form_valid(true);

				for (i=1;i<=10;i++){
					if ($("#word"+i).val()=="") {
						form_valid(false);
						break;
					};
				};
				
			};
			
			
			

		});   
   
  </script>
  
  <h1>Synonyms in English</h1>
  <table width="100%">
  	<tr>
     	<td width="*">
  <div id="instructions">
	<p>This HIT is only for people who speak English.</p>
	            <p>Please&nbsp;<b>do not use</b>&nbsp;translation software or online machine translation systems like Google translate.&nbsp;Please make sure that your English translation:</p>
	            <ul>
	                <li>Does not add or delete any information from the original text</li>
	            </ul>
    <a href="" id="hide_instructions">hide instructions</a>
  </div>
  <div id="instructions2"  style="display:none;">
    <a  href="" id="show_instructions">show instructions</a>
  </div>
	<br/>
	<div id="preview_panel" style="display:none;">
		This is just a preview! You MUST accept the HIT before you can submit the results.
	</div>

     	</td>

		<td width="250px" rowspan="2" valign="top">
  			%include templates/consent.tpl
  		</td>
  		
  	</tr>
  	<tr>
  		<td valign="top" >
  			<!-- This POST method is posting to the sandbox worker site-->
              <form id="mainform" method="GET" action="http://workersandbox.mturk.com/mturk/externalSubmit">
              <!-- This POST method is posting to the production worker site-->
              <!--<form method="POST" action="http://www.mturk.com/mturk/externalSubmit">-->
	              <input type="hidden" id="assignmentId" name="assignmentId" value=""/>
	              <input type="hidden" id="hitId" name="hitId" value=""/>
	              <input type="hidden" id="ip" name="ip" value=""/>
	              <input type="hidden" id="city" name="city" value=""/>
	              <input type="hidden" id="region" name="region" value=""/>
              

				<div id="user_survey">
		  			%include templates/englishspeakersurvey.tpl
				</div>

				<div id="words_panel">
					<h3>Task</h3>
					<table id="word_table">
						<tr>
							<td>
								<h4>Main word</h4>
								</td>
							</tr>
							<tr>
								<td> Synonym #1 <br/>
									  <input type="radio" name="synonym" value='notaword'>Synonym</input>
									  <input type="radio" name="synonym"  value='notaword'>Antonym (opposite meaning)</input>
									  <input type="radio" name="synonym"  value='englishword'>Other (not related word)</input>
									  <input type="radio" name="synonym"  value='notaword'>Not a word (gibberish/HTML formatting/special characters)</input>
									
									</td>
								</tr>
								<tr>
									<td> Synonym #2 <br/>
										  <input type="radio" name="synonym" value='notaword'>Synonym</input>
										  <input type="radio" name="synonym"  value='notaword'>Antonym (opposite meaning)</input>
										  <input type="radio" name="synonym"  value='englishword'>Other (not related word)</input>
										  <input type="radio" name="synonym"  value='notaword'>Not a word (gibberish/HTML formatting/special characters)</input>

										</td>
									</tr>
					</table>
				</div>

				<input id="submitbutton" type="submit" value="Done!" disabled="disabled"/>
				<div id="validation_text">
					All ten translation should be completed before this HIT can be submitted.
				</div>
				
  			</form>
  			
  			
  			
<div id="debug">
	<h3>Debug:</h3>
</div>
  		</td>
  	</tr>
  </table>



%include templates/instructions_js

</body>
</html>