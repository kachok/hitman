<script>
if ($.cookie(HITtype+"_instructions")!=null)
    {
      
      //alert("instructions !=null");
      $("#instructions").hide();
	  $("#instructions2").show();
    }
    //$.cookie("test","test message");
    //alert("cookie test:"+ $.cookie("test"));

 function show_instructions()
    {
      $("#instructions").toggle();
	  $("#instructions2").toggle();
      $.cookie(HITtype+"_instructions",null);
	  return false;
    }
function hide_instructions()
    {
      $("#instructions").toggle();
	  $("#instructions2").toggle();
      $.cookie(HITtype+"_instructions","hide");
	  return false;
    }

    $("#show_instructions").click(show_instructions);
    $("#hide_instructions").click(hide_instructions);

</script>
