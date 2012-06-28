<html>
<head>
  <title>Are those two sentences have similar meaning?</title>
  <link rel="stylesheet" href="/static/main.css" type="text/css" />
    
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>

  <!--script type="text/javascript" src="static/mturk.js"></script-->
  <script type="text/javascript" src="/static/jquery.cookie.js"></script>
  
  
</head>
<body>
  <script>
	var HITtype="{{params['hit_type']}}";
	var ip="{{params['ip']}}";
	var total=0;
	var pairs={};
	
 $.getJSON("http://api.ipinfodb.com/v3/ip-city/?key={{params["ipinfodb_key"]}}&ip="+ip+"&format=json&callback=?",function(data) {
    //alert("Location Data: " + data['cityName']+", "+data['regionName']);
	$("#debug").html($("#debug").html()+"city: "+data['cityName']+"<br/>");
	$("#debug").html($("#debug").html()+"region: "+data['regionName']+"<br/>");
	
	$("#ip").val(data['ipAddress']);
	$("#city").val(data['cityName']);
	$("#region").val(data['regionName']);
	$("#country").val(data['countryName']);
	$("#zipcode").val(data['zipCode']);
	$("#lat").val(data['latitude']);
	$("#lng").val(data['longitude']);	
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

		/*		v=$('input[name=pair_0000009431]:checked').val();
		alert(v);
		alert(v==undefined);

		for (pair in pairs){
			alert(pairs[pair]);
		}
		

		alert(pairs);
		*/

		for (pair in pairs){
			v=$('input[name=pair_'+pairs[pair]["pair_id"]+']:checked').val();
			//alert(pairs[pair]["pair_id"]+" "+v+" "+(v==undefined));
			
			if (v==undefined)
			{
				form_valid(false);
				break;
			}

		};
		
	};
	
	//add show/hide events to words/help (3 sentences with word usage)
	function add_pairhandler(i){
		$("input[name=pair_"+i+"]").change(function(){
			validate_form();
		});

		$("input[name=pair_"+i+"]").click(function(){
			validate_form();
		});
	};
	




    
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
			
			


		});   
   
  </script>
  
  <h1>Are those two sentences have similar meaning?</h1>
  <table width="100%">
  	<tr>
     	<td width="*">
  <div id="instructions">
	<p>This HIT is only for people who speak English.</p>
	            <ul>
					<li>There are 5 identical sections.</li>
					<li>For each section you need to answer three questions.</li>
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
	              <input type="hidden" id="country" name="country" value=""/>
	              <input type="hidden" id="zipcode" name="zipcode" value=""/>
	              <input type="hidden" id="lat" name="lat" value=""/>
	              <input type="hidden" id="lng" name="lng" value=""/>
              

				<div id="user_survey">
		  			%include templates/englishspeakersurvey.tpl
				</div>


				<div id="words_panel">
					<h3>Are those two sentences have similar meaning?</h3>
					<table id="word_table" width="100%">
						%for word in params['words']:
						<tr>
							<td colspan="2">
								1) Does this two sentences have the same meaning?
								<br/>
								<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='yes'>Yes &nbsp; 
								<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='no'>No &nbsp;
								<br/>

							</td>
						</tr>
						<tr>
							<td width="50%">
								<b>{{word['translation']}}</b>
								<br/>
								<br/>
							</td>
							<td width="50%">
								<b>{{word['similar_sentence']}}</b>
								<br/>
								<br/>
							</td>
						</tr>
						
						<tr>
							<td colspan="2">
								2) Does this sentence looks like it was machine translated?
								<br/>
								<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='yes'>Yes &nbsp; 
								<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='no'>No &nbsp;
								<br/>
							</td>
						</tr>
						<tr>
							<td colspan="2">
								<b>{{word['translation']}}</b>
								<br/>
								<br/>
							</td>
						</tr>
						<tr>
							<td width="50%">
								Example of translation by Google:<br/>
								{{word['google']}}
								<br/>
								<br/>
							</td>
							<td width="50%">
								Example of translation by Bing:<br/>
								{{word['bing']}}
								<br/>
								<br/>
							</td>
						</tr>
						
						<tr>
							<td colspan="2">
								3) Is this translation good enough? or should it be re-translated (e.g. is it grammatically correct English sentence and look like professional translation or not?)
								<br/>
								<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='yes'>Yes &nbsp; 
								<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='no'>No &nbsp;
								<br/>
							</td>
						</tr>
						<tr>
							<td colspan="2" align="center">
							<hr/>
							</td>
						</tr>
						%end

					</table>
				</div>

				<input id="submitbutton" type="submit" value="Done!" disabled="disabled"/>
				<div id="validation_text">
					All pairs should be completed before this HIT can be submitted.
				</div>
				
  			</form>
  			
  			
  			
<div id="debug" style="display:none">
	<h3>Debug:</h3>
</div>
  		</td>
  	</tr>
  </table>



%include templates/instructions_js

</body>
</html>