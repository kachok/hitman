<html>
<head>
 <title>Correct English grammar and language errors made by foreign speakers of English</title> 
  <link rel="stylesheet" href="/static/main.css" type="text/css" />
    
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>

<link
	href="http://ajax.googleapis.com/ajax
	/libs/jqueryui/1.8/themes/base/jquery-ui.css"
	rel="stylesheet" type="text/css" />
<!--script
	src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script-->
<script
	src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>


  <!--script type="text/javascript" src="/static/mturk.js"></script-->
  <script type="text/javascript" src="/static/jquery.cookie.js"></script>
  
<style type="text/css">
div.correct {
	background-color: #FFFFFF;
}

div.highlight {
	background-color: yellow;
}

div.tmp_highlight {
	background-color: lightgreen;
}

div.highlight_for_deletion {
	background-color: red;
}

div.hover {
	background-color: grey;
}

/*from http://www.elated.com/articles/drag-and-drop-with-jquery-your-essential-guide/ tutorial */
div.space {
	width: 30px;
	height: 30px;
	padding: 2px;
	border: 2px solid #333;
	border-style: dashed;
	-moz-border-radius: 10px;
	-webkit-border-radius: 10px;
	border-radius: 10px;
}

div.word {
	padding: 4px;
	border: 2px solid #333;
	-moz-border-radius: 10px;
	-webkit-border-radius: 10px;
	border-radius: 10px;
	-moz-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	-webkit-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	font-size: 16px;
	text-align: center;
}

div.corrected_word {
	padding: 4px;
	border: 2px solid #333;
	-moz-border-radius: 10px;
	-webkit-border-radius: 10px;
	border-radius: 10px;
	-moz-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	-webkit-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	font-size: 16px;
	text-align: center;
}

div.edited {
	text-align: center;
}

div.orig {
	text-align: center;
}

div.active {
	color: #0066FF;
	font-weight: bold;
}

div.inactive {
	color: grey;
}

button {
	padding: 6px;
	border: 1px solid #333;
	-moz-border-radius: 10px;
	-webkit-border-radius: 10px;
	border-radius: 10px;
	-moz-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	-webkit-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	box-shadow: 0 0 .3em rgba(0, 0, 0, .8); */
	font-size: 16px;
	background-color: #FFFFFF;
	-moz-border-radius: 10px;
	-webkit-border-radius: 10px;
	border-radius: 10px;
	-moz-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	-webkit-box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
	box-shadow: 0 0 .3em rgba(0, 0, 0, .8);
}

button.clicked {
	background-color: lightblue;
}

button.hover {
	background-color: lightblue;
}

select {
	background-color: #FFFFFF;
}

input {
	background-color: #FFFFFF;
}

input.img {
	background-colo: red;
}

A:link {
	text-decoration: none;
	color: black;
}

A:visited {
	text-decoration: none;
	color: black;
}

A:active {
	text-decoration: none;
	color: black;
}

A:hover {
	text-decoration: none;
	color: black;
}

body {
	color: black;
	font-size: 16px;
}
//
</style>

<!--from tutorial at http://www.kriesi.at/archives/create-a-multilevel-dropdown-menu-with-css-and-improve-it-via-jquery -->

<style type="text/css">
#nav, #nav ul{
     margin:0;
     padding:0;
     list-style-type:none;
     list-style-position:outside;
     position:relative;
     line-height:1.0em;
 }

 #nav a:link, #nav a:active, #nav a:visited{
    display:block;
    padding:0px 5px;
    border:1px solid #333;
    color:#fff;
    text-decoration:none;
    background-color:#333;
 }

#nav a:hover{
    background-color:#fff;
    color:#333;
}

#nav a{
    display:block;
    padding:0px 5px;
    border:1px solid #333;
    color:#333;
    text-decoration:none;
    background-color:#fff;
}

a.chosen{
    display:block;
    padding:0px 5px;
    border:1px solid #333;
    color:#333;
    text-decoration:none;
    background-color:#fff;
    text-align: center;
}

#nav a.desc{
    background-color: lightblue;
    color:#333;
    text-align:center;
    font-size:14px;
    line-height:0.8em;
    width:22em
}

#nav li{
    float:left;
    position:relative;
}

#nav ul {
    position:absolute;
    width:10em;
    top:1.0em;
    display:none;
}

#nav li ul a{
    width:10em;
    top:1.0em;
    float:left;
}

#nav ul ul{
	top:auto;
	}

#nav li ul ul {
    left:10em;
    margin:0px 0 0 10px;
    }

#nav li:hover ul ul, #nav li:hover ul ul ul, #nav li:hover ul ul ul ul, #nav li:hover ul ul ul ul ul{
    display:none;
    }
#nav li:hover ul, #nav li li:hover ul, #nav li li li:hover ul, #nav li li li li:hover ul, #nav li li li li li:hover ul{
    display:block;
    }

</style>

<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
<link
	href="http://ajax.googleapis.com/ajax
	/libs/jqueryui/1.8/themes/base/jquery-ui.css"
	rel="stylesheet" type="text/css" />
<!--script
	src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script-->
<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>

<script type="text/javascript" src="/static/jquery.qtip-1.0.0-rc3.min.js"></script>

<script type="text/javascript" src="/static/ESLHIT.js"></script>

  
</head>
<body>
  <script>
	var HITtype="{{params['hit_type']}}";
	var ip="{{params['ip']}}";
	var total=0;
	var pairs={};
	var sentences = [
	
	
	%for sentence in params['sentences']:
	"{{sentence["sentence"]}}",
	%end
	
			
			];
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
/*Format of JSON response from IP Info DB
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
/*
				v=$('input[name=pair_0000009431]:checked').val();
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
	

/*
 $.getJSON("/synonyms?hitId={{params['hitid']}}", function(data) {
	total=data["total"];
	pairs=data["words"]
	for (word in data["words"]){
		//alert(data["words"][word]["word"]);
		$("#word"+word).html(data["words"][word]["word"]);

		c="";
		if ((word%2)?false:true){
			//even
			c=' class="even" ';
		}
		else{
			c=' class="odd" ';
		}


		options="<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='yes'>Yes &nbsp;"+
		  "<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='no'>No &nbsp;"+
		  "<input type='radio' name='pair_"+data["words"][word]["pair_id"]+"' value='related'>Related but not synonymous &nbsp;";
		
		
		checks="<br/>"+
		"<input type='checkbox' name='misspelled_"+data["words"][word]["pair_id"]+"' value='misspelled' /> Word is misspelled <br/>";


		//html='<tr><td id="word'+word+'">'+data["words"][word]["word"]+'</td><td><input id="word'+word+'in" type="text" name="word'+word+'" size="50"></input><br/><div id="word'+word+'help" style="display:none">help</div></td></tr>';
		html='<tr><td> <b><a target="_blank" href="http://dictionary.reference.com/browse/'+data["words"][word]["synonym"]+'">'+data["words"][word]["synonym"]+'</a></b> and <b><a target="_blank" href="http://dictionary.reference.com/browse/'+data["words"][word]["translation"]+'">'+data["words"][word]["translation"]+"</a></b><br/>"+options+checks+'</div><br/></td></tr>';


		//alert(html);

		$("#word_table").html($("#word_table").html()+html);


	}
	for (i=0;i<total;i++){
		add_pairhandler(data["words"][i]["pair_id"]);
	}

    });
*/

    
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
  
 <h1>Correct English grammar and language errors made by foreign speakers of English.</h1>
  <table width="100%">
  	<tr>
     	<td width="*">
   <div id="instructions">
	<p>This HIT is only for people who speak English.</p>
	            <ul> Below are 5 English sentences which were written by foreign English speakers. Please correct grammar mistakes and stylistic errors to make the sentences sound fluent.  </ul>
    <!--a href="" id="hide_instructions">hide instructions</a-->
  </div>
  <!--div id="instructions2"  style="display:none;">
    <a  href="" id="show_instructions">show instructions</a>
  </div>--> 
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
		  			<!--%include templates/englishspeakersurvey.tpl-->
				</div> 

				<div id="words_panel">
					<h3>Correct ESL mistakes in these sentences</h3>
					<table id="word_table">
						
					</table>
				</div> 
				
				
				<!--progress bar from http://caffeinatedcode.wordpress.com/2008/04/08/simple-javascript-progress-bar/-->
				<!--<center>-->
				<!--<h4 id="orig" align="center">Original Sentence</h4></center>-->
				<!--p id="current-edits" align="center"></p-->
				<p id="orig" align="center"></p>
				<br>
				<table id="prevNext" cols=4>
					<center>
						<tr>
							<td width="10%" align="center">
								<button id="buttonP" align="right" onClick="return prevSentence()">Previous
									Sentence</button>
							</td><td></td><td></td>
							<td width="10%">
								<button id="buttonN" align="right" onClick="return nextSentence()">Next
									Sentence</button>
							</td>
						</tr></center></table>
				<br>
					<table id="allSentences" cols=4>
					<center>
						<tr>
						<td colspan=2 width="50%">
								<div align="center">Original Sentence</div>
							</td>
							<td colspan=2 width="50%">
								<div align="center">Your Edits</div>
							</td></tr>
						<tr>
							<td colspan=2 width="50%">
								<div class="orig" id="sent0" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">
								<div class="edited" id="edit0" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent1" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit1" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent2" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit2" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent3" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit3" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent4" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit4" align="left">Sentences</div>
							</td>
						</tr>
						<!-- tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent5" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit5" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent6" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit6" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent7" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit7" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent8" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit8" align="left">Sentences</div>
							</td>
						</tr>
						<tr>
							<td colspan=2 width="50%">

								<div class="orig" id="sent9" align="left">Sentences</div>
							</td>
							<td colspan=2 width="50%">

								<div class="edited" id="edit9" align="left">Sentences</div>
							</td>
						</tr-->
					</table>
				</center>
				<!--  What are the different types of errors? <img id="help" src="http://www.homeserviceworld.com/images/vautomulti/icon_question_mark.png"></img>
				-->

				<p id="HITend">Thanks for doing our HIT! Please provide any comments
					that you have about this HIT. We appreciate your input!</p>
				<p>
					<textarea rows="4" cols="80" name="comment" id="commentBox"> </textarea>
					&nbsp;
				</p>

				<p>
					<input type="hidden" name="userDisplayLanguage" /> <input
						type="hidden" name="browserInfo" /> <input type="hidden"
						name="ipAddress" /> <input type="hidden" name="country" /> <input
						type="hidden" name="city" /> <input type="hidden" name="region" />
				</p>
			<!--	
				<script type="text/javascript"
					src="http://gd.geobytes.com/gd?after=-1&variables=GeobytesCountry,GeobytesCity,GeobytesRegion,GeobytesIpAddress"></script>
				 <script type="text/javascript">function getUserInfo() {
					var userDisplayLanguage = navigator.language ? navigator.language : navigator.userDisplayLanguage;
					var browserInfo = navigator.userAgent;
					var country = sGeobytesCountry;
					var city = sGeobytesCity;
					var region = sGeobytesRegion;

					document.mturk_form.userDisplayLanguage.value = userDisplayLanguage;
					document.mturk_form.browserInfo.value = browserInfo;
					document.mturk_form.country.value = country;
					document.mturk_form.city.value = city;
					document.mturk_form.region.value = region;
				}

				getUserInfo();
				 -->
				</script>


				

				<!--input id="submitbutton" type="submit" value="Done!" disabled="disabled"/-->
				<input id="submitbutton" type="submit" value="Done!"/>
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



<!-- %include templates/instructions_js-->

</body>
</html>
