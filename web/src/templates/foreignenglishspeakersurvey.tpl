<div id="survey">
<h3>Language Survey</h3>
<p>First, please answer these questions about your language abilities:</p>
			<input type="hidden" id="surveyname" name="surveyname" value="foreignenglishspeakersurvey_{{lang_name}}"/>
            <table id="surveytable" border="0" cellspacing="0" cellpadding="0">
                <tbody>
                    <tr class="odd">
                        <td>Is {{lang_name}} language your native language?</td>
                        <td><input type="radio" name="survey_is_native_foreign_speaker" value="yes" id="survey_is_native_foreign_speaker_yes"/><label for="survey_is_native_foreign_speaker_yes">Yes</label> 
							<input type="radio" name="survey_is_native_foreign_speaker" value="no" id="survey_is_native_foreign_speaker_no" /><label for="survey_is_native_foreign_speaker_no">No</label> </td>
                    </tr>
                    <tr class="even">
                        <td>How many years have you spoken {{lang_name}} language?</td>
                        <td><input size="4" name="survey_years_speaking_foreign" id="survey_years_speaking_foreign" type="text" /> <span class="answertext">years</span></td>
                    </tr>
                    <tr class="odd">
                        <td>Is English your native language?</td>
                        <td><input type="radio" name="survey_is_native_english_speaker" value="yes" id="survey_is_native_english_speaker_yes"/><label for="survey_is_native_english_speaker_yes">Yes</label> 
							<input type="radio" name="survey_is_native_english_speaker" value="no" id="survey_is_native_english_speaker_no"/><label for="survey_is_native_english_speaker_no">No</label> </td>
                    </tr>
                    <tr class="even">
                        <td>How many years have you spoken English?</td>
                        <td><input size="4" name="survey_years_speaking_english"  id="survey_years_speaking_english" type="text" /> <span class="answertext">years</span></td>
                    </tr>
                    <tr class="odd">
                        <td>What country do you live in?</td>
                        <td><input size="15" name="survey_what_country"  id="survey_what_country" type="text" /></td>
                    </tr>
                    <tr class="even">
                        <td>What country were you born in?</td>
                        <td><input size="15" name="survey_what_country_born" id="survey_what_country_born" type="text" /></td>
                    </tr>
                </tbody>
            </table>
<br/>
  <a href="" id="hide_survey">save survey (cookies must be enabled)</a>
</div>
<div id="survey2"  style="display:none;">
	<div id="survey_summary"></div>
  <a  href="" id="show_survey">change answers</a>
</div>

<script>

var survey_name="foreignenglishspeakersurvey_{{lang_name}}";

function load_survey_data()
//restoring data from cookies into survey form
{
	var foreign_native=$.cookie("survey_is_native_foreign_speaker");
	var foreign_years=$.cookie("survey_years_speaking_foreign");
	var english_native=$.cookie("survey_is_native_english_speaker");
	var english_years=$.cookie("survey_years_speaking_english");
	var what_country=$.cookie("survey_what_country");
	var what_country_born=$.cookie("survey_what_country_born");

	if (foreign_native=="yes"){foreign_native="native";} else {foreign_native="non-native"}
	if (english_native=="yes"){english_native="native";} else {english_native="non-native"}

	var survey_summary="{{lang_name}} ("+foreign_native+") - "+ foreign_years+" years, English ("+english_native+") - "+english_years+" years, lives in "+what_country+" (born in "+what_country_born+")";
	$("#survey_summary").html(survey_summary);
	
	$("[name=survey_is_native_foreign_speaker]").filter("[value="+$.cookie("survey_is_native_foreign_speaker")+"]").prop('checked', true);
	$("#survey_years_speaking_foreign").val($.cookie("survey_years_speaking_foreign"));
	$("[name=survey_is_native_english_speaker]").filter("[value="+$.cookie("survey_is_native_english_speaker")+"]").prop('checked', true);
	$("#survey_years_speaking_english").val($.cookie("survey_years_speaking_english"));
	$("#survey_what_country").val($.cookie("survey_what_country"));
	$("#survey_what_country_born").val($.cookie("survey_what_country_born"));
}

function validate_survey()
{
	if ($('input[name=survey_is_native_foreign_speaker]:checked').val()==null ) return false;
	if ($("#survey_years_speaking_foreign").val()==null ) return false;
	if ($('input[name=survey_is_native_english_speaker]:checked').val()==null ) return false;
	if ($("#survey_years_speaking_english").val()==null ) return false;
	if ($("#survey_what_country").val()==null ) return false;
	if ($("#survey_what_country_born").val()==null ) return false;
	
	return true;
}

function save_survey_data()
//saving survey values into cookie (should be called by form submit)
{
	//mark survey in a cookie
	$.cookie(survey_name,"true");

	$.cookie("survey_is_native_foreign_speaker",$('input[name=survey_is_native_foreign_speaker]:checked').val());
	$.cookie("survey_years_speaking_foreign",$("#survey_years_speaking_foreign").val());
	$.cookie("survey_is_native_english_speaker",$('input[name=survey_is_native_english_speaker]:checked').val());
	$.cookie("survey_years_speaking_english",$("#survey_years_speaking_english").val());
	$.cookie("survey_what_country",$("#survey_what_country").val());
	$.cookie("survey_what_country_born",$("#survey_what_country_born").val());
	load_survey_data();
}

%include templates/survey_js
   
</script>