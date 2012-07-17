//var sentences = [ "${sent0}", "${sent1}", "${sent2}", "${sent3}", "${sent4}", "${sent5}", "${sent6}", "${sent7}", "${sent8}", "${sent9}" ];

// Removed sentences variable and pushed it into ESL.tpl file

var sentences = [
		"Sri Lanka 's forest region was destroyed by agriculture , wooden works , vetinary feeds , etc . ,",
		"several commissions where created to protect the remaining forest region",
		"Sri Lanka is considered as the bird 's sanctionary place .",
		"For further information please see the article on bird sanctionary rights in Indian Subcontinent",
		"There is thousand of animals living in Sri Lanka which includes several Sri Lanka orignated animals .",
		"When we compare the area of Sri lanka 's Island , birds are highly found here .",
		"Apart from the birds that live here , specific number of migrant birds that come from the north pole to avoind their winter season come to SriLanka .",
		"Among the bird species , 233 live in Srilanka , in that 26 belong to intra state .",
		"Others live in the Indian sub continent , however more than 80 of them have special features that are unique to Sri Lanka .",
		"Some of the breeds based on their feather formation characteristics largely differ from the Indian breeds ." ];


var annotations = [];

var words = [ [], [], [], [], [], [], [], [], [], [] ];

var step_list = [ 'spelling', 'prepositions', 'determiners', 'agreement',
		'verbs', 'awk_phrases', 'reorder' ];

var visited = [];

var steps = new Array();
steps['Spelling'] = 'spelling';
steps['Preposition'] = 'prepositions';
steps['Determiner'] = 'determiners';
steps['Agreement'] = 'agreement';
steps['Verb'] = 'verbs';
steps['Awkward Phrase'] = 'awk_phrases';
steps['Reorder'] = 'reorder';
steps['Insert'] = "insert";
steps['Delete'] = "delete";

var defaults = new Array();
defaults['word'] = 'spelling';
defaults['pair'] = 'agreement';
defaults['phrase'] = 'awk_phrases';
defaults['insert'] = 'insert';

var highlighting_modes = new Array();
highlighting_modes['spelling'] = 'word';
highlighting_modes['prepositions'] = 'word';
highlighting_modes['determiners'] = 'word';
highlighting_modes['agreement'] = 'pair';
highlighting_modes['verbs'] = 'word';
highlighting_modes['awk_phrases'] = 'phrase';
highlighting_modes['reorder'] = 'phrase';

var error_type_list = [
'Article', 'Part of Speech', 'Pluralization', 'Infinitive', 'Gerund', 'Passive Voice', 'Verb Tense', 'Negation', 'Subject-Verb Agreement', 
'Verb-Verb Agreement', 'Punctuation', 'Mass Count', 'Repeated Subject/Pronoun', 'Preposition', 'Word Order', 'Adjective Order', 'Split Infinitive',
'Run-on Sentence', 'Fragment', 'Unnecessary Transition']

var instructions = new Array();
instructions['reorder'] = "Drag and drop phrase to new location";
instructions['confirm'] = "Click green check to confirm change";
instructions['insert'] = "Click on open space to insert word";
instructions['modes'] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ '<tr><td colspan=2 align=center>Use buttons to change between different highlighting modes</td>'
		+ '<tr><td width="50%" align=center>Word</td>'
		+ '<td>Select and change individual words. Use to correct spelling errors, incorrect prepositions or determiners, incorrect verb conjugations, or to delete unnecessary words. </td>'
		+ '<tr><td width="50%" align=center>Pair</td>'
		+ '<td>Select pairs of words. Use to correct agreement errors such as subject-verb or pronoun-noun mismatches.</td>'
		+ '<tr><td width="50%" align=center>Phrase</td>'
		+ '<td>Highlight contiguous, multi-word phrases. Use to reorder phrases within a sentence or reword awkward phrases.</td>'
		+ '<tr><td width="50%" align=center>Insert</td>'
		+ '<td>Select empty space between two words in order to insert a word or phrase into the sentence.</td>'
		+ "</table></center>";

var errorChoices = new Array();

errorChoices["all"] = " <ul id=nav> "+ " <li><a>Choose Error Type</a> "+ " <ul> "+ " <li><a>Grammatical</a> "+ " <ul> "+ " <li><a>Article</a> "+ " <ul> "+ " <li><a class=desc><b>Article errors include missing,"+ "extraneous, or incorrect articles.</b><br> <i>Ex.  I go to "+ "store.<br>Ex. I want to be the doctor when I grow up.<br>Ex. "+ "I like to drink the tea. "+ " </i></a></li> "+ " </ul></li> "+ " <li><a>Noun</a> "+ " <ul> "+ " <li><a>Mass Count</a> "+ " <ul> "+ " <li><a class=desc><b>Mass count errors occur when"+ "an article does not match its corresponding noun in number.</b><br> "+ "<i>Ex. I hope you have many success in life. </i></a></li> "+ " </ul></li> "+ " <li><a>Repeat Subject/Pronoun</a> "+ " <ul> "+ " <li><a class=desc><b>Repeated subject errors occur"+ "when an unnecessary pronoun appears, marking a subject which "+ "is already clear from the context of the sentence.</b><br>"+ "<i>Ex. My sister she likes to sing in the shower.</i></a></li> "+" </ul></li> "+ " <li><a>Missing Noun</a> "+ " <ul> "+ " <li><a class=desc><b>Insert nouns that should be present, if possible.</b><br> "+ "</a></li> "+" </ul></li> "+ " <li><a>Other</a> "+ " <ul> "+ " <li><a class=desc><b>Other noun-related errors.</b><br>"+ "</a></li> "+ " </ul></li> "+ " </ul></li> "+ " <li><a>Preposition</a> "+ " <ul> "+ " <li><a class=desc><b>Preposition errors include "+"missing, extraneous, or incorrect prepositions.</b><br> <i>Ex."+ "I go store.<br>Ex. I feel very worried for it.<br>Ex."+ "Let's meet at tomorrow. "+ " </i></a></li> "+ " </ul></li> "+ " <li><a>Punctuation</a> "+ " <ul> "+ " <li><a class=desc><b>You should correct any missing"+ "or incorrectly used punctuation. </b><br> <i>Ex.  I like, "+ "chocolate </i></a></li> "+ " </ul></li> "+ " <li><a>Spelling/Capitalization</a> "+ " <ul> "+ " <li><a class=desc><b>You should correct any misspelled words. </b><br> <i>Ex. I like, "+ "chocolate </i></a></li>"+ " </ul></li> "+ " <li><a>Verb</a> "+ " <ul> "+ " <li><a>Form</a> "+ " <ul> "+ " <li><a>Infinitive</a> "+ " <ul> "+ " <li><a class=desc><b>Mark an infinitive use "+"error when an infinitive (a 'to' verb) is used in place of "+ "a conjugated verb. </b><br> <i>Ex. In the evening, we "+ "to eat dinner. </i></a></li> "+ " </ul></li> "+ " <li><a>Gerund</a> "+ " <ul> "+ " <li><a class=desc><b>Mark a gerund use error "+"when a gerund (an 'ing' verb) is used in place of a "+"conjugated verb. </b><br> <i>In the evening, we "+"eating dinner. </i></a></li> "+ " </ul></li> "+ " <li><a>Passive Voice</a> "+ " <ul> "+ " <li><a class=desc><b>You should correct any "+"awkward or incorrectly-used passive voice. </b><br> <i>Ex."+ "I was slept for 10 hours last night.</i></a></li> "+ " </ul></li> "+ " </ul></li> "+ " <li><a>Tense</a> "+ " <ul> "+ " <li><a class=desc><b>Tense errors should be "+"identified when a verb is in the incorrect tense.</b><br> <i>Ex. "+ "I Yesterday, I go home after school. </i></a></li> "+ " </ul></li> "+ " <li><a>Negation</a> "+ " <ul> "+ " <li><a class=desc><b>Negation errors occur when "+"there is a misplaced or missing 'no' or 'not', or when the"+ "verb is in the wrong form during a negation.</b><br> <i>Ex."+ "I no like this soup.<br>Ex. I didn't swore in front of "+ "my mother. "+ " </i></a></li> "+ " </ul></li> "+ " <li><a>Agreement</a> "+ " <ul> "+ " <li><a>Subject-Verb</a> "+ " <ul> "+ " <li><a class=desc><b>Subject-Verb agreement "+"errors occur when the verb does not match the noun to "+"which it relates in number or in person.</b><br> <i>"+ "Ex. I goes home after school. </i></a></li> "+ " </ul></li> "+ " <li><a>Verb-Verb</a> "+ " <ul> "+ " <li><a class=desc><b>Verb-Verb agreement errors"+ "occur when two verbs in the same sentence appear "+"incorrectly in different tenses.</b><br> <i> Ex.  "+"Yesterday I woke up and going downstairs for breakfast.  </i></a></li>"+ " </ul></li> "+ " </ul> "+ " <li><a>Missing Verb</a> "+ " <ul> "+ " <li><a class=desc><b>Insert verb that should be present, if possible.</b><br></a></li> "+" </ul></li> "+ " <li><a>Other</a> "+ " <ul> "+ " <li><a class=desc><b>Other verb-related errors.</b><br>"+ "</a></li> "+ " </ul></li> "+ " </ul></li> "+ " <li><a>Word Form</a> "+ " <ul> "+ " <li><a>Part of Speech</a> "+ " <ul> "+ " <li><a class=desc><b>Part of speech errors occur"+ "when a form of a word is used in the incorrect part of"+ "speech.</b><br> <i> Ex. I was very delightful about the "+ "good news. </i></a></li> "+ " </ul></li> "+ " <li><a>Pluralization</a> "+ " <ul> "+ " <li><a class=desc><b>You should mark pluralization"+ "errors when a plural of a word includes misplaced "+"apostrophes, missing apostrophes, or wrong word form. </b><br>"+ "<i> Ex. It was in the Stevensons's yard. </i></a></li> "+ " </ul></li> "+ " <li><a>Other</a> "+ " <ul> "+ " <li><a class=desc><b>Other form-related errors.</b><br>"+ "</a></li> "+ " </ul></li> "+ " </ul></li> "+ " <li><a>Wrong Word/Homonyms</a> "+ " <ul> "+ " <li><a class=desc><b>Replace misused words with correct ones if the authors appears to have confused two similar words.</b><br> <i>Ex. Global warming is one affect of carbon emissions.<br>Correction: Global warming is one <b>effect</b> of carbon emissions.. "+ " </i></a></li> "+ " </i> </ul></li> "+ " <li><a>Other</a> "+ " <ul> "+ " <li><a class=desc><b>Other grammatical errors.</b><br>"+ "</a></li> "+ " </ul></li> "+ " </ul></li> "+ " <li><a>Stylistic</a> "+ " <ul> "+ " <li><a>Run-On Sentence</a> "+ " <ul> "+ " <li><a class=desc><b>Run-on sentences are "+"sentences that consist of too many clauses and appear clumsy "+ "or unnatural.</b><br> <i> Ex. I like school and "+ "especially I like math class but I do not like when we have "+ "a lot of homework but I still work very hard on our "+ "homework. </i></a></li> "+ " </ul></li> "+ " <li><a>Fragment</a> "+ " <ul> "+ " <li><a class=desc><b>Sentence fragments are "+"phrases which do not communicate a complete idea, often "+"because they are missing either a subject or a verb.</b><br>"+ "<i> Ex. And then going outside. </i></a></li> "+ " </ul></li> "+ " <li><a>Ordering</a> "+ " <ul> "+ " <li><a>Word Order</a> "+ " <ul> "+ " <li><a class=desc><b>Word order errors occur when"+ "words or phrases appear in an order that is unnatural or"+ "does not flow well.</b><br> <i> Ex.  Marie returned the "+ "bike to the store that she borrowed </i></a></li> "+ " </ul></li> "+ " <li><a>Adjective Order</a> "+ " <ul> "+ " <li><a class=desc><b>Adjective order errors occur"+ "when adjectives appear in an unnatural or unusual order.</b><br>"+ "<i> Ex. I am next to the brick tall building. </i></a></li> "+ " </ul></li> "+ " <li><a>Split Infinitive</a> "+ " <ul> "+ " <li><a class=desc><b>A split infinitive is the "+"placement of an adverb between the word 'to' and the verb.</b><br>"+ "<i> Ex. It is best to quickly run. </i></a></li> "+ " </ul></li> "+ " </ul></li> "+ " <li><a>Word Choice</a> "+ " <ul> "+ " <li><a>Wrong Noun</a> "+ " <ul> "+ " <li><a class=desc><b>If necessary, replace nouns with words that better express the idea the author seems to be communicating.</b><br> "+ "<i>Ex. I went to see a movie on Friday with my comrades. <br> Correction: I went to see a movie on Friday with my <b>friends</b>.  </i></a></li> "+" </ul></li> "+ " <li><a>Wrong Verb</a> "+ " <ul> "+ " <li><a class=desc><b>If necessary, replace verbs with words that better express the idea the author seems to be communicating.</b><br> "+ "<i>Ex. I had to dash to keep up with her.<br> Correction: I had to <b>run</b> to keep up with her.  </i></a></li> "+" </ul></li> "+ " <li><a>Wrong Adjective/Adverb</a> "+ " <ul> "+ " <li><a class=desc><b>If necessary, replace descriptors with words that better express the idea the author seems to be communicating.</b><br> "+ "<i>Ex. I was not gleeful about the news.<br> Correction: I was not <b>happy</b> about the news.  </i></a></li> "+" </ul></li> "+ " <li><a>Other Wrong Words</a> "+ " <ul> "+ " <li><a class=desc><b>Replace words for which you believe another word would be more appropriate or read more naturally.</b><br> "+ "</a></li> "+" </ul></li> "+ " </ul></li> "+ " <li><a>Other</a> "+ " <ul> "+ " <li><a class=desc><b>Other structural errors.</b><br>"+ "</a></li> "+ " </ul></li> "+ " </ul></li> "+ " </ul> "+ " </ul> "+ " </li> " ; 

var curr_sentence = 0;
var num_entered = 0;
var num_highlighted = 0;
var span_start = -1;
var span_start2 = -1;
var span_anchor = -1;
var insert_idx = -1;
var revert_word = "";
var last_corrected = "";
var new_word = "";
var highlighting_mode = "";
var errType = "";
var old_word = "";
var old_word2 = "";
var dropText = "";
var dragToken = "";
var current_step = "spelling";
var hasHelpQtip = false;
var hasWarningQtip = false;
var new_sentence = true;
var clicked_word = false;
var moving_phrase = false;
var first_word = true;
var in_progress = false;
var option_chosen = false;
var input_displayed = false;
var forward_highlighting = true;
var num_corr = 0; 
var err_type_chosen = false;
var menuLocked = false;

/**
 * Initalizes words array which contains space-delimited words of each sentence 
 */
function initalizeArrays() {
	for ( var i = 0; i < sentences.length; i++) {
		words[i] = sentences[i].split(/\s/);
	}
}

/**
 * Create buttons to allow for switching between word/pair/phrase highlighting modes and set up help qtip 
 */
function writeTabs() {
	var text = "";
	text += '<br> <br>';
	text += '<button class="button" type="button" id="insertButton"> Insert </button>';
	text += ' a new word or phrase.';
	text += ' or select a ';
	text += '<button class="button" type="button" id="wordButton" disabled="true"> Word </button>, ';
	text += '<button class="button" type="button" id="pairButton"> Pair </button>';
	text += ', or <button class="button" type="button" id="phraseButton"> Phrase </button>';
	text += ' to change or delete.   ';
	text += '<input class="img" type="image" onClick="return false;" id="modes"'
			+ 'style="width:34;height:34;border=none"'
			+ 'src="http://www.fingerhut.com/assets/f/nonselling/icon_questionmark.gif">'
			+ '</img><center>'; //terrible style, i know, to have half the <center> flag here and the other half in the .html, but I am lazy and this works 
	$("#orig").before(text);
	$("#wordButton").addClass("clicked");
	$("#modes").qtip({
		content : instructions["modes"],
		show : { when : 'mouseover', effect : { type : 'slide', length : '500' } },
		hide : { when : 'mouseout', effect : { type : 'slide', length : '500' } },
		position : { target : $("#orig"), corner : { target : 'topMiddle', tooltip : 'topMiddle' } },
		style : { width : { max : 1000 }, name : 'blue' }
	});

	initalizeArrays();
}

/**
* Display explanations for current error type 
*/
function getHelp() {
	var msg = "Choose a description for the error you are correcting. Please be as specific as possible while still accurately capturing the error you have identified.";
	$("#help" + num_corr).qtip({
		content : msg,
		show : { when : 'mouseover', effect : { type : 'slide', length : '500' } },
		hide : { when : 'mouseout', effect : { type : 'slide', length : '500' } },
		position : { target : $("#orig"), corner : { target : 'topMiddle', tooltip : 'topMiddle' } },
		style : { width : { max : 1000 }, name : 'blue' },
		api : { beforeShow : function() { hasHelpQtip = true; }, beforeDestroy : function() { hasHelpQtip = false; } }
	});
}

/**
* Write text of all original sentences to display as reference for user
*/
function writeOriginalSentences() {
	for ( var s = 0; s < sentences.length; s++) {
		$("#sent" + s).text(sentences[s]);
	}
	/*for(var i = 0; i < words.length; i++){
		var s = "";
		for(var j = 0; i < words[i].length; j++){
			s += words[i][j]+ " ";
		}
		$("#sent" + 1).text(s);
	}*/
}

/**
* Writes the sentence, hides left over spaces, updates reference sentences, and inactivates enter keys to prevent accidental form submission
*/
function updateTab() {
	var txt = "";
	txt += writeSentence(curr_sentence, false);
	$("#orig").html(txt);
	$("#current-edits").html(sentences[curr_sentence]);
//	$("#orig").before(txt);
	$(".space").hide();
	for ( var s = 0; s < sentences.length; s++) {
		if (visited[s]) { $("#edit" + s).text(sentences[s]); } 
		else { $("#edit" + s).text("Incomplete"); }
	}
	$(".orig").each(function() {
		if ($(this).attr('id') == "sent" + curr_sentence) {
			$(this).removeClass("inactive");
			$(this).addClass("active");
		} else {
			$(this).removeClass("active");
			$(this).addClass("inactive");
		}
	});
	$(".edited").each(function() {
		if ($(this).attr('id') == "edit" + curr_sentence) {
			$(this).removeClass("inactive");
			$(this).addClass("active");
		} else {
			$(this).removeClass("active");
			$(this).addClass("inactive");
		}
	});
	$("input").keypress(function(e) {
		var key;
		if (window.event) { key = window.event.keyCode; } 
		else { key = e.which; }
		if (key == 13) { return false; } 
		else { return true; }
	});
	$("tr").keypress(function(e) {
		var key;
		if (window.event) { key = window.event.keyCode; } 
		else { key = e.which; }
		if (key == 13) { return false; } 
		else {return true; }
	});
}

/**
 * Hide the corrections table.
 */
function hideCorrectionsTable() {
	for ( var j = 0; j < 100; j++) {
		var id = "C" + j;
		$("#" + id).hide();
		$("#input" + id).hide();
		$("#input" + id + '_b').hide();
		$("#errType" + id).hide();
	}
	$(".change").hide();
	$(".corrected_word").hide();
}

/**
 * Writes sentence i to the HTML document and wraps every word with a javascript
 * click function.
 */
function writeSentenceWithSpaces(i) {
	var origTxt =  $("#orig").html();
	var divs = origTxt.split('<td><div class="space"');
	var newTxt = divs[0];
	var cnt = 0;
	for(n = 1; n < divs.length; n++){
		newTxt += '<td><div class="space"'+divs[n];
		cnt += 1;
		if(cnt == 10){
			newTxt += '</tr><tr align=center>';
			cnt = 0;
		}
	} 
	return newTxt;	
}

/**
 * Writes sentence i to the HTML document and wraps every word with a javascript
 * click function.
 */
function writeSentence(i, showSpaces) {
	var num_words = 0;
	var text = '';
	text += '<div align=center><table id="wholesentence"><tr align=center>';
	for ( var j = 0; j < words[i].length; j++) {
		var word = words[i][j];
		if (word != "") {
			text += '<td><div class="space" id="' + j + '"> </div></td>';
			text += '<td><div class="word" id="word_' + i + '_' + j
					+ '" onClick="onClick(' + i + ', ' + j
					+ ')"  onMouseOver="mouseOverWord(' + i + ', ' + j
					+ ')" onMouseOut="leaveWord(' + i + ', ' + j + ')">';
			text += word;
			text += '</div> </td>';
		}
		num_words += 1
		if(!showSpaces && num_words == 15){
			text+='</tr><tr align=center>';
			num_words = 0;
		}
		if(showSpaces && num_words == 10){
			text+='</tr><tr align=center>';
			num_words = 0;
		}
	}
	text += '<td><div class="space" id="' + words[i].length + '"> </div></td>';
	text += '</tr></table></div>';
	return text;
}

/**
 * Writes the correction table for i to the HTML document as well as hidden form
 * elements for the highlight_mask and the num_highlights.
 */
function writeCorrectionsTable() {
	var text = '';
	text += '<table>';
	var i = num_corr;
	text += '<tr class="hidden" id="C' + i + '">';
	text += '</tr>';
	text += '</table>';
	$("#prevNext").after(text);
/*	if (num_corr == 0) {
		$("#allSentences").before(text);
	} else {
		$("#C" + (num_corr - 1)).before(text);
	}*/
}

/**
* Updates the words in the corrections tables to match the words displayed in the sentences
*/
function updateTables() {
	for ( var i = 0; i < words[curr_sentence].length; i++) {
		for ( var s = 0; s < step_list.length; s++) {
			$("#selection_" + steps[s] + "_word_" + curr_sentence + "_" + i)
					.text(words[curr_sentence][i]);
		}
	}
}

/**
* Insert a word into the sentence
*/
function insertWord(idx, word) {
	var new_sent = "";
	for ( var i = 0; i < idx; i++) {
		var id = "#word_" + curr_sentence + "_" + i;
		new_sent += $(id).text() + ' ';
	}
	new_sent += word + " ";
	for ( var i = idx; i < words[curr_sentence].length; i++) {
		var id = "#word_" + curr_sentence + "_" + i;
		new_sent += $(id).text() + ' ';
	}
	return new_sent;
}

/**
* Update current sentence's indecies to reflex reordered words 
*/
function commitMove() {
	moving_phrase = false;
	//confirmSpanStart();
	sentences[curr_sentence] = moveSpan(span_start, num_highlighted);
	words[curr_sentence] = sentences[curr_sentence].split(/\s/);
	updateTables();
	updateTab();
}

/**
* Update current sentence's indecies to reflex inserted words 
*/
function commitInsert() {
	$("#" + insert_idx).text($("#inputC" + num_corr).val() + " ");
	sentences[curr_sentence] = insertWord(insert_idx, $("#inputC" + num_corr)
			.val());
	words[curr_sentence] = sentences[curr_sentence].split(/\s/);
	updateTab();
	insert();
}

/**
* Update current sentence's indecies to reflex changed words 
*/
function commitChange() {
	$(".word").text(function() {
		if ($(this).hasClass("highlight")) {
			if (highlighting_mode == "word") {
				if (current_step == "delete") { return $(this).text(); } 
				else { return $("#inputC" + num_corr).val() + " "; }
			} else if (highlighting_mode == "pair") {
				if (first_word) {
					first_word = false;
					return $("#inputC" + num_corr).val() + " ";
				} else {
					first_word = true;
					return $("#inputC" + num_corr + '_b').val() + " ";
				}
			} else if (highlighting_mode == "phrase") {
				if (first_word && current_step != "delete") {
					first_word = false;
					return $("#inputC" + num_corr).val() + " ";
				} else { return ""; }
			}
		}
	});
	compileCorrections(curr_sentence);
	updateTab();
}


/**
* Remove unneeded text and buttons and write description of change that has been committed
*/
function cleanUpChange() {
	if (highlighting_mode == "pair") {
	//	$("#corr_text" + num_corr).before('<table><tr><td><div class="corrected_word">'
		$("#allSentences").before('<table><tr><td><div class="corrected_word">'
		+ $("#corr_div" + num_corr).text() + '</div></td>'
		+'<td class="change"><div width="14"> changed to </div></td>'
		+ '<td class="change"><div class="corrected_word">'
		+ $("#inputC" + num_corr).val() + " ... "
		+ $("#inputC" + num_corr + '_b').val() + '</div></td>'
		+ '<td><div class="corrected_word">'
		+$('#chosenErr'+num_corr).text()+'</div></td></tr></table>');
		$("#inputC" + num_corr + '_b').hide();
		$("#corr_text" + num_corr).hide();
		$("#C" + num_corr).hide();
	} else {
//		$("#corr_text" + num_corr).before('<table><tr><td><div class="corrected_word">'
		$("#allSentences").before('<table><tr><td><div class="corrected_word">'
		+ $("#corr_div" + num_corr).text() + '</div></td>'
		+ '<td class="change"><div width="14"> changed to </div></td>'
		+ '<td><div class="corrected_word">'
		+ $("#inputC" + num_corr).val() + '</div></td>'
		+ '<td><div class="corrected_word">'
		+$('#chosenErr'+num_corr).text()+'</div></td></tr></table>');
		$("#corr_text" + num_corr).hide();
		$("#C" + num_corr).hide();
	}
	$("#inputC" + num_corr).hide();
	$("#errTypeC" + num_corr).hide();
	$('#chosenErr'+num_corr).hide();
}

/**
* Remove unneeded text and buttons and write description of delete that has been committed
*/
function cleanUpDelete() {
	//$("#corr_text" + num_corr).after('<table><tr><td><div class="corrected_word">'
	$("#allSentences").before('<table><tr><td><div class="corrected_word">'
	+ $("#corr_div" + num_corr).text() + '</div></td>'
	+'<td class="change"><div width="14""> deleted </div></td>'
	+ '<td><div class="corrected_word">'
	+$('#chosenErr'+num_corr).text()+'</div></td></tr></table>');
	$("#corr_text" + num_corr).hide();
	$("#inputC" + num_corr).hide();
	$("#errTypeC" + num_corr).hide();
	$('#chosenErr'+num_corr).hide();
	$("#C" + num_corr).hide();
}

/**
* Remove unneeded text and buttons and write description of move that has been committed
*/
function cleanUpMove() {
	//$("#corr_text" + num_corr).after('<table><tr><td><div class="corrected_word">'
	$("#allSentences").before('<table><tr><td><div class="corrected_word">'
	+ $("#corr_div" + num_corr).text() + '</div></td>'
	+'<td class="change"><div width="14""> moved </div></td>'
	+ '<td><div class="corrected_word">'
	+$('#chosenErr'+num_corr).text()+'</div></td></tr></table>');
	$("#corr_text" + num_corr).hide();
	$("#inputC" + num_corr).hide();
	$("#errTypeC" + num_corr).hide();
	$('#chosenErr'+num_corr).hide();
	$("#C" + num_corr).hide();
}

/**
* Remove unneeded text and buttons and write description of insert that has been committed
*/
function cleanUpInsert() {
//	$("#corr_text" + num_corr).after('<table><tr><td><div class="corrected_word">'
	$("#allSentences").before('<table><tr><td><div class="corrected_word">'
	+ $("#inputC" + num_corr).val() + '</div></td>'
	+ '<td class="change"><div width="14"> inserted </div></td>'
	+ '<td><div class="corrected_word">'
	+$('#chosenErr'+num_corr).text()+'</div></td></tr></table>');
	$("#corr_text" + num_corr).hide();
	$("#inputC" + num_corr).hide();
	$("#errTypeC" + num_corr).hide();
	$('#chosenErr'+num_corr).hide();
	$("#C" + num_corr).hide();
}

/**
* Clean up after an edit has been made: remove unnecessary text and buttons, revert highlights, reenable buttons
*/
function cleanUpUI() {
	$("div").toggleClass("highlight", false);
	$("#errTypeC" + num_corr).attr("disabled", true);
	$("#inputC" + num_corr).attr("disabled", true);
	if (highlighting_mode == "pair") {
		$("#inputC" + num_corr + '_b').attr("disabled", true);
	}
	$("#cancel" + num_corr).hide();
	$("#enter" + num_corr).hide();
	$("#help" + num_corr).hide();
	if (current_step == "change") {
		cleanUpChange();
	} else if (current_step == "delete") {
		cleanUpDelete();
	} else if (current_step == "reorder") {
		cleanUpMove();
	}
	if (highlighting_mode == "insert") {
		cleanUpInsert();
	}
	if (hasWarningQtip) {
		$("#orig").qtip("destroy");
	}
	spanst = -1;
	num_highlighted = 0;
	num_corr += 1;
	first_word = true;
}

/**
* Display an alert if user attempts to submit without choosing and error type
*/
function displayWarning() {
	var warning = "<center><table width=100% cellspacing=5 cellpadding=3 cols=1>"
			+ "<tr><td align=center>Please select an error type.</td></tr>"
			+ "</table></center>";
	$("#orig").qtip({
		content : warning,
		show : { ready : true, effect : { type : 'fade', length : '500' } },
		hide : { when : { event : 'unfocus' }, effect : { type : 'fade', length : '500' } },
		//hide : { when : { target : $("#errType" + num_corr), event : 'focus' }, effect : { type : 'fade', length : '500' } },
		position : { target : $('#orig'), corner : { target : 'topMiddle', tooltip : 'topMiddle' } },
		style : { name : 'blue' },
		api : { beforeShow : function() { hasWarningQtip = true; }, beforeDestroy : function() { hasWarningQtip = false; } }
	});
}

/**
 * Corrects the word j in sentence i with the value in the text field; checks to
 * see if the correction is blank before replacing the word.
 */
function correctWord() {
	if (err_type_chosen == false) { displayWarning(); } 
	else {
		//$("#user_survey").before(getTrackChangesTable(num_corr));
		trackChanges(num_corr, span_start);
		if (moving_phrase) { commitMove(); } 
		else if (highlighting_mode == "insert") { commitInsert(); } 
		else { commitChange(); }
		cleanUpUI();
	}
	return false; // to stop MTurk from submitting the form early
}

/**
 * Remove all highlights from sentence's words 
 */
function reset_highlights() {
	var words = $("div");
	words.toggleClass("correct");
}

/**
 * Clears the tmp highlights in sentence.
 */
function clear_tmp_highlights() {
	$(".tmp_highlights").remove_class;
}

/**
* Builds drop-down menu with relevant error types for user to annotate
*/
function promptForType() {
	var text = "";
	text += '<td id="errTypeC'+num_corr+'">';
	text += getOptions();
	text += '</td>';
	text += '<td><input class="img" type="image" onClick="return false;" id="help'
				+ num_corr
				+ '" style="width:34;height:34;border=none"'
				+ 'src="http://www.fingerhut.com/assets/f/nonselling/icon_questionmark.gif">'
				+ '</img></td>';
	return text;
	/*if (highlighting_mode != "phrase" && current_step != "reorder") {
		var text = "";
		text += '<td><select id="errTypeC' + num_corr + '">';
		text += getOptions();
		text += '</select>';
		text += '<input class="img" type="image" onClick="return false;" id="help'
				+ num_corr
				+ '" style="width:34;height:34;border=none"'
				+ 'src="http://www.fingerhut.com/assets/f/nonselling/icon_questionmark.gif">'
				+ '</img></td>';
//		return text;
		return '<td id="errTypeC'+num_corr+'">'+multiMenu+'</td>';
	}
	return "";*/
}

/**
* Set up drag-and-drop feature by wrapping each word and space with necessary functions
*/
function dragDrop() {
	$(".space").mouseover( function(){
		$(this).addClass("hover");
	});
	$(".space").mouseout( function(){
		$(this).removeClass("hover");
	});
	$(".space").click( function(){
		insert_idx = $(this).attr('id');
		$(this).text(dropText);
		$(this).removeClass("space", "hover");
		$(this).addClass("word", "highlight");
		$("#"+dragToken).hide();
		$(".space").hide();
		$("#orig").qtip("destroy");
	});
	$(".space").droppable({
		over : function(e, ui) {
			$(this).addClass("hover");
		},
		out : function(e, ui) {
			$(this).removeClass("hover");
		},
		drop : function(e, ui) {
			insert_idx = $(this).attr('id');
			$(this).text(ui.draggable.text());
			$(this).removeClass("space", "hover");
			$(this).addClass("word", "highlight");
			ui.draggable.hide();
			$(".space").hide();
			$("#orig").qtip("destroy");
		},
	});
	$(".highlight").draggable(
			{
				snap: '.space',
				containment: '#orig',
				cursor : 'move',
				start : function() {
					$(".space").each(
							function() {
								var num = $(this).attr('id');
								if ($("#word_" + curr_sentence + "_" + num).is(
										":visible")
										&& num != span_start) {
									$(this).show();
								}
							});
					$(".highlight").each(function() {
					});
				},
			});
}

/**
* Find the phrase that has been highlighted and return as a div
*/
function selectedPhrase(e) {
	var phrase = "";
	$('.highlight').each(function() {
		phrase += $(this).text();
	});
	return '<div class="drag">' + phrase + '</div>';
}

/**
* Get the error types allowable for annotations given the current highlighting mode
*/
function getOptions() {
	var opts = '<ul id="nav"> <li><a>Choose Error Type</a> <ul>';
	if(current_step == "change"){
		opts = errorChoices["all"];
	}else if(current_step == "delete"){
		opts = errorChoices["all"];
	}else if(current_step == "reorder"){
		opts = errorChoices["all"];
	} else if(highlighting_mode == "insert"){
		opts = errorChoices["all"];
	}
	return opts;
}


/**
* Switch temporary highlights into permanent highlights
*/
function commitHighlights() {
	word = $(".tmp_highlight");
	word.removeClass("tmp_highlight");
	word.addClass("highlight");
}

/**
* Highlight a word that has been clicked
*/
function generalClick(id) {
	$("#" + id).addClass('clicked');
	/*
	 * $(".option").each(function() { if ($(this).attr('id') != id) {
	 * $(this).hide(); } });
	 */
}

/**
* Present user with text and buttons to begin making an edit
*/
function correctionUI() {
	$("#early_cancel" + num_corr).hide();
	var txt = "";
	$(".word").each(function() {
		if ($(this).hasClass("highlight")) {
			txt += $(this).text() + " ";
		}
	});
	if (highlighting_mode == "pair") {
		var pair = txt.split(/\s/);
		txt = pair[0] + "..." + pair[1];
	}
	if (current_step == "delete") {
		txt = revert_word;
	}
	var text = "";
	if (highlighting_mode != "insert") {
		text = '<table><tr><td id="corr_text' + num_corr
				+ '"><div id="corr_div'+num_corr+'" class="corrected_word">' + txt + '</div>';
	} else {
		text = '<td id="corr_text' + num_corr + '">';
	}
	text += promptForType();
	text += getButtons();
	text += '</tr></table>';
//	$('#C' + num_corr).after(text);
	$('#prevNext').after(text);
	enableDropDown();
}

function enableDropDown(){
	type = "";
	$("#nav a").mouseover(function(){
		$(this).css("background-color", "lightblue");
		if(!$(this).hasClass("desc")){
			errType = $(this).text();
		}
	});
	$("#nav a").mouseout(function(){
		$(this).css("background-color", "white");
	});
	$("#nav a").click(function(){
//		if(menuLocked){
			type = errType; 
			if(type != "Choose Error Type"){
				err_type_chosen = true;
			}
			if($('#chosenErr'+num_corr).length <= 0){ //if an error has already been chosen
				$("#errTypeC"+num_corr).before('<td><a id="chosenErr'+num_corr+'" class="chosen" href="#">'+type+'</a></td>');
			}else{
				$('#chosenErr'+num_corr).text(type);
				$('#chosenErr'+num_corr).show();
			}
			$("#errTypeC"+num_corr).hide();
			$("#chosenErr"+num_corr).click(function(){
				$("#errTypeC"+num_corr).show();
				$(this).hide();
			});
			menuLocked = false;
/*		}else{
			$("li").attr("display", "block");
			menuLocked = true;
		}*/
		return false;
	});
}

/**
* Save state and present correction UI if user enters "delete" mode
*/
function deleteClick() {
	current_step = "delete";
	generalClick("delete" + num_corr);
	$("#step_buttons" + num_corr).hide();
	$("#step_text" + num_corr).hide();
	$("#qmark" + num_corr).hide();
	revert_word = "";
	$(".word").each(function() {
		if ($(this).hasClass("highlight")) {
			revert_word += $(this).text() + " ";
			$(this).text("");
		}
	});
	correctionUI();
	$("#enter" + num_corr).show();
	$("#cancel" + num_corr).show();
	$(".finish").mouseover(function() {
		if (!$(this).hasClass("clicked")) {
			$(this).addClass("hover");
		}
	});
	$(".finish").mouseout(function() {
		$(this).toggleClass("hover", false);
	});
	getHelp();
	return false;
}

/**
* Save state and present correction UI if user enters "reorder" mode
*/
function moveClick() {
	$(".space").each(
			function() {
				// check to make sure no contiguous spaces
				var space_num = $(this).attr('id');
				if (space_num < span_start
						|| space_num > span_start + num_highlighted) {
					$(this).show();
				}
	});
	current_step = "reorder";
	generalClick("move" + num_corr);
	$("#step_buttons" + num_corr).hide();
	$("#step_text" + num_corr).hide();
	$("#qmark" + num_corr).hide();
	correctionUI();
	moving_phrase = true;
	$("#enter" + num_corr).show();
	$("#cancel" + num_corr).show();
	var phrase = "";
	var group_start = false;
	var first = "";
	$('.highlight').each(function() {
		if (!$(this).hasClass("corrected_word")) {
			phrase += $(this).text() + ' ';
			if (!group_start) {
				group_start = true;
				first = $(this);
			} else {
				$(this).remove();
			}
		}
	});
	phrase = phrase.trim();
	dropText = phrase;
	first.text(phrase);
	dragToken = first.attr('id');
	var txt = writeSentenceWithSpaces(curr_sentence);
	$("#orig").html(txt);
	dragDrop();
	$(".finish").mouseover(function() {
		if (!$(this).hasClass("clicked")) {
			$(this).addClass("hover");
		}
	});
	$(".finish").mouseout(function() {
		$(this).toggleClass("hover", false);
	});
	getHelp();
	reorderInstructions("Drag and drop word or phrase into place.");
	return false;
}

/**
* Save state and present correction UI if user enters "change" mode
*/
function changeClick() {
	current_step = "change";
	generalClick("change" + num_corr);
	$("#step_buttons" + num_corr).hide();
	$("#step_text" + num_corr).hide();
	$("#qmark" + num_corr).hide();
	correctionUI();
	onBlur();
	$(".finish").mouseover(function() {
		if (!$(this).hasClass("clicked")) {
			$(this).addClass("hover");
		}
	});
	$(".finish").mouseout(function() {
		$(this).toggleClass("hover", false);
	});
	getHelp();
	return false;
}

/**
* Create buttons presenting user with options once a word or phrase and been chosen
*/
function stepButtons(txt) {
	var text = "";
	if (highlighting_mode != "pair") {
		text = '<td id = "step_buttons' + num_corr + '"> Do you want to ';
		text += '<button class="option" id="change' + num_corr + '">';
		text += "Change";
		text += '</button>, ';
		text += '<button class="option" id="delete' + num_corr + '">';
		text += "Delete";
		text += '</button>, or ';
		text += ' <button class="option" id="move' + num_corr + '">';
		text += "Move";
		text += '</button>';
		text += '<td><div class="corrected_word" id="step_text' + num_corr
				+ '">' + txt + '</div></td><td><div id="qmark' + num_corr
				+ '"> ? </div></td>';
	} else {
		text = '<td id = "step_buttons' + num_corr + '">';
		text += '<button class="option" id="change' + num_corr + '">';
		text += "Change";
		text += '</button> ';
		text += '<td><div class="corrected_word" id="step_text' + num_corr
				+ '">' + txt + '</div></td><td><div id="qmark' + num_corr
				+ '"> ? </div></td>';
	}
	text += '<td><button class = "finish" id="early_cancel'
			+ num_corr
			+ '"'
			+ 'onclick="return cancel()" onsubmit="return cancel()">'
			+ '<img src="http://www.developmentgateway.org/sites/all/themes/corporate/images/cancel_icon.gif"></img>Cancel</button></td></td>';
	return text;
}

/**
* Present user with move/change/delete options once a word/phrase has been selected
*/
function displayChoices() {
	if (!in_progress) {
		//writeCorrectionsTable();
		var txt = "";
		$(".highlight").each(function() {
			txt += $(this).text() + " ";
		});
		old_word = txt;
		if (highlighting_mode == "pair") {
			var pair = txt.split(/\s/);
			txt = pair[0] + "..." + pair[1];
			old_word = pair[0];
			old_word2 = pair[1];
		}
	//	$("#C" + num_corr).show();
	//	$("#C" + num_corr).append(stepButtons(txt));
		$("#prevNext").after(stepButtons(txt));
		$('#enter' + num_corr).hide();
		$("#delete" + num_corr).click(function() {
			if (!option_chosen) {
				deleteClick();
				option_chosen = true;
			}
			return false;
		});
		$("#move" + num_corr).click(function() {
			if (!option_chosen) {
				moveClick();
				option_chosen = true;
			}
			return false;
		});
		$("#change" + num_corr).click(function() {
			if (!option_chosen) {
				changeClick();
				option_chosen = true;
			}
			return false;
		});
		$(".option").mouseover(function() {
			$(this).addClass("hover");
		});
		$(".option").mouseout(function() {
			$(this).removeClass("hover");
		});
		$(".finish").mouseover(function() {
			$(this).addClass("hover");
		});
		$(".finish").mouseout(function() {
			$(this).removeClass("hover");
		});
		in_progress = true;
	}
}

/**
* Finalize highlights once a word or phrase has been selected and clicked, and record necessary data before displaying 
* editing choices to the user
*/
function onClick(i, j) {
	if (!in_progress) {
		clear_tmp_highlights();
		if (highlighting_mode == "pair") {
			num_highlighted = 1;
			if (!clicked_word) {
				commitHighlights();
				clicked_word = true;
				span_start = j;
			} else {
				clicked_word = false;
				span_start2 = j;
				commitHighlights();
				displayChoices();
			}
		} else if (highlighting_mode == "word") {
			span_start = j;
			num_highlighted = 1;
			commitHighlights();
			displayChoices();
		} else if (highlighting_mode == "phrase") {
			if (!clicked_word) {
				span_start = j;
				span_anchor = j;
				num_highlighted = 1;
				clicked_word = true;
			} else {
				if (num_highlighted == 1) {
					highlighting_mode = "word";
					$('#wordButton').attr('disabled', true);
					$('#phraseButton').attr('disabled', false);
					$("#wordButton").addClass('clicked');
					$("#phraseButton").removeClass('clicked');
					$("#phraseButton").removeClass('hover');
				}
				commitHighlights();
				confirmSpanStart();
				displayChoices();
				clicked_word = false;
			}
		}
	}
}


function confirmSpanStart(){
	cnt = 0;
	true_start = 0;
	found = false;
	for(i = 0; i < words[curr_sentence].length; i++){
		if($('#word_'+curr_sentence+'_'+i).hasClass('highlight')){
			if(!found){
				true_start = i;
				found = true;
			}
			cnt += 1;
		}
	}
	s = "";
	for(j = 0; j < words[curr_sentence].length; j++){
		s += words[curr_sentence][j] + "-";
	}
	span_start = true_start;
	num_highlighted = cnt;
}

/**
* Clean up and reset variables if an edit is cancelled
*/
function cancel() {
	if (current_step == "reorder") {
		updateTab();
	}
	if (current_step == "delete") {
		$("#word_" + curr_sentence + "_" + span_start).text(revert_word);
		updateTab();
	}
	$("#inputC" + num_corr).hide();
	$("#corr_text" + num_corr).hide();
	$("#errTypeC" + num_corr).hide();
	$("#chosenErr" + num_corr).hide();
	if (highlighting_mode == "pair") {
		$("#inputC" + num_corr + '_b').hide();
	}
	$("#C" + num_corr).hide();
	$("#step_buttons" + num_corr).hide();
	$("#step_text" + num_corr).hide();
	$("#qmark" + num_corr).hide();
	$("#early_cancel" + num_corr).hide();
	$("#help" + num_corr).hide();
	$("#cancel" + num_corr).hide();
	$("#enter" + num_corr).hide();
	$("div").toggleClass("highlight", false);
	num_corr += 1;
	in_progress = false;
	option_chosen = false;
	input_displayed = false;
	clicked_word = false;
	moving_phrase = false;
	err_type_chosen = false;
	old_word = "";
	old_word2 = "";
	if (highlighting_mode == "insert") {
		$(".space").show();
	}
	if (hasWarningQtip) {
		$("#orig").qtip("destroy");
	}
	return false;
}

/**
* Create enter and cancel buttons
*/
function getButtons() {
	return '<td><button class="finish" id="enter'
			+ num_corr
			+ '"'
			+ 'onclick="return correctWord()" onsubmit="return correctWord()">'
			+ '<img src="http://www.harddrivesdirect.com/images/icon_checkmark.gif"></img>Submit</button>'
			+ '<button class = "finish" id="cancel'
			+ num_corr
			+ '"'
			+ 'onclick="return cancel()" onsubmit="return cancel()">'
			+ '<img src="http://www.developmentgateway.org/sites/all/themes/corporate/images/cancel_icon.gif"></img>Cancel</button>';
}

/**
* Show input text box for user to enter correction, badly named for legacy reasons...
*/
function onBlur() {
	if (!input_displayed) {
		if (highlighting_mode == "pair") {
			$("#corr_text" + num_corr)
					.after(
							'<input type="text" id="inputC' + num_corr
									+ '"size="20"/>');
			$("#inputC" + num_corr).after(
					'<input type="text" id="inputC' + num_corr
							+ '_b" size="20"/>');
			$("#enter" + num_corr).show();
			$("#cancel" + num_corr).show();
			if(current_step != "insert"){
				$('#inputC'+num_corr).val(old_word);
				$('#inputC'+num_corr+'_b').val(old_word2);
			}
		} else {
			$("#corr_text" + num_corr).after(
					'<input type="text" id="inputC' + num_corr
							+ '" size="20"/>');
			$("#enter" + num_corr).show();
			$("#cancel" + num_corr).show();
			$("#inputC" + num_corr).focus();
			input_displayed = true;
			if(current_step != "insert"){
				$('#inputC'+num_corr).val(old_word);
			}
		}
	}
}

/**
* Prompt user with instructions for drag-and-drop during reorder mode
*/
function reorderInstructions(action) {
	$("#orig").qtip({
		content : action,
		show : { ready : true, effect : { type : 'fade', length : '500' } },
		hide : { when : { event : 'unfocus' }, effect : { type : 'fade', length : '500' }, fixed : 'false', delay: '5000'},
		position : { target : $('#orig'), corner : { target : 'bottomMiddle', tooltip : 'topMiddle' }, },
		style : { name : 'blue' }
	});
}

/**
* Governs highlighting behavior in phrase-mode; ensures spans are contiguous and highlights are added in a logical manner
*/
function addTmpHighlightsToSpan(i, j) {
	var added = 0;
	if (j > span_start) {
		if (!forward_highlighting) {
			forward_highlighting = true;
			for ( var k = span_start; k < span_anchor; k++) {
				$("#word_" + i + "_" + k).removeClass("tmp_highlight");
			}
			num_highlighted = 1;
			span_start = span_anchor;
		}
		for ( var k = span_anchor + num_highlighted; k <= j; k++) {
			$("#word_" + i + "_" + k).addClass("tmp_highlight");
			added += 1;
		}
		num_highlighted += added;
	} else {
		if (forward_highlighting) {
			forward_highlighting = false;
			for ( var k = span_anchor; k <= span_anchor + num_highlighted; k++) {
				$("#word_" + i + "_" + k).removeClass("tmp_highlight");
			}
			num_highlighted = 1;
			span_start = j;
		}
		if (j < span_start) {
			span_start = j;
		}
		for ( var k = j; k <= span_anchor; k++) {
			$("#word_" + i + "_" + k).addClass("tmp_highlight");
			added += 1;
		}
		num_highlighted += added;
	}
}

/**
* Governs highlighting behavior in phrase-mode; ensures spans are contiguous and highlights are removed in a logical manner
*/
function removeTmpHighlightsFromSpan(i, j) {
	var removed = 0;
	if (j > span_start) {
		if (forward_highlighting) {
			for ( var k = j; k <= span_anchor + num_highlighted; k++) {
				$("#word_" + i + "_" + k).removeClass("tmp_highlight");
				removed += 1;
			}
			num_highlighted -= removed;
		} else {
			if (!forward_highlighting) {
				for ( var k = span_start; k <= j; k++) {
					$("#word_" + i + "_" + k).removeClass("tmp_highlight");
					removed += 1;
				}
				num_highlighted -= removed;
			}
		}
	}
}

/**
 * This method specifies action to take when mousing over word j in sentence i.
 */
function mouseOverWord(i, j) {
	var word = $("#word_" + i + "_" + j);
	if (!in_progress && highlighting_mode != "insert") {
		if (highlighting_mode == "phrase" && clicked_word) {
			if (word.hasClass('tmp_highlight')) {
				removeTmpHighlightsFromSpan(i, j);
			} else {
				addTmpHighlightsToSpan(i, j);
			}
		} else {
			word.toggleClass("tmp_highlight");
			if (highlighting_mode != "phrase") {
				num_highlighted = 1;
			}
		}
	}
}

/**
* Remove temporary highlights from a word
*/
function leaveWord(i, j) {
	var word = $("#word_" + i + "_" + j);
	if (highlighting_mode != "phrase" || !clicked_word) {
		word.removeClass("tmp_highlight");
	}
}

/**
* Display next sentence in HIT
*/ 
function nextSentence() {
	if (!in_progress) {
		if (curr_sentence + 1 < sentences.length) {
			curr_sentence++;
			visited[curr_sentence] = true;
			new_sentence = true;
			if ($('#buttonN').attr('disabled')){
				 $('#buttonN').removeAttr('disabled');
			}
			$("#buttonN").text("Next Sentence");
			updateTab();
		}if(curr_sentence + 1 == sentences.length){
			$("#buttonN").attr("disabled", "disabled");
			$("#buttonN").text("All Sentences Completed");
		}
	}
	return false;
}

/**
* Return to previous sentence in HIT
*/
function prevSentence() {
	if (!in_progress) {
		if (curr_sentence > 0) {
			curr_sentence--;
			new_sentence = true;
			updateTab();
		}
			if ($('#buttonN').attr('disabled')){
				 $('#buttonN').removeAttr('disabled');
			}
			$("#buttonN").text("Next Sentence");
	}
	return false;
}

/**
* Insert the currently-selected span into a new location in the sentence
*/
function moveSpan(start, length) {
	var sentence = "";
	if (insert_idx < start) {
		for ( var i = 0; i < insert_idx; i++) {
			var id = "#word_" + curr_sentence + "_" + i;
			sentence += $(id).text() + ' ';
		}
		for ( var i = start; i < start + length; i++) {
			var id = "#word_" + curr_sentence + "_" + i;
			sentence += $(id).text() + ' ';
		}
		for ( var i = insert_idx; i < words[curr_sentence].length; i++) {
			if (!(i >= start && i < start + length)) {
				var id = "#word_" + curr_sentence + "_" + i;
				sentence += $(id).text() + ' ';
			}
		}
	} else {
		for ( var i = 0; i < insert_idx; i++) {
			if (!(i >= start && i < start + length)) {
				var id = "#word_" + curr_sentence + "_" + i;
				sentence += $(id).text() + ' ';
			}
		}
		for ( var i = start; i < start + length; i++) {
			var id = "#word_" + curr_sentence + "_" + i;
			sentence += $(id).text() + ' ';
		}
		for ( var i = insert_idx; i < words[curr_sentence].length; i++) {
			var id = "#word_" + curr_sentence + "_" + i;
			sentence += $(id).text() + ' ';
		}
	}
	return sentence;
}

/**
 * Clean up the text of a sentence and update data structures to reflect new changes to sentence 
 */
function compileCorrections(i) {
	var sentence = "";
	$(".word").each(function() {
		if ($(this).is(":visible")) {
			sentence += $(this).text() + " ";
		}
	});
	// clean up extraneous spaces
	sentence = sentence.replace(/^\s+/g, "");
	sentence = sentence.replace(/\s+$/g, "");
	sentence = sentence.replace(/\s+/g, " ");
	if (sentence != sentences[i]) {
		// save the new sentence into the sentences array so that it gets used
		// in the next step.
		sentences[i] = sentence;
		words[i] = sentences[i].split(/\s/);
		updateTables();
	}
}

/**
* Build a new row of the hidden table to save data about the new edit 
*/
function getTrackChangesTable(id) {
/*        var text = '<form id="mainform"' + id + 'method="GET" action="http://workersandbox.mturk.com/mturk/externalSubmit">'
	text =  ""; //'<table>';
	alert(text);
        text += '<input type="text" name = "corr.' + id + '.num" id="corr.' + id
                        + '.num" value=""/>';
        text += '<input type="text" name = "corr.' + id + '.snt" id="corr.'
                        + id + '.snt" value=""/>';
        text += '<input type="hidden" name = "corr.' + id + '.sst" id="corr.'
                        + id + '.sst" value=""/>';
        text += '<input type="hidden" name = "corr.' + id + '.snd" id="corr.'
                        + id + '.snd" value=""/>';
        text += '<input type="text" name = "corr.' + id + '.old" id="corr.'
                        + id + '.old" value=""/>';
        text += '<input type="hidden" name = "corr.' + id + '.new" id="corr.'
                        + id + '.new" value=""/>';
        text += '<input type="hidden" name = "corr.' + id + '.mod" id="corr.'
                        + id + '.mod" value=""/>';
        text += '<input type="hidden" name = "corr.' + id + '.atn" id="corr.' + id
                        + '.atn" value=""/>';
//        text += '</table></form>';
     //   text += '</table>';
	alert(text);
        return text;*/
}

function record(id, num, snt, sst, snd, old, nw, mod, atn){
	var text = "";
	text += '<input type="hidden" name = "corr.' + id + '.num" id="corr.' + id + '.num" value="'+num+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.snt" id="corr.' + id + '.snt" value="'+snt+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.sst" id="corr.' + id + '.sst" value="'+sst+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.snd" id="corr.' + id + '.snd" value="'+snd+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.old" id="corr.' + id + '.old" value="'+old+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.new" id="corr.' + id + '.new" value="'+nw+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.mod" id="corr.' + id + '.mod" value="'+mod+'"/>';
        text += '<input type="hidden" name = "corr.' + id + '.atn" id="corr.' + id + '.atn" value="'+atn+'"/>';
	$("#allSentences").after(text);
	alert("here");
	$("#corr."+id+".num").hide();
	$("#corr."+id+".snt").hide();
	$("#corr."+id+".sst").hide();
       return false;
//	$("#user_survey").after('<input type="text" name="name" id="atest" value="'+value+'" />');
}


function trackChanges(id, j) {
	var num = num_corr;
        var snt = curr_sentence;
        var sst = span_start;
        var snd = span_start + num_highlighted;
        var old = $("#corr_text" + num_corr).text();
        var mod = current_step;
        var atn = errType;
        var wd1 = $("#inputC" + id).val();
        var wd2 = $("#inputC" + id + "_b").val();
	var nw = wd1;
        if (highlighting_mode == "pair") {
                var pair = old.split("...");
                old = pair[0] + ", " + pair[1];
                nw = wd1 + ", " + wd2;
                sst = span_start + ", " + span_start2;
                snd = (span_start + num_highlighted) + ", " + (span_start2 + num_highlighted);
        } 
        if (current_step == "reorder") {
                nw = insert_idx;
        }
        if (current_step == "delete") {
                nw = "";
        }
        in_progress = false;
        option_chosen = false;
        input_displayed = false;
        err_type_chosen = false;
//	record("id", "num", "snt", "sst", "snd", "old", "nw", "mod", "atn");
	record(id, num, snt, sst, snd, old, nw, mod, atn);
	return false;
}

/**
* Gather data about the most recent edit and save it into the hidden changes data structure 
*/
/*function trackChanges(id, j) {
	recordNum("this is the value");
	return false;
        var cid = "corr." + id;
	$("#" + cid + ".num").val(num_corr);
	//alert(document.getElementById(cid+".num"));
	//document.getElementById(cid+".num").Value = num_corr;
        $("#" + cid + ".snt").val(curr_sentence);
        $("#" + cid + ".sst").val(span_start);
        $("#" + cid + ".snd").val(span_start + num_highlighted);
        var txt = $("#corr_text" + num_corr).text();
        $("#" + cid + ".old").val(txt);
        $("#" + cid + ".mod").val(current_step);
        $("#" + cid + ".atn").val(errType); //$("#errTypeC" + id).val());
        var wd1 = $("#inputC" + id).val();
        var wd2 = $("#inputC" + id + "_b").val();
        if (highlighting_mode == "pair") {
                var pair = txt.split("...");
                $("#" + cid + ".old").val(pair[0] + ", " + pair[1]);
                $("#" + cid + ".new").val(wd1 + ", " + wd2);
                $("#" + cid + ".sst").val(span_start + ", " + span_start2);
                $("#" + cid + ".snd").val(
                                (span_start + num_highlighted) + ", "
                                                + (span_start2 + num_highlighted));

        } else {
                $("#" + cid + ".new").val(wd1);
        }
        if (current_step == "reorder") {
                $("#" + cid + ".new").val(insert_idx);
        }
        in_progress = false;
        option_chosen = false;
        input_displayed = false;
        err_type_chosen = false;
}*/





/**
* Insert a word into the sentence
*/ 
function insert() {
	txt = writeSentence(curr_sentence, true);
	$("#orig").html(txt);
//	$("#current-version").html(sentences[curr_sentence]);
	$(".space").show();
	$(".space").click(function() {
		$(this).removeClass("tmp_highlight");
		$(this).addClass("highlight");
		insert_idx = $(this).attr('id');
		////writeCorrectionsTable();
		correctionUI();
		onBlur();
		$(".finish").mouseover(function() {
			if (!$(this).hasClass("clicked")) {
				$(this).addClass("hover");
			}
		});
		$(".finish").mouseout(function() {
			$(this).toggleClass("hover", false);
		});
		$(".space").each(function() {
			if ($(this).attr('id') != insert_idx) {
				$(this).hide();
			}
		});
		$("#inputC" + num_corr).focus();
		getHelp();
	});
	$(".space").mouseover(function() {
		$(this).addClass("tmp_highlight");
	});
	$(".space").mouseout(function() {
		$(this).removeClass("tmp_highlight");
	});
}

function multimenu(){
$("#nav ul").css({display: "none"}); // Opera Fix
$("#nav li").hover(function(){
                $(this).find('ul:first').css({visibility: "visible",display: "none"}).show(400);
                },function(){
                $(this).find('ul:first').css({visibility: "hidden"});
                });
$("#nav a").click(function(){
	});
}

$(document).ready(function() {
	multimenu();	
	writeTabs();
	
	$(".button").click(function() {
		if (!in_progress) {
			$(":disabled").each(function() {
				if ($(this).hasClass("button")) {
					$(this).attr("disabled", false);
					$(this).removeClass("clicked");
					$(this).removeClass("hover");
				}
			});
			$(this).attr("disabled", true);
			$(this).addClass("clicked");
			highlighting_mode = $(this).text().toLowerCase().trim();
			current_step = defaults[highlighting_mode];
			compileCorrections(curr_sentence);
			initalizeArrays();
			updateTab();
			if ($(this).attr('id') == "insertButton") {
				insert();
			}
		}
		return false;
	});
	$(".button").mouseover(function() {
		if (!$(this).hasClass("clicked")) {
			$(this).addClass("hover");
		}
	});
	$(".button").mouseout(function() {
		$(this).toggleClass("hover", false);
	});
		

	
	highlighting_mode = "word";
	current_step = "spelling";
	for ( var i = 0; i < sentences.length; i++) {
		visited[i] = false;
	}
	visited[0] = true;
	if (curr_sentence == 0) {
		writeOriginalSentences();
	}
	updateTab();
});



