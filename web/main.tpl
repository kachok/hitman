<html>
<head>
  <title>Content Title</title>
  <link rel="stylesheet" href="static/main.css" type="text/css" />
    
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>

  <!--script type="text/javascript" src="static/mturk.js"></script-->
  <script type="text/javascript" src="static/jquery.cookie.js"></script>
  
  
</head>
<body>
  <script>
	var HITtype="{{params['hit_type']}}";
	var IP="74.125.45.100";
	
 
 $.getJSON("http://api.ipinfodb.com/v3/ip-city/?key={{params["ipinfodb_key"]}}&ip=74.125.45.100&format=json&callback=?",function(data) {
    //alert("Location Data: " + data['cityName']+", "+data['regionName']);
	$("#debug").html($("#debug").html()+"city: "+data['cityName']+"<br/>");
	$("#debug").html($("#debug").html()+"region: "+data['regionName']+"<br/>");
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
			}


			$("#assignmentId").val(getParameterByName("assignmentId"));
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
			
			
			
			//add show/hide events to words/help (3 sentences with word usage)
			function add_wordhandler(i){
				$("#word"+i).focus(function(){
					$("#word"+i+"help").show();
					
				});
				$("#word"+i).blur(function(){
					$("#word"+i+"help").hide();
					validate_form();
				});
				$("#word"+i).keypress(function(){
					validate_form();
				});
			};

			for (i=1;i<=10;i++){
				add_wordhandler(i);
				
			}
		});   
   
  </script>
  
  <h1>Vocabulary HIT</h1>

  <table width="100%">
  	<tr>
     	<td colspan="2">
  <div id="instructions">
    This is just an instructions for vocabulary HIT!
	<br/>
    <a href="" id="hide_instructions">hide disclaimer</a>
  </div>
  <a  href="" id="show_instructions" style="display:none;">show instructions</a>
     	</td>
  	</tr>
  	<tr>
  		<td width="*" valign="top">
  			Main content and  Form goes here .
  			
  			<!-- This POST method is posting to the sandbox worker site-->
              <form id="mainform" method="POST" action="http://workersandbox.mturk.com/mturk/externalSubmit">
              <!-- This POST method is posting to the production worker site-->
              <!--<form method="POST" action="http://www.mturk.com/mturk/externalSubmit">-->
              <input type="hidden" id="assignmentId" name="assignmentId" value=""/>
              
        		Word 1: <input id="word1" type="text" name="word1" size="50"></input><br/>
				<div id="word1help" style="display:none;">
					here are 3 sentences how this word is used:<br/>
					Sentence 1,<br/>
					Sentence 2,<br/>
					Sentence 3<br/>
				</div>
          		Word 2: <input id="word2" type="text" name="word2" size="50"></input><br/>
				<div id="word2help" style="display:none;">
					here are 3 sentences how this word is used:<br/>
					Sentence 1,<br/>
					Sentence 2,<br/>
					Sentence 3<br/>
				</div>
				Word 3: <input id="word3" type="text" name="word3" size="50"></input><br/>
				<div id="word3help" style="display:none;">
					here are 3 sentences how this word is used:<br/>
					Sentence 1,<br/>
					Sentence 2,<br/>
					Sentence 3<br/>
				</div>
          		Word 4: <input id="word4" type="text" name="word4" size="50"></input><br/>
          		Word 5: <input id="word5" type="text" name="word5" size="50"></input><br/>
          		Word 6: <input id="word6" type="text" name="word6" size="50"></input><br/>
          		Word 7: <input id="word7" type="text" name="word7" size="50"></input><br/>
          		Word 8: <input id="word8" type="text" name="word8" size="50"></input><br/>
          		Word 9: <input id="word9" type="text" name="word9" size="50"></input><br/>
          		Word 10: <input id="word10" type="text" name="word10" size="50"></input><br/>
          		
				<input id="submitbutton" type="submit" value="Done!" disabled="disabled"/>
				<div id="validation_text">
					All ten translation should be completed before this HIT can be submitted.
				</div>
				
				<div id="preview_panel">
					This is just a preview of this HIT type!
				</div>
  			</form>
  			
  			
  			
Debug:
<div id="debug">
</div>
  		</td>
  		<td width="250px">
  			%include templates/consent.tpl
  		</td>
  	</tr>
  </table>


<script>

if ($.cookie(HITtype+"_instructions")!=null)
    {
      
      //alert("instructions !=null");
      $("#instructions").hide();
	  $("#show_instructions").show();
    }
    //$.cookie("test","test message");
    //alert("cookie test:"+ $.cookie("test"));

 function show_instructions()
    {
      $("#instructions").toggle();
      $.cookie(HITtype+"_instructions",null);
    }
function hide_instructions()
    {
      $("#instructions").toggle();
      $.cookie(HITtype+"_instructions","hide");
    }

    $("#show_instructions").click(show_instructions);
   
    $("#hide_instructions").click(hide_instructions);
   
</script>
</body>
</html>