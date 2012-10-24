def do_change(sent, edit):
	words = sent.split()
	ewords = edit.new_wd.split()
	nwords = []
	for w in words[:int(edit.sp_start)]: #range(0, int(edit.sp_start)):
		nwords.append(w)
	for w in ewords:
		nwords.append(w)
	for w in words[int(edit.sp_end):]: #range(int(edit.sp_end)-1, len(words)):
		nwords.append(w)
	retstr = ""
	for w in nwords:
		retstr += w + " "
#	print retstr
	return retstr	
	
def do_move(sent, edit):
	if(int(edit.sp_start) <= int(edit.new_wd)):
		return move_forward(sent, edit)
	else:
		return move_back(sent, edit)
	
def move_back(sent, edit):
	print "move back"
	print "EDIT: "+ str(edit)
	words = sent.split()
	ewords = words[int(edit.sp_start):int(edit.sp_end)]
	nwords = []
	for w in words[:int(edit.new_wd)]:
		nwords.append(w)
	for w in ewords:
		nwords.append(w)
	for w in words[int(edit.new_wd):int(edit.sp_start)]:
		nwords.append(w)
	for w in words[int(edit.sp_end):]:
		nwords.append(w)
	retstr = ""
	for w in nwords:
		retstr += w + " "
	return retstr

def move_forward(sent, edit):
	print "move forward"
	print "EDIT: "+ str(edit)
	words = sent.split()
	ewords = words[int(edit.sp_start):int(edit.sp_end)]
	nwords = []
	for w in words[:int(edit.sp_start)]:
		nwords.append(w)
	for w in words[int(edit.sp_end):int(edit.new_wd)]:
		nwords.append(w)
	for w in ewords:
		nwords.append(w)
	for w in words[int(edit.new_wd):]:
		nwords.append(w)
	retstr = ""
	for w in nwords:
		retstr += w + " "
	return retstr

def do_insert(sent, edit):
	words = sent.split()
	ewords = edit.new_wd.split()
	nwords = []
	#print words
	for w in words[:int(edit.sp_start)]: #range(0, int(edit.sp_start)):
		nwords.append(w)
	for w in ewords:
		nwords.append(w)
	for w in words[int(edit.sp_start):]: #range(int(edit.sp_end)-1, len(words)):
		nwords.append(w)
	retstr = ""
	for w in nwords:
		retstr += w + " "
	return retstr	

def do_delete(sent, edit):
	words = sent.split()
	nwords = []
	for w in words[:int(edit.sp_start)]: #range(0, int(edit.sp_start)):
		nwords.append(w)
	for w in words[int(edit.sp_end):]: #, len(words)):
		nwords.append(w)
	retstr = ""
	for w in nwords:
		retstr += w + " "
	return retstr	

def do_edit(sent, edit):
	typ = edit.mode
	retstr = ""
	if(typ == "change"):
		retstr = do_change(sent, edit)
	if(typ == "reorder"):
		retstr = do_move(sent, edit)
	if(typ == "insert"):
		retstr = do_insert(sent, edit)
	if(typ == "delete"):
		retstr = do_delete(sent, edit)
	return retstr




