/*var sentences = [ "${sent0}", "${sent1}", "${sent2}", "${sent3}", "${sent4}",
		"${sent5}", "${sent6}", "${sent7}", "${sent8}", "${sent9}" ];*/

// Removed sentences variable and pushed it into ESL.tpl file

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
var explanations = new Array();

explanations["None"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Error Type</b></td></tr>"
		+ '<tr><td colspan=2 align=center>Please choose the category that best describes the type of correction '
		+ 'you are making. If you do not know what is meant by a specific error type, select that error type and mouse over the '
		+ 'question mark for a description. If you are still not sure which type to choose for your error, select "Not Sure."</td>';
explanations["Spelling"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Spelling</b></td></tr>"
		+ '<tr><td colspan=2 align=center>You should identify spelling errors when the choice of word is '
		+ 'correct but it is spelled or capitalized incorrectly</td>'
		+ "<tr><td colspan=2 align=center><i>Example</i></td></tr>"
		+ "<td><i>Incorrect: </i>I got lost on <b>teh</b> way to his house.<br>"
		+ "<i>Correction: </i>I got lost on <b>the</b> way to his house.</td></tr>"
		+ "</table></center>";
explanations["Punctuation"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Punctuation</b></td></tr>"
		+ '<tr><td colspan=2 align=center>You should remove extraneous punctuation and insert missing punctuation marks.</td>'
		+ "<tr><td colspan=2 align=center><i>Example</i></td></tr>"
		+ "<td><i>Incorrect: </i>She always<b>,</b> dresses up.<br>"
		+ "<i>Correction: </i>She always dresses up.</td></tr>"
		+ "</table></center>";
explanations["Noun"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Noun</b></td></tr>"
		+ '<tr><td colspan=2 align=center>A <b>noun</b> is a word representing a person, place, or thing. '
		+ 'Common noun errors involve confusion of noun numbers</td>'
		+ "<tr><td colspan=2 align=center><i>Example</i></td></tr>"
		+ "<td><i>Incorrect: </i>I will be there in three <b>hour</b>.<br>"
		+ "<i>Correction: </i>I will be there in three <b>hours</b>.</td></tr>";
explanations["Verb"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Verb</b></td></tr>"
		+ '<tr><td colspan=2 align=center>A <b>verb</b> is a word representing an action. '
		+ 'Common verb errors involve incorrect verb tenses or incorrect verb forms</td>'
		+ "<tr><td colspan=2 align=center><i>Examples</i></td></tr>"
		+ "<td><i>Incorrect: </i>Yesterday, John <b>run</b> two miles.<br>"
		+ "<i>Correction: </i>Yesterday, John <b>ran</b> two miles.</td></tr>"
		+ "<td><i>Incorrect: </i>My sister <b>cutted</b> her finger.<br>"
		+ "<i>Correction: </i>My sister <b>cut</b> her finger.</td></tr>";
explanations["Adjective"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Adjective</b></td></tr>"
		+ '<tr><td colspan=2 align=center>An <b>adjective</b> is a word which describes a noun. '
		+ 'Common adjective errors involve confusion between plural/singular nouns and incorrect adjective forms.</td>'
		+ "<tr><td colspan=2 align=center><i>Example</i></td></tr>"
		+ "<td><i>Incorrect: </i>You look much <b>more better</b> today.<br>"
		+ "<i>Correction: </i>You look much <b>better</b> today.</td></tr>"
		+ "<td><i>Incorrect: </i>Research requires <b>many</b> knowledge.<br>"
		+ "<i>Correction: </i>Research requires <b>much</b> knowledge.</td></tr>";
explanations["Preposition"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Preposition</b></td></tr>"
		+ '<tr><td colspan=2 align=center><b>Prepositions</b> are words such as <i>about, at, by, down, for, from, in, into, of, off, on, onto, out, over, to, up, upon, with,</i> and <i>within</i> '
		+ 'which describe relationships between nouns, verbs, and ideas in a sentence. '
		+ 'Common preposition errors involve missing prepositions or confusion between similar prepositions. </td>'
		+ "<tr><td colspan=2 align=center><i>Examples</i></td></tr>"
		+ "<td><i>Incorrect: </i>Let us meet home.<br>"
		+ "<i>Correction: </i>Let us meet <b>at</b> home.</td></tr>"
		+ "<td><i>Incorrect: </i>My brother lives <b>at</b> Mumbai.<br>"
		+ "<i>Correction: </i>My brother lives <b>in</b> Mumbai.</td></tr>"
		+ "<td><i>Incorrect: </i>I will be there <b>in</b> the hour.<br>"
		+ "<i>Correction: </i>I will be there <b>within</b> the hour.</td></tr>";
explanations["Determiner"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Determiner</b></td></tr>"
		+ '<tr><td colspan=2 align=center><b>Determiners</b> are words such as <i>a/the, this/that, some/any</i> and <i>each/every</i> '
		+ 'which describe the reference of a noun. '
		+ 'Common determiner errors involve missing determiners, unneccessary determiners, or determiners that do not match the noun to which they refer. </td>'
		+ "<tr><td colspan=2 align=center><i>Examples</i></td></tr>"
		+ "<td><i>Incorrect: </i>Kyiv is <b>a</b> capitol of Ukraine.<br>"
		+ "<i>Correction: </i>Kyiv is <b>the</b> capitol of Ukraine.</td></tr>"
		+ "<td><i>Incorrect: </i>I saw her when I was looking out of window.<br>"
		+ "<i>Correction: </i>I saw her when I was looking out of <b>the</b> window.</td></tr>"
		+ "<td><i>Incorrect: </i><b>The</b> football is very popular in Europe.<br>"
		+ "<i>Correction: </i>Football is very popular in Europe.</td></tr>";
explanations["Unknown"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Not Sure</b></td></tr>"
		+ '<tr><td colspan=2 align=center>If it is not clear which category you should use for the error you are correcting, select "Not Sure." </td>';
explanations["Subject-Verb"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Subject-Verb Agreement</b></td></tr>"
		+ '<tr><td colspan=2 align=center>Verbs should agree in number and in person with their corresponding subject. </td>'
		+ "<tr><td colspan=2 align=center><i>Examples</i></td></tr>"
		+ "<td><i>Incorrect: </i>Sarah's <b>books is</b> all over the floor.<br>"
		+ "<i>Correction: </i>Sarah's <b>books are</b> all over the floor.</td></tr>"
		+ "<td><i>Incorrect: </i><b>She go</b> to school very early in the morning.<br>"
		+ "<i>Correction: </i><b>She goes</b> to school very early in the morning.</td></tr>";
explanations["Pronoun-Noun"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Pronoun-Noun Agreement</b></td></tr>"
		+ '<tr><td colspan=2 align=center>Pronouns should match the gender and number of the noun they are replacing.</td>'
		+ "<tr><td colspan=2 align=center><i>Examples</i></td></tr>"
		+ "<td><i>Incorrect: </i>Every <b>student</b> must submit <b>their</b> own work.<br>"
		+ "<i>Correction: </i>Every <b>student</b> must submit <b>his</b> own work.</td></tr>";
explanations["Determiner-Agreement"] = "<center><table border=2 width=100% cellspacing=5 cellpadding=3 cols=2>"
		+ "<tr><td colspan=2 align=center><b>Determiner Agreement</b></td></tr>"
		+ '<tr><td colspan=2 align=center>Determiners should match the number and specificity of their corresponding noun, verb, or idea.</td>'
		+ "<tr><td colspan=2 align=center><i>Examples</i></td></tr>"
		+ "<td><i>Incorrect: </i>We've talked about <b>these</b> kind of <b>things</b>.<br>"
		+ "<i>Correction: </i>We've talked about <b>this</b> kind of <b>thing</b>.</td></tr>"
		+ "<td><i>Incorrect: </i>There were too <b>much people</b> in the crowd.<br>"
		+ "<i>Correction: </i>There were too <b>many people</b> in the crowd.</td></tr>";

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
var errType = "spelling";
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

/**
 * Initalizes the arrays that store the space-delimited words, and the boolean
 * arrays that indicate what words were marked as highlights.
 */
function initalizeArrays() {
	for ( var i = 0; i < sentences.length; i++) {
		words[i] = sentences[i].split(/\s/);
	}
}

/**
 * Write the tabs by iterating through the steps, and naming them according to
 * the tab_names.
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
			+ '</img>';
	$("#orig").before(text);
	$("#wordButton").addClass("clicked");
	$("#modes").qtip({
		content : instructions["modes"],
		show : {
			when : 'mouseover',
			effect : {
				type : 'slide',
				length : '500'
			}
		},
		hide : {
			when : 'mouseout',
			effect : {
				type : 'slide',
				length : '500'
			}
		},
		position : {
			target : $("#orig"),
			corner : {
				target : 'topMiddle',
				tooltip : 'topMiddle'
			}
		},
		style : {
			width : {
				max : 1000
			},
			name : 'blue'
		}
	});

	initalizeArrays();
}

function getHelp() {
	var msg = explanations["None"];
	$("#help" + num_corr).qtip({
		content : msg,
		show : {
			when : 'mouseover',
			effect : {
				type : 'slide',
				length : '500'
			}
		},
		hide : {
			when : 'mouseout',
			effect : {
				type : 'slide',
				length : '500'
			}
		},
		position : {
			target : $("#orig"),
			corner : {
				target : 'topMiddle',
				tooltip : 'topMiddle'
			}
		},
		style : {
			width : {
				max : 1000
			},
			name : 'blue'
		},
		api : {
			beforeShow : function() {
				hasHelpQtip = true;
			},
			beforeDestroy : function() {
				hasHelpQtip = false;
			}
		}
	});
	$("select").change(
			function() {
				if (hasHelpQtip) {
					if ($(this).val() == undefined) {
						$("#help" + num_corr).qtip("api").updateContent(
								explanations['None'], false);
					} else {
						$("#help" + num_corr).qtip("api").updateContent(
								explanations[$(this).val()], false);
					}
				}
			});

}

function writeOriginalSentences() {
	for ( var s = 0; s < sentences.length; s++) {
		$("#sent" + s).text(sentences[s]);
	}
}

function updateTab() {
	var txt = "";
	txt += writeSentence(curr_sentence);
	$("#orig").html(txt);
	$(".space").hide();
	for ( var s = 0; s < sentences.length; s++) {
		if (visited[s]) {
			$("#edit" + s).text(sentences[s]);
		} else {
			$("#edit" + s).text("Incomplete");
		}
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
		if (window.event) {
			key = window.event.keyCode;
		} else {
			key = e.which;
		}
		if (key == 13) {
			return false;
		} else {
			return true;
		}
	});
	$("tr").keypress(function(e) {
		var key;
		if (window.event) {
			key = window.event.keyCode;
		} else {
			key = e.which;
		}
		if (key == 13) {
			return false;
		} else {
			return true;
		}
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
function writeSentence(i) {
	var text = '';
	text += '<table id="wholesentence" align="center"><tr>';
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
	}
	text += '<td><div class="space" id="' + words[i].length + '"> </div></td>';
	text += '</tr></table>';
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
	if (num_corr == 0) {
		$("#HITend").before(text);
	} else {
		$("#C" + (num_corr - 1)).before(text);
	}
}

function updateTables() {
	for ( var i = 0; i < words[curr_sentence].length; i++) {
		for ( var s = 0; s < step_list.length; s++) {
			$("#selection_" + steps[s] + "_word_" + curr_sentence + "_" + i)
					.text(words[curr_sentence][i]);
		}
	}
}

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

function commitMove() {
	moving_phrase = false;
	sentences[curr_sentence] = moveSpan(span_start, num_highlighted);
	words[curr_sentence] = sentences[curr_sentence].split(/\s/);
	updateTables();
	updateTab();
}

function commitInsert() {
	$("#" + insert_idx).text($("#inputC" + num_corr).val() + " ");
	sentences[curr_sentence] = insertWord(insert_idx, $("#inputC" + num_corr)
			.val());
	words[curr_sentence] = sentences[curr_sentence].split(/\s/);
	updateTab();
	insert();
}

function commitChange() {
	$(".word").text(function() {
		if ($(this).hasClass("highlight")) {
			if (highlighting_mode == "word") {
				if (current_step == "delete") {
					return $(this).text();
				} else {
					return $("#inputC" + num_corr).val() + " ";
				}
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
				} else {
					return "";
				}
			}
		}
	});
	compileCorrections(curr_sentence);
	updateTab();
}

function cleanUpChange() {
	if (highlighting_mode == "pair") {
		$("#corr_text" + num_corr).after(
				'<td class="change"><div width="14"> changed to </div></td>'
						+ '<td class="change"><div class="corrected_word">'
						+ $("#inputC" + num_corr).val() + " ... "
						+ $("#inputC" + num_corr + '_b').val() + '</div></td>');
		$("#inputC" + num_corr + '_b').hide();

	} else {
		$("#corr_text" + num_corr).after(
				'<td class="change"><div width="14"> changed to </div></td>'
						+ '<td><div class="corrected_word">'
						+ $("#inputC" + num_corr).val() + '</div></td>');
	}
	$("#inputC" + num_corr).hide();
}

function cleanUpDelete() {
	$("#corr_text" + num_corr).after(
			'<td class="change"><div width="14""> deleted </div></td>');
	$("#inputC" + num_corr).hide();
}

function cleanUpMove() {
	$("#corr_text" + num_corr).after(
			'<td class="change"><div width="14"> moved </div></td>');
	$("#inputC" + num_corr).hide();
}

function cleanUpInsert() {
	$("#inputC" + num_corr)
			.before(
					'<td class="change"><div class="corrected_word">'
							+ $("#inputC" + num_corr).val()
							+ '</div></td>'
							+ '<td class="change"><div with="14"> inserted </div></td>');
	$("#inputC" + num_corr).hide();
}

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

function displayWarning() {
	var warning = "<center><table width=100% cellspacing=5 cellpadding=3 cols=1>"
			+ "<tr><td align=center>Please select a part of speech.</td></tr>"
			+ "</table></center>";
	$("#orig").qtip({
		content : warning,
		show : {
			ready : true,
			effect : {
				type : 'fade',
				length : '500'
			}
		},
		hide : {
			when : {
				target : $("#errType" + num_corr),
				event : 'focus'
			},
			effect : {
				type : 'fade',
				length : '500'
			}
		},
		position : {
			target : $('#orig'),
			corner : {
				target : 'topMiddle',
				tooltip : 'topMiddle'
			}

		},
		style : {
			name : 'blue'
		},
		api : {
			beforeShow : function() {
				hasWarningQtip = true;
			},
			beforeDestroy : function() {
				hasWarningQtip = false;
			}
		}
	});
}

/**
 * Corrects the word j in sentence i with the value in the text field checks to
 * see if the correction is blank before replacing the word.
 */
function correctWord() {
	if ($("#errTypeC" + num_corr).val() == "None") {
		displayWarning();
	} else {
		$("#commentBox").before(getTrackChangesTable(num_corr));
		trackChanges(num_corr, span_start);
		if (moving_phrase) {
			commitMove();
		} else if (highlighting_mode == "insert") {
			commitInsert();
		} else {
			commitChange();
		}
		cleanUpUI();
	}
	return false; // to stop MTurk from submitting the form early
}

/**
 * Causes the highlights to be displayed in the HTML.
 */
function reset_highlights() {
	var words = $("div");
	words.toggleClass("correct");
}

/**
 * Clears the tmp highlights in all sentences.
 */
function clear_tmp_highlights() {
	$(".tmp_highlights").remove_class;
}

function promptForType() {
	if (highlighting_mode != "phrase" && current_step != "reorder") {
		var text = "";
		text += '<td><select id="errTypeC' + num_corr + '">';
		text += getOptions();
		text += '</select>';
		text += '<input class="img" type="image" onClick="return false;" id="help'
				+ num_corr
				+ '" style="width:34;height:34;border=none"'
				+ 'src="http://www.fingerhut.com/assets/f/nonselling/icon_questionmark.gif">'
				+ '</img></td>';
		return text;
	}
	return "";
}

function dragDrop() {
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
		}
	});
	$(".highlight").draggable(
			{
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
				}
			});
}

function selectedPhrase(e) {
	var phrase = "";
	$('.highlight').each(function() {
		phrase += $(this).text();
	});
	return '<div class="drag">' + phrase + '</div>';
}

function getOptions() {
	var opts = "";
	if (highlighting_mode == "word") {
		opts = '<option value="None">Choose One</option>';
		if (current_step != "delete") {
			opts += '<option value="Spelling">Spelling</option>';
		}
		opts += '<option value="Punctuation">Punctuation</option>'
				+ '<option value="Noun">Noun</option>'
				+ '<option value="Verb">Verb</option>'
				+ '<option value="Adjective">Adjective</option>'
				+ '<option value="Preposition">Preposition</option>'
				+ '<option value="Determiner">Determiner</option>'
				+ '<option value="Unknown">Not Sure</option>';
	} else if (highlighting_mode == "pair") {
		opts = '<option value="None">Choose One</option>'
				+ '<option value="Subject-Verb">Subject-Verb Agreement</option>'
				+ '<option value="Pronoun-Noun">Pronoun-Noun Agreement</option>'
				+ '<option value="Determiner-Agreement">Determiner Agreement</option>'
				+ '<option value="Unknown">Not Sure</option>';
	} else if (highlighting_mode == "insert" || current_step == "delete") {
		opts = '<option value="None">Choose One</option>'
				+ '<option value="Punctuation">Punctuation</option>'
				+ '<option value="Noun">Noun</option>'
				+ '<option value="Verb">Verb</option>'
				+ '<option value="Adjective">Adjective</option>'
				+ '<option value="Preposition">Preposition</option>'
				+ '<option value="Determiner">Determiner</option>'
				+ '<option value="Unknown">Not Sure</option>';
	}
	return opts;
}

function commitHighlights() {
	word = $(".tmp_highlight");
	word.removeClass("tmp_highlight");
	word.addClass("highlight");
}

function generalClick(id) {
	$("#" + id).addClass('clicked');
	/*
	 * $(".option").each(function() { if ($(this).attr('id') != id) {
	 * $(this).hide(); } });
	 */
}

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
		text = '<td id="corr_text' + num_corr
				+ '"><div class="corrected_word">' + txt + '</div>';
	} else {
		text = '<td id="corr_text' + num_corr + '">';
	}
	text += promptForType();
	text += getButtons();
	$('#C' + num_corr).after(text);
}

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

function moveClick() {
	current_step = "reorder";
	generalClick("move" + num_corr);
	$("#step_buttons" + num_corr).hide();
	$("#step_text" + num_corr).hide();
	$("#qmark" + num_corr).hide();
	$(".space").each(
			function() {
				// check to make sure no contiguous spaces
				var space_num = $(this).attr('id');
				if (space_num < span_start
						|| space_num > span_start + num_highlighted) {
					$(this).show();
				}
			});
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
	first.text(phrase);
	dragDrop();
	$(".finish").mouseover(function() {
		if (!$(this).hasClass("clicked")) {
			$(this).addClass("hover");
		}
	});
	$(".finish").mouseout(function() {
		$(this).toggleClass("hover", false);
	});
	return false;
}

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

function displayChoices() {
	if (!in_progress) {
		writeCorrectionsTable();
		var txt = "";
		$(".highlight").each(function() {
			txt += $(this).text() + " ";
		});
		if (highlighting_mode == "pair") {
			var pair = txt.split(/\s/);
			txt = pair[0] + "..." + pair[1];
		}
		$("#C" + num_corr).show();
		$("#C" + num_corr).append(stepButtons(txt));
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
				displayChoices();
				clicked_word = false;
			}
		}
	}
}

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
	if (highlighting_mode == "pair") {
		$("#inputC" + num_corr + '_b').hide();
	}
	$("#C" + num_corr).hide();
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
	if (highlighting_mode == "insert") {
		$(".space").show();
	}
	if (hasWarningQtip) {
		$("#orig").qtip("destroy");
	}
	return false;
}

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
		} else {
			$("#corr_text" + num_corr).after(
					'<input type="text" id="inputC' + num_corr
							+ '" size="20"/>');
			$("#enter" + num_corr).show();
			$("#cancel" + num_corr).show();
			$("#inputC" + num_corr).focus();
			input_displayed = true;
		}
	}
}

function reorderInstructions(action) {
	$("#orig").qtip({
		content : instructions[action],
		show : {
			ready : true,
			effect : {
				type : 'fade',
				length : '500'
			}
		},
		hide : {
			when : {
				event : 'unfocus'
			},
			effect : {
				type : 'fade',
				length : '500'
			}
		},
		position : {
			target : $('#orig'),
			corner : {
				target : 'bottomMiddle',
				tooltip : 'topMiddle'
			},

		},
		style : {
			name : 'blue'
		}
	});
}

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

function leaveWord(i, j) {
	var word = $("#word_" + i + "_" + j);
	if (highlighting_mode != "phrase" || !clicked_word) {
		word.removeClass("tmp_highlight");
	}
}

function nextSentence() {
	if (!in_progress) {
		if (curr_sentence + 1 < sentences.length) {
			curr_sentence++;
			visited[curr_sentence] = true;
			new_sentence = true;
			updateTab();
		}
	}
	return false;
}

function prevSentence() {
	if (!in_progress) {
		if (curr_sentence > 0) {
			curr_sentence--;
			new_sentence = true;
			updateTab();
		}
	}
	return false;
}

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
 * Compiles the corrections for a sentence.
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

function getTrackChangesTable(id) {
	var text = '<table>';
	text += '<input type="hidden" name = "corr-' + id + '-num" id="corr-' + id
			+ '-num" />';
	text += '<input type="hidden" name = "corr-' + id + '-sentence" id="corr-'
			+ id + '-sentence" />';
	text += '<input type="hidden" name = "corr-' + id + '-spanst" id="corr-'
			+ id + '-spanst" />';
	text += '<input type="hidden" name = "corr-' + id + '-spanend" id="corr-'
			+ id + '-spanend" />';
	text += '<input type="hidden" name = "corr-' + id + '-oldword" id="corr-'
			+ id + '-oldword" />';
	text += '<input type="hidden" name = "corr-' + id + '-newword" id="corr-'
			+ id + '-newword" />';
	text += '<input type="hidden" name = "corr-' + id + '-errtype" id="corr-'
			+ id + '-errtype" />';
	text += '<input type="hidden" name = "corr-' + id + '-pos" id="corr-' + id
			+ '-pos" />';
	text += '</table>';
	return text;
}

function trackChanges(id, j) {
	var cid = "corr-" + id;
	$("#" + cid + "-num").val(num_corr);
	$("#" + cid + "-sentence").val(curr_sentence);
	$("#" + cid + "-spanst").val(span_start);
	$("#" + cid + "-spanend").val(span_start + num_highlighted);
	var txt = $("#corr_text" + num_corr).text();
	$("#" + cid + "-oldword").val(txt);
	$("#" + cid + "-errtype").val(current_step);
	$("#" + cid + "-pos").val($("#errTypeC" + id).val());
	var wd1 = $("#inputC" + id).val();
	var wd2 = $("#inputC" + id + "_b").val();
	if (highlighting_mode == "pair") {
		var pair = txt.split("...");
		$("#" + cid + "-oldword").val(pair[0] + ", " + pair[1]);
		$("#" + cid + "-newword").val(wd1 + ", " + wd2);
		$("#" + cid + "-spanst").val(span_start + ", " + span_start2);
		$("#" + cid + "-spanend").val(
				(span_start + num_highlighted) + ", "
						+ (span_start2 + num_highlighted));

	} else {
		$("#" + cid + "-newword").val(wd1);
	}
	if (current_step == "reorder") {
		$("#" + cid + "-newword").val(insert_idx);
	}
	in_progress = false;
	option_chosen = false;
	input_displayed = false;
}

function insert() {
	$(".space").show();
	$(".space").click(function() {
		$(this).removeClass("tmp_highlight");
		$(this).addClass("highlight");
		insert_idx = $(this).attr('id');
		writeCorrectionsTable();
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

$(document).ready(function() {
	
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
