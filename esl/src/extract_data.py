import csv
import sys
import rebuild_sents
import edit_graph
#import progressbar

#edit object containing information about an atomic change made to a sentence
class Edit:
	def __init__(self):
		self.seq_id= 0
		self.sp_start = 0
		self.sp_end = 0
		self.old_wd = 0
		self.new_wd = 0
		self.mode = 0
	def __init__(self, seq, start, end, old, new, mode):
		self.seq_id= seq
		self.sp_start = start
		self.sp_end = end
		self.old_wd = old
		self.new_wd = new
		self.mode = mode
	def __str__(self):
		return "[{id: %s}, {start: %s}, {end: %s}, {old: %s}, {new: %s}, {mode: %s}]" % (self.seq_id, self.sp_start, self.sp_end, self.old_wd, self.new_wd, self.mode)
	def __repr__(self):
		return "[{id: %s}, {start: %s}, {end: %s}, {old: %s}, {new: %s}, {mode: %s}]" % (self.seq_id, self.sp_start, self.sp_end, self.old_wd, self.new_wd, self.mode)
	def __cmp__(self, other):
		return (int(self.seq_id) - int(other.seq_id))	


#given a row from the data table, return a map of sent_id: edit 
def get_edit(dt_row):
	edit = Edit()
	edit.seq_id = dt_row[' edit_num']
	edit.sp_start = dt_row[' span_start']
	edit.sp_end = dt_row[' span_end']
	edit.old_wd = dt_row[' old_word']
	edit.new_wd = dt_row[' new_word']
	edit.mode = dt_row[' edit_type']
	return {dt_row[' esl_sentence_id'].strip() : edit}


def build_edit_map(edit_data, sent_data):
	raw_edits = csv.DictReader(edit_data)
	#mapping from assignment: [list of {sentence: [list of edits]}]
	all_edits = {}
	print 'Build edit map: ',
	for e in raw_edits: 
		assign = e[' assignment_id'].strip()
		if(not(assign == "")): 
			if(not(assign in all_edits)): 
				all_edits[assign] = {}
		edit = get_edit(e)
		sent = edit.keys()[0].strip()
		if(not(sent == "")):
			if(not(sent in all_edits[assign])):
				all_edits[assign][sent] = [edit[sent]]
			else:
				all_edits[assign][sent].append(edit[sent])
	print 'Complete'
	return all_edits		

def build_sent_map(sent_data):
	raw_sents = csv.DictReader(sent_data)
	all_sents = {}
	print 'Build sent map: ',
	for s in raw_sents:
		all_sents[s['id']] = s[' sentence']	
	print 'Complete'
	return all_sents

#Build map of hitid : {map of sentences : [list of edits]}
def build_control_map(control_data):
	raw_cntrl = csv.DictReader(control_data)
	all_controls = {}
	print 'Build control map: ',
	for c in raw_cntrl:
		hit = c[' hit_id'].strip()
		if(not(hit in all_controls)):
			all_controls[hit] = {}
		sent = c['esl_sentence_id'].strip()
		if(not(sent in all_controls[hit])):
			all_controls[hit][sent] = []
		all_controls[hit][sent].append(c) 
	print 'Complete'
	return all_controls
