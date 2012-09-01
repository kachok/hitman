"""
Library of functions for parsing edit data structures and organizing edits
"""

import edit_graph

sanity_check = {"change" : 0, "delete" : 0, "reorder" : 0, "insert" : 0}
sanity_totals = {"change" : 0, "delete" : 0, "reorder" : 0, "insert" : 0}
pos_sanity_check = {"change" : 0, "delete" : 0, "reorder" : 0, "insert" : 0}
pos_sanity_totals = {"change" : 0, "delete" : 0, "reorder" : 0, "insert" : 0}

def byn(data):
	retmap = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
	for sentnum in data:
		count = 0
		for sent in data[sentnum]:
			count += 1
		retmap[count][sentnum] = data[sentnum]
	return retmap


def by_mode(_data):
	data = byn(_data)
	retmap = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
	for n in retmap:
		submap = {"change" : 0, "delete" : 0, "reorder" : 0, "insert" : 0}
		for sentnum in data[n]:
			for sent in data[n][sentnum]:
				alts = sent.get_alterations()
				for a in alts:
					for e in alts[a]:
						submap[e.mode.strip()] += 1
		retmap[n] = submap
	return retmap

def by_pos(_data):
	data = byn(_data)
	retmap = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
	for n in retmap:
		submap = {"change" : {}, "delete" : {}, "reorder" : {}, "insert" : {}}
		for sentnum in data[n]:
			for sent in data[n][sentnum]:
				alts = sent.get_alterations(pos=True)
				for a in alts:
					if(not(alts[a]['alt'] == [])):
						for e in alts[a]['alt']:
							mode = e.mode.strip()
							if(mode == "delete"):
								pos = alts[a]['ipos'][0]
								if(not(pos in submap[mode])):
									submap[mode][pos] = 1
								else:
									submap[mode][pos] += 1
							else:	
								pos = alts[a]['pos']
								for p in pos:
									if(not(p in submap[mode])):
										submap[mode][p] = 1
									else:
										submap[mode][p] += 1
		retmap[n] = submap
	return retmap

def count_words(data, mode, n):
	retmap = {}
	for sentnum in data:
		corrs = {}
		for sent in data[sentnum]:
			alts = sent.get_alterations()
			found = False
			for a in alts:
				if(not(found)):
					for e in alts[a]:
						if(e.mode.strip() == mode):
							if(n == 3):
								sanity_totals[mode] += 1
							if(not(a in corrs)):
								corrs[a] = 0
								found = True
							else:
								corrs[a] += 1
								if(n == 3):
									sanity_check[mode] += 1
							break
		if(n==1):
			retmap[sentnum] = [float(corrs[idx]) / n for idx in corrs]
		else:	
			retmap[sentnum] = [float(corrs[idx]) / (n - 1) for idx in corrs]
	return retmap

def count_words_pos(data, mode, n, pos):
	retmap = {}
	for sentnum in data:
		corrs = {}
		for sent in data[sentnum]:
			alts = sent.get_alterations(pos=True)
			found = False
			for a in alts:
				if(not(found)):
					for e in alts[a]['alt']:
						poss = []
						if(mode == 'delete'):
							poss = alts[a]['ipos']
						else:
							poss = alts[a]['pos']
						if(e.mode.strip() == mode and (pos in poss)):
							pos_sanity_totals[mode] += 1
							if(not(a in corrs)):
								corrs[a] = 0
								found = True
							else:
								corrs[a] += 1
								pos_sanity_check[mode] += 1
							break
		if(n==1):
			retmap[sentnum] = [float(corrs[idx]) / n for idx in corrs]
		else:	
			retmap[sentnum] = [float(corrs[idx]) / (n - 1) for idx in corrs]
	return retmap

def sanitycheck():
	print sanity_check
	print sanity_totals
	print pos_sanity_check
	print pos_sanity_totals

def __agreement(_data, mode, n):
	data = byn(_data)
	chdata = count_words(data[n], mode, n)	
	cntsum = 0
	total = 0
	for num in chdata:
		for c in chdata[num]:
			cntsum += c
			total += 1
	return (float(cntsum) / total) * (n - 1)

	
def __agreement_pos(_data, mode, n):
	data = byn(_data)[n]
	print "compiling" , mode , "data..." 
	retmap = {p : 0 for p in edit_graph.Sentence.POS_LIST}
	for pos in retmap:
		print "...", pos	
		chdata = count_words_pos(data, mode, n, pos)	
		cntsum = 0
		total = 0
		for num in chdata:
			for c in chdata[num]:
				cntsum += c
				total += 1
		if(not(total == 0)):
			retmap[pos] = (float(cntsum) / total) * (n - 1)
	
	return retmap

def agreement(data, n=0, mode=None):
	ns = []
	modes = []
	retmap = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
	if(n == 0):
		ns = [1, 2, 3, 4]
	else:
		ns = [n]
	if(mode == None):
		modes = ["change", "insert", "delete", "reorder"]
	else:
		modes = [mode]			
		
	for nn in ns:
		submap = {"change" : 0, "delete" : 0, "reorder" : 0, "insert" : 0}
		for m in modes:
			submap[m] = __agreement(data, m, nn)
		retmap[nn] = submap
	print retmap[3]
	return retmap

def agreement_pos(data, n=3):
        if(n < 1 or n > 4):
        	print "invalid value for n"
		return
	retmap = {"change" : {}, "insert" : {}, "delete" : {}, "reorder" : {}}
        for m in retmap:
                retmap[m] = __agreement_pos(data, m, n)
	print retmap
        return retmap













