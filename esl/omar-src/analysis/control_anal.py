import extract_data
import edit_graph

"""Methods for organizing and analyzing control sentences' introduced errors and turkers responses to those errors"""


#Get the raw counts for each type of error
def get_counts(data):
	ret = {'insert' : 0, 'delete' : 0, 'change' : 0}
	for hit in data:
		for sent in data[hit]:
			for error in data[hit][sent]:
				mode = error[' mode'].strip()
				ret[mode] += 1
	return ret
	
#Average number of errors per sentence
def avgnumerr(data):
	total = 0
	errs = 0
	for hit in data:
		for sent in data[hit]:
			total += 1
			for error in data[hit][sent]:
				errs += 1
	return float(errs) / total

#Distribution of error count over control sents
def numerrdist(data, reps):
	counts = []
	for hit in data:
		for sent in data[hit]:
			errs = 0
			for error in data[hit][sent]:
				errs += 1
			for i in range(0, reps[sent]):
				counts.append(errs)
	return counts 

#Average number of turker-made corrections per sentence
def avgnumcorr(data):
	total = 0
	corr = 0
	for assign in data:
		for sent in data[assign]:
			total += 1
			for error in data[assign][sent]:
				corr += 1
	return float(corr) / total

#get list of (numhits, accuracy) for each turker
def acc_against_hits(hit_data, control_data, assign_data, both=False):
	workers = {}
	accs = {}
	accs2 = {}
	for hit in hit_data:
		for assign in hit_data[hit]:
			worker = assign_data[assign]
			if(not(worker in workers)):
				workers[worker] = 0
			if(not(worker in accs)):
				accs[worker] = 0
				accs2[worker] = 0
			workers[worker] += 1
			tp = 0
			tp2 = 0
			t = 0
			for sent in hit_data[hit][assign]:	
				t += 1
				fwd = formatworker(hit_data[hit][assign][sent])
				fcd = formatcontrol(control_data[hit][sent])
				p = grade_sent(fwd,fcd)
				tp += p
				if(both):
					p2 = grade_sent(fwd,fcd,grademode='i')
					tp2 += p2
			accs[worker] += (float(tp) / t)
			if(both):
				accs2[worker] += (float(tp2) / t)
	if(both):
		return [(workers[w], (accs[w] / workers[w])) for w in workers],  [(workers[w], (accs2[w] / workers[w])) for w in workers]
	return [(workers[w], (accs[w] / workers[w])) for w in workers]

#Average number of turker-made corrections per sentence
def numcorrdist(data):
	counts = []
	for assign in data:
		for sent in data[assign]:
			corr = 0	
			for error in data[assign][sent]:
				corr += 1
			counts.append(corr)
	return counts

#get the number of times each sentence was assigned to a worker for editing
def numassign(data):
	sents = {}
	for assign in data:
		for sent in data[assign]:
			if(not(sent in sents)):
				sents[sent] = 1
			else:	
				sents[sent] += 1
	return sents 

#get ID accuracy and ID+word accuracy dists
def accdist(worker_data, control_data):
	ids = []
	idsnwords = []
	for hit in worker_data:
		for assign in worker_data[hit]:
			for sent in worker_data[hit][assign]:
				fwd = formatworker(worker_data[hit][assign][sent])
				fcd = formatcontrol(control_data[hit][sent])
				i = grade_sent(fwd, fcd, grademode='i')
				iw = grade_sent(fwd, fcd, grademode='i+w')
				print i, iw
				assert i >= iw
				ids.append(i)
				idsnwords.append(iw)
	return ids, idsnwords

#get list of accuracies across all workers and sents
def grade_sents(worker_data, control_data):
	perfs = []
	for hit in worker_data:
		for assign in worker_data[hit]:
			for sent in worker_data[hit][assign]:
				fwd = formatworker(worker_data[hit][assign][sent])
				fcd = formatcontrol(control_data[hit][sent])
				p = grade_sent(fwd,fcd)
				if(not(p==None)):
					perfs.append(p)
	return perfs

#get list of accuracies across all workers and sents
def grade_sents_modes(worker_data, control_data, grademode='i+w'):
	dels = [] 
	chgs = []
	ints = []
	for hit in worker_data:
		for assign in worker_data[hit]:
			for sent in worker_data[hit][assign]:
				fwd = formatworker(worker_data[hit][assign][sent])
				fcd = formatcontrol(control_data[hit][sent])
				dg = grade_sent_mode(fwd,fcd,"delete", grademode)
				if(not(dg==None)):
					dels.append(dg)
				cg = grade_sent_mode(fwd,fcd,"change", grademode)
				if(not(cg==None)):
					chgs.append(cg)
				ig = grade_sent_mode(fwd,fcd,"insert", grademode)
				if(not(ig == None)):
					ints.append(ig)

	return dels, chgs, ints

def avgacc_modes(worker_data, control_data):
	dels, chgs, ints = grade_sents_modes(worker_data, control_data, grademode='i')
	delsw, chgsw, intsw = grade_sents_modes(worker_data, control_data, grademode='i+w')
	avgs = [float(sum(l)) / len(l) for l in [dels, chgs, ints]]
	avgsw = [float(sum(l)) / len(l) for l in [delsw, chgsw, intsw]]
	print avgs
	print avgsw
	return avgs, avgsw

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_sent_debug(candidate, ref, grademode='i+w', logfile="grade.log"):
	totalpts = 0
        total = 0
	edits = {}
	for edit in ref:
		total += 1
		edits[edit['idx']] = edit
		
	for cedit in candidate:
		logfile.write(cedit+'\n')
		idx = cedit['idx']
		if(idx in edits):
			if(grademode == 'i'):
				totalpts += idpoints(edits[idx], cedit)
			else:
				totalpts += corrpoints(edits[idx], cedit)
			edits.pop(idx)
	
	return float(totalpts) / total

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_sent(candidate, ref, grademode='i+w'):
	totalpts = 0
        total = 0
	edits = {}
	for edit in ref:
		total += 1
		edits[edit['idx']] = edit
		
	for cedit in candidate:
		idx = cedit['idx']
		if(idx in edits):
			if(grademode == 'i'):
				totalpts += idpoints(edits[idx], cedit)
			else:
				totalpts += corrpoints(edits[idx], cedit)
			edits.pop(idx)
	
	return float(totalpts) / total

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_sent_mode(candidate, ref, mode, grademode='i+w'):
	totalpts = 0
        total = 0
	edits = {}
	for edit in ref:
		if(edit['mode'] == mode):
			total += 1
			edits[edit['idx']] = edit
		
	for cedit in candidate:
		idx = cedit['idx']
		if(idx in edits):
			if(grademode == 'i'):
				totalpts += idpoints(edits[idx], cedit)
			else:
				totalpts += corrpoints(edits[idx], cedit)
			edits.pop(idx)
	
	if(total == 0):
		return None
	return float(totalpts) / total

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_sent_mode1(candidate, ref, mode):
	totalpts = 0
        total = 0
        for edit in ref:
		if(edit['mode'] == mode):
			total += 1
			p = 0
			for cedit in candidate:
				p = corrpoints(edit, cedit)
			if(not(p==None)):
				totalpts += p
	if(total == 0):
		return None
	return float(totalpts) / total


#util to put control error data in format for grading
def formatcontrol(sent):
	formatted = []
	for e in sent:
		edict = {}
		edict['idx'] = int(e[' err_idx'])
		edict['mode'] = e[' mode'].strip()
		edict['word'] = e[' oldwd'].strip()
		formatted.append(edict)
	return formatted
	
#util to put turker correction data in format for grading
def formatworker(sent):
	formatted = []
	for e in sent:
		edict = {}
		edict['idx'] = int(e.sp_start.strip())
		edict['mode'] = e.mode.strip()
		edict['word'] = e.new_wd.strip()
		edict['rank'] = e.seq_id.strip()
		formatted.append(edict)
	return sorted(formatted, key=lambda e : e['rank'], reverse=True)

#number of points, weighting between IDing error and making correction change	
def corrpoints(mistake, fix):
	pts = idpoints(mistake, fix)
	if(pts > 0):
		pts += wordpoints(mistake,fix)
	assert pts <= 2
	return float(pts) / 2

#point if error is found at correct location
def idpoints(mistake, fix):
        inverses = {'insert' : 'delete', 'delete' : 'insert', 'change' : 'change'}
        if(not(mistake['idx'] == fix['idx'])):
		return None
	if(inverses[mistake['mode'].strip()] == fix['mode']):
        	return 1
	return 0

#point if error is changed to correct word
def wordpoints(mistake, fix):
        if(mistake['word'] == fix['word']):
		return 1
        return 0

def getrevsforcontrols(data):
	sents = []
	for hit in data:
		print "Graphing control for HIT", hit
		for sent in data[hit]:
			s = None
			i = 0
			for err in data[hit][sent]:
				if(not(s)):
					s = edit_graph.initialize_sentence(err[' sentence'])
				e = extract_data.Edit()
				e.seq_id = i
				e.sp_start = int(err[' err_idx'])
				e.ep_end = int(err[' err_idx']) + 1
				e.old_wd = err[' oldwd']
				e.new_wd = err[' newwd']
				e.mode = err[' mode']
				s.revise(e)
				i += 1
			sents.append(s)
	return sents
				


		 
