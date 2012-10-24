"""
Definitions of edit, revision, and sentence objects, as well as graph data structures containing them
"""

import rebuild_sents
import figures
import sys
import nltk
#import progressbar
from nltk.tag.simplify import simplify_brown_tag

#edit object containing information about an atomic change made to a sentence
class Node:
	id_num = 0
	#static method for printing a list of nodes	
	@staticmethod
	def print_list(nodes):
		for n in nodes:
			if(isinstance(n, Node)):
				if(n.is_root):
					print str(n),
				else:
					print str(n) + '<-',
			else:
				Node.print_list(n)
	#pos: the node's position in the sentence, parent: the parent node, text: the word represented by the node, 
	#blank: whether the node represents a space (rather than a word)
	def __init__(self, _pos, _parent, _text, _blank,):
		#id (unique within sentence)
		self.id = Node.id_num
		self.pos = _pos
		#id of parent in previous revision
		assert isinstance(_parent, list)
		self.parent = _parent
		self.children = [] 
		self.alterations = {} 
		self.is_blank = _blank
		if(_parent == [None]):
			self.is_root = True
			self.ipos_tag = 'HEAD'
		else:
			self.is_root = False
			self.ipos_tag = [p.ipos_tag for p in _parent if not(p.is_root)]
		#word in sentence
		self.text = _text
		self.pos_tag = []
		Node.id_num +=1
	
	def __str__(self):
		if(self.is_root):
			return '[ Head ]'
		else:
			pid = [p.pos for p in self.parent] #str(self.parent[0].pos) + '-' + str(self.parent[len(self.parent)-1].pos)
			return '[pos:'+str(self.pos)+' parent:'+ str(pid) +' '+str(self.text)+']'
	
	def add_child(self, node):
		self.children.append(node)

	def was_deleted(self):
		if("delete" in [self.alterations[e].mode for e in self.alterations]):
			return True
		return False

	#when a node is changed during a revision, track the change made to the node and bubble up the change to its parent nodes	
	def alter(self, edit):
		self.alterations[edit.seq_id] = edit
		if(not(self.is_root)):
			for p in self.parent:
				p.alter(edit)

	#pos_tag this node and bubble up tag to parent node (used when tags are generated from final version of sentence)	
	def tag(self, _tag):
		self.pos_tag.append(_tag)
		if(not(self.is_root)):
			for p in self.parent:
				p.tag(_tag)

	#pos tag this node (used when tags are generated from initial, errorful version of sentence)
	def itag(self, _tag):
		self.ipos_tag.append(_tag)

	#get list of nodes that preceded this node (may return nested lists)	
	def lineage(self):
		l = [self]
		par = self.parent
		if(self.is_root):
			return [self]
		else:
			for p in par:
				l.append(p.lineage())
		return l

	#get the final version of this node, skipping intermediate edits and returning the node as it appears in final version
	#does not take into account nodes that split into multiple nodes, traces only the first node in this node's "offspring"	
	def get_ultimate_fate(self):
		if(self.children == []):
			return self 
		else:
			if(len(self.children) == 1):
				c = self.children[0]
				return c.get_ultimate_fate()
			else:
				c = self.children[1]
				return c.get_ultimate_fate()

	#opposite of get_lineage, get a nested dictionary of the nodes that are "offspring" of this node
	def get_fate(self):
		fate = {self : {}}
		if(self.children == []):
			return fate
		else:
			for c in self.children:
				fate[self][c] = c.get_fate()
		return fate

	#return a list of changes made to this node
	def get_alterations(self):
		return [self.alterations[id] for id in self.alterations]

	#True if this mode has been changed by mode mode, False otherwise	
	def has_changed(self, mode):
		for a in self.alterations:
			if(a.mode == mode):
				return True
		return False

#data structure holding a list of revisions which have been made on a sentence
class Sentence:
	POS_LIST = [] 
	id_num = 0
	#sent - the root sentence represented by this Sentence (not actually used during init. use initialize_sentence() method when creating a new 
	#Sentence
	def __init__(self, sent):
		self.id = Sentence.id_num
		self.head = Node(0, [None], "Head", False)
		#list of revisions
		self.revisions = []
		self.latest = 0
		Sentence.id_num += 1

	#perform the edit on the sentence (see Edit data structre)
	def revise(self, edit):
		#tag the first sentence
		if(self.latest == 0):
			itags = self.__get_initial_pos()
			idx = 0
			for r in self.revisions[0].words:
				if(r.is_blank):
					r.itag("BLANK")
				else:
					r.itag(itags[idx][1])
					idx += 1	
		last_revision = self.revisions[self.latest]
		new = last_revision.revise(edit)
		self.revisions.append(new)
		self.latest += 1	

	#print each revision of the sentence in order, with words surrounded by square brackets
	def clean_print(self):
		print '['+str(self.head.text)+']'
		for r in self.revisions:
			s = ""
			for w in r.words:
				s += '['+w.text+']'
			print s

	#print each revision of the sentence in order, in Revision string format
	def print_sent(self):
		for r in self.revisions:
			print str(r)			
	
	#return the plain text string of the final version of the sentence
	def plain_str(self):
		s = ""
		for n in self.revisions[self.latest].words:
			s += n.text + " "
		return s

	#print each word of the initial version of the sentence followed by the version of the node in teh final version of the sentence
	#each word is on its own line	
	def print_ultimate(self, buf=sys.stdout):
		f = self.get_ultimate_fates()
		for node in self.revisions[0].words:
			buf.write("["+str(node.pos)+"] ["+node.text + "] "+"<"+f[node.pos].text+">\n")
		buf.write('\n')

	#print the initial version of the sentence followed by the final version
	def print_final(self, buf=sys.stdout):
		buf.write("Initial: ")
		for node in self.revisions[0].words:
			buf.write("["+str(node.pos)+"] ["+node.text + "] ")
		buf.write('\n')
		buf.write("Final: ")
		for node in self.revisions[self.latest].words:
			buf.write("["+str(node.pos)+"] ["+node.text + "] ")
		buf.write('\n')
#		buf.write("Initial: " + str(self.revisions[0])+'\n')
#		buf.write("Final: " + str(self.revisions[self.latest])+'\n')
		buf.write('\n')

	#return a list of indicies of nodes in teh initial sentence that are deleted before the final version of the sentence
	def deleted_nodes(self):
		deletes = []
		for node in self.revisions[0].words:
			if(node.was_deleted()):
				deletes.append(node.pos)
		return deletes

	#trace each word in initial sentence to its version in the final sentence
	def get_fates(self):
		destiny = []
		for node in self.revisions[0].words:
			destiny.append(node.get_fate())
		return destiny
	
	#get final version of each word in original sentence
	def get_ultimate_fates(self):
		fates = {}
		for node in self.revisions[0].words:
			f = node.get_ultimate_fate()
		#	print node.text, f
			fates[node.pos] = f
		return fates

	#get list of all alterations made on this sentence. if pos is true, will return all alterations plus their corresponding parts of speech
	def get_alterations(self, pos=False):
		alts = {}
		if(pos):
			self.percolate_pos()
			for node in self.revisions[0].words:
				alts[node.pos] = {'alt' : node.get_alterations(), 'ipos' : node.ipos_tag, 'pos' : node.pos_tag}
		else:
			for node in self.revisions[0].words:
				alts[node.pos] = node.get_alterations()
		return alts

	#simplification of tagset
	def simplify(self, tag):
		# Natural Language Toolkit: POS Tag Simplification 
		# 
		# Copyright (C) 2001-2011 NLTK Project 
		# Author: Steven Bird <sb@csse.unimelb.edu.au> 
		# URL: <http://www.nltk.org/> 
 		# For license information, see LICENSE.TXT 
 		# http://khnt.hit.uib.no/icame/manuals/brown/INDEX.HTM 
 		brown_mapping1 = { 
		'j': 'ADJ', 'p': 'PRO', 'm': 'MOD', 'q': 'DET', 
		'w': 'WH', 'r': 'ADV', 'i': 'P', 
		'u': 'UH', 'e': 'EX', 'o': 'NUM', 'b': 'V', 
		'h': 'V', 'f': 'FW', 'a': 'DET', 't': 'TO', 
		'cc': 'CNJ', 'cs': 'CNJ', 'cd': 'NUM', 
		'do': 'V', 'dt': 'DET', 
		'nn': 'N', 'nr': 'N', 'np': 'NP', 'nc': 'N'} 
		brown_mapping2 = { 
		'vb': 'V', 'vbd': 'VD', 'vbg': 'VG', 'vbn': 'VN', 
		} 
 		tag = tag.lower()
		if tag[0] in brown_mapping1: 
			return brown_mapping1[tag[0]] 
 		elif tag[:2] in brown_mapping1:   # still doesn't handle DOD tag correctly 
			return brown_mapping1[tag[:2]] 
		try: 
 			if '-' in tag: 
				tag = tag.split('-')[0] 
			return brown_mapping2[tag] 
		except KeyError: 
			return tag.upper() 


	def __get_final_pos(self):
		s = ""
		for r in self.revisions[self.latest].words:
			s += r.text + " "
		toks = nltk.word_tokenize(figures.undo_csv_format(s))
		tagged = nltk.pos_tag(toks)
		for tag in tagged:
			if(not(self.simplify(tag[1]) in Sentence.POS_LIST)):
				Sentence.POS_LIST.append(self.simplify(tag[1]))
		return [(word, self.simplify(tag)) for word, tag in tagged]		

	def __get_initial_pos(self):
		s = ""
		for r in self.revisions[0].words:
			s += r.text + " "
		toks = nltk.word_tokenize(figures.undo_csv_format(s))
		tagged = nltk.pos_tag(toks)
		for tag in tagged:
			if(not(self.simplify(tag[1]) in Sentence.POS_LIST)):
				Sentence.POS_LIST.append(self.simplify(tag[1]))
		return [(word, self.simplify(tag)) for word, tag in tagged]		
	
	def percolate_pos(self):
		tags = self.__get_final_pos()
		idx = 0
		for r in self.revisions[self.latest].words:
			if(r.is_blank):
				r.tag("BLANK")
			else:
			#	print idx, tags
				r.tag(tags[idx][1])
				idx += 1	

	def __print_fate(self, dct):
		s = ""
		for key in dct:
			if(dct[key] == {}):
				return key.text #str(key)
			else:
				s += key.text + "->"+self.__print_fate(dct[key])
		return s

	def print_fates(self, buf=sys.stdout):
		for f in self.get_fates():
			buf.write(self.__print_fate(f)+'\n')

	def print_alterations(self, buf=sys.stdout):
		for a in self.get_alterations():
			buf.write(str(a)+'\n')
	
	def print_lineage(self, name):
		figures.draw_revisions(self.revisions, "figures/schematics/"+name) # "figures/sent-"+str(self.id))
	
	def print_lineagec(self, name):
		figures.draw_controls(self.revisions, "figures/control-schematics/"+name) # "figures/sent-"+str(self.id))
	
	
class Revision:
	def __init__(self, _num):
		self.num = _num
		#list of nodes
		self.words = []
		self.edit_num = -1

	def __str__(self):
		s = ""
		for w in self.words:
			s += str(w.text) + " "	
		return "{ "+str(self.num)+" "+str(self.edit_num)+" "+s+" }"

	def revise(self, edit):
		e = edit.mode.strip()
		if(e == "change"):
			return self.change(edit)
		if(e == "insert"):
			return self.insert(edit)
		if(e == "reorder"):
			return self.reorder(edit)
		if(e == "delete"):
			return self.delete(edit)
		else:
			return self

	#get new revision which uses this revision as a start and applies the change to the word as specified by edit
	def change(self, edit):
		new = Revision(self.num + 1)
		ewords = edit.new_wd.split()
		pos = 0
	        for w in self.words[:(2*(int(edit.sp_start))+1)]:
	#		print pos, w.text
			node = Node(pos, [w], w.text, w.is_blank)
	                new.words.append(node)
			w.add_child(node)
			pos += 1
		parent = []
		for w in self.words[(2*(int(edit.sp_start))+1):(2*(int(edit.sp_end)))]:
			parent.append(w)
		if(len(ewords) == 0):
			node = Node(pos, parent, "", True)
			new.words.append(node)
			for p in parent:
				p.add_child(node)
				p.alter(edit)
			pos += 1
		else:
	      		for w in ewords:
	#			print pos, w
				node = Node(pos, parent, w, False)
	                	new.words.append(node)
				for p in parent:
					p.add_child(node)
					p.alter(edit)
				pos += 1
				if(len(ewords)>1 and w != ewords[len(ewords)-1]):#if adding multiple words, put spaces between them
					n = Node(pos, parent, "", True)
					new.words.append(n)
					for p in parent:
						p.add_child(node)
						p.alter(edit)
					pos += 1
	        for w in self.words[(2*(int(edit.sp_end))): len(self.words)]:
	#		print pos, w.text
			node = Node(pos, [w], w.text, w.is_blank)
	                new.words.append(node)
			w.add_child(node)
			pos += 1
		new.edit_num = edit.seq_id
		return new 

	def insert(self, edit):
        	new = Revision(self.num + 1)
		ewords = edit.new_wd.split()
		pos = 0
		for w in self.words[:(2*(int(edit.sp_start))+1)]:
#			print pos, w.text
			node = Node(pos, [w], w.text, w.is_blank)
	                new.words.append(node)
			w.add_child(node)
			pos += 1
	        for w in ewords:
#			print pos, w
			if(2*(int(edit.sp_start)) < len(self.words)):
				parent = self.words[2*(int(edit.sp_start))]
			else:
				parent = self.words[len(self.words) - 1]
			node = Node(pos, [parent], w, False)
	                new.words.append(node)
			parent.add_child(node)
			parent.alter(edit)
			pos += 1
			node = Node(pos, [parent], "", True)
	                new.words.append(node)
			parent.add_child(node)
			parent.alter(edit)
			pos += 1
	        for w in self.words[(2*(int(edit.sp_start))+1): len(self.words)]:
#			print pos, w.text
			node = Node(pos, [w], w.text, w.is_blank)
	                new.words.append(node)
			w.add_child(node)
			pos += 1
		new.edit_num = edit.seq_id
		return new

	def reorder(self, edit):
		if(int(edit.sp_start) <= int(edit.new_wd)):
                	return self.__move_forward(edit)
        	else:
                	return self.__move_back(edit)

	def __move_back(self, edit):
		new = Revision(self.num + 1)
	        ewords = self.words[(2*(int(edit.sp_start))+1):(2*(int(edit.sp_end))+1)]
		pos = 0
	        for w in self.words[:(2*(int(edit.new_wd))+1)]:
	        	node = Node(pos, [w], w.text, w.is_blank)	
		        new.words.append(node)
			w.add_child(node)
			pos += 1
		onode = 2*(int(edit.sp_start))+1
	        for w in ewords:
	        	node = Node(pos, [self.words[onode]], w.text, w.is_blank)
		        new.words.append(node)
			self.words[onode].add_child(node)
			self.words[onode].alter(edit)
			onode += 1	
			pos += 1
	        for w in self.words[(2*(int(edit.new_wd))+1):(2*(int(edit.sp_start))+1)]:
			node = Node(pos, [w], w.text, w.is_blank)	
		        new.words.append(node)
			w.add_child(node)
			pos += 1
	        for w in self.words[(2*(int(edit.sp_end))+1):]:
	        	node = Node(pos, [w], w.text, w.is_blank)	
		        new.words.append(node)
			w.add_child(node)
			pos += 1
		new.edit_num = edit.seq_id
		return new

	def __move_forward(self, edit):
		new = Revision(self.num + 1)
	        ewords = self.words[(2*(int(edit.sp_start))+1):(2*(int(edit.sp_end))+1)]
	        pos = 0
		for w in self.words[:(2*(int(edit.sp_start))+1)]:
	        	node = Node(pos, [w], w.text, w.is_blank)	
		        new.words.append(node)
			w.add_child(node)
			pos += 1
	        for w in self.words[(2*(int(edit.sp_end))+1):(2*(int(edit.new_wd))+1)]:
			node = Node(pos, [w], w.text, w.is_blank)	
		        new.words.append(node)
			w.add_child(node)
			pos += 1
		onode = 2*(int(edit.sp_start))+1
	        for w in ewords:
	        	node = Node(pos, [self.words[onode]], w.text, w.is_blank)
		        new.words.append(node)
			self.words[onode].add_child(node)
			self.words[onode].alter(edit)
			onode += 1	
			pos += 1
	        for w in self.words[(2*(int(edit.new_wd))+1):]:
			node = Node(pos, [w], w.text, w.is_blank)	
		        new.words.append(node)
			w.add_child(node)
			pos += 1
		new.edit_num = edit.seq_id
		return new

	def delete(self, edit):
        	new = Revision(self.num + 1)
		ewords = edit.new_wd.split()
		pos = 0
		for w in self.words[:(2*(int(edit.sp_start))+1)]:
			node = Node(pos, [w], w.text, w.is_blank)
	                new.words.append(node)
			w.add_child(node)
			pos += 1
		for w in self.words[(2*(int(edit.sp_start))+1):(2*(int(edit.sp_end))+1)]:
			w.alter(edit)		
	        for w in self.words[(2*(int(edit.sp_end))+1): len(self.words)]:
			node = Node(pos, [w], w.text, w.is_blank)
	                new.words.append(node)
			w.add_child(node)
			pos += 1
		new.edit_num = edit.seq_id
		return new

#map of assignment id : {sentence_id : [edits]}
class EditGraph:
	def __init__(self, graph):
		self.data = graph
	
	def get_edits(self, sentid=None):
		edits = {}
		if(sentid==None):
			for assign in self.data:
				edits[assign] = [] 
				for s in self.data[assign]:
					for edit in self.data[assign][s]:
						edits[assign].append(edit)
		else:
			for assign in self.data:
				edits[assign] = [] 
				if sentid in self.data[assign]:
					for edit in self.data[assign][sentid]:
						edits[assign].append(edit)
		return edits

	#return data in for of sentid : {assignment : [edits]}
	def get_by_sent(self):
		by_sents = {}
		for assign in self.data:
			for s in self.data[assign]:
				if(not(s in by_sents)):
					by_sents[s] = {}
				for edit in self.data[assign][s]:
					if(not(assign in by_sents[s])):
						by_sents[s][assign] = []
					by_sents[s][assign].append(edit)
		return by_sents
			 
class RevisionGraph:
	"""Highest level data structure containing map from sentence id to all the revisions on that sentence"""
	def __init__(self, graph):
		self.data = graph
	
	def get_revisions(self, sentid=None):
		revs = []
		if(sentid==None):
			for s in self.data:
				for r in self.data[s]:
					revs.append(r)
		else:
			for r in self.data[sentid]:
				revs.append(r)
		return revs

def initialize_sentence(sent):
	words = nltk.word_tokenize(sent) # sent.split()
	graph = Sentence(sent)
	rev = Revision(0) 
	pos = 0
	n = Node(pos, [graph.head], "", True)
	pos += 1
	rev.words.append(n)
	for w in words:
		n = Node(pos, [graph.head], w, False)
		rev.words.append(n)
		pos += 1
		n = Node(pos, [graph.head], "", True)
		rev.words.append(n)
		pos += 1
	graph.revisions.append(rev)
	return graph

def generate_figures(graph, sentid=None):
   	if(sentid==None):
		for s in graph:
			s.print_lineage(str(s.id))
        else:
		i = 0
	        for s in graph[sentid]:
        	        s.print_lineage(sentid+'.'+str(i))
        	        i += 1

def get_single_graph(edits, sentence):
	s = initialize_sentence(sentence)
	for edit in these_edits:
		s.revise(edit)	
		graph.append(s)	
	return RevisionGraph(graph)
	
def get_graph(all_sents, all_edits):
	graph_by_sent = {}
	edits_by_sent = {}
	for assign in all_edits:
		if(not(assign in edits_by_sent)):
			edits_by_sent[assign] = {}
		for sent in all_edits[assign]:
			if(not(sent in graph_by_sent)):
				graph_by_sent[sent] = []
			if(not(sent in edits_by_sent[assign])):
				edits_by_sent[assign][sent] = []
			if(sent != None):
				start = all_sents[sent].strip()
				start = start.strip('"')
				s = initialize_sentence(start)
				these_edits = all_edits[assign][sent]
				these_edits.sort()
				for edit in these_edits:
					s.revise(edit)
					edits_by_sent[assign][sent].append(edit)
				graph_by_sent[sent].append(s)	
	return [RevisionGraph(graph_by_sent), EditGraph(edits_by_sent)]
