if ($.cookie(survey_name)!=null)
    {

	  load_survey_data();
      //alert("instructions !=null");
      $("#survey").hide();
	  $("#survey2").show();
    }
    //$.cookie("test","test message");
    //alert("cookie test:"+ $.cookie("test"));


//if ($.cookie(HITtype+"_instructions")!=null)
//    {
//      
//      //alert("instructions !=null");
//      $("#instructions").hide();
//	  $("#instructions2").show();
//    }
    //$.cookie("test","test message");
    //alert("cookie test:"+ $.cookie("test"));

function show_survey()
    {
      $("#survey").toggle();
      $("#survey2").toggle();
      //$.cookie(HITtype+"_instructions",null);
		return false;
    }

function hide_survey()
    {
	  
		if (validate_survey()) {}
	
		save_survey_data()
      $("#survey").toggle();
      $("#survey2").toggle();
		return false;}
		else {
			
			alert ("Please, answer all questions in the survey.")
			return false;
		}
    }

    $("#show_survey").click(show_survey);
    $("#hide_survey").click(hide_survey);


	$("#submitbutton").click(save_survey_data());