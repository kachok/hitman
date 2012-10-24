import csv
import extract_data
import sys
import edit_graph
import edit_anal
import figures 
import argparse 
import control_anal

print "Begin main..."

parser = argparse.ArgumentParser()
parser.add_argument('--data', dest='data', help='path to directory containing mturk data dump', action='store', default=False)
parser.add_argument('--controls', dest='controls', help='perform analysis on control data', action='store_true', default=False)
parser.add_argument('--controlsonly', dest='controlsonly', help='perform analysis on control data and not edit data', action='store_true', default=False)

args = parser.parse_args()

if(not(args.data)):
        print "usage: provide path to edit_data and sent_ids"
        exit(0)

print "Reading data from " + args.data + "..."

print "Mapping assignment ids to HIT ids..."

assign2hit = {}
assign2worker = {}

#util function for now, since I forgot to flesh out hits_data table with assignment ID
mturk2id = {}
hit_data = open(args.data+"/assign_data")
assignraw = csv.DictReader(hit_data)
for line in assignraw:
	aid = line['id'].strip()
	assignid = line[' mturk_assignment_id'].strip()
	mturk2id[assignid] = aid

hit_data = open(args.data+"/hit_data_dump")
raw = csv.DictReader(hit_data)
for line in raw:
	hit = line['hit_id'].strip()
	assign = line['assignment_id'].strip()
	wid = line['worker_id'].strip()
	if(assign in mturk2id):
		assign2hit[mturk2id[assign]] = hit
		assign2worker[mturk2id[assign]] = wid

rgraph = {}
egraph = {}

if(not(args.controlsonly)):
	edit_data = open(args.data+"/edit_data")
	sent_data = open(args.data+"/sent_ids")
	
	all_edits = extract_data.build_edit_map(edit_data, sent_data)

	all_sents = extract_data.build_sent_map(sent_data)

	graph = edit_graph.get_graph(all_sents, all_edits)

	rgraph = graph[0]
	egraph = graph[1]

if(args.controls or args.controlsonly):
	control_data = open(args.data+"/cntrl_data")
	all_controls = extract_data.build_control_map(control_data)

	sentrevs = control_anal.getrevsforcontrols(all_controls)
	for i, s in enumerate(sentrevs):
		name = "control"+str(i)
		s.print_lineagec(name)	
#	counts = control_anal.avgnumerr(all_controls)
#	print counts
#	corrcounts = control_anal.avgnumcorr(egraph.data)
#	print corrcounts

#	reps = control_anal.numassign(egraph.data)	
#	errs = control_anal.numerrdist(all_controls, reps)
#	corrs = control_anal.numcorrdist(egraph.data)
#	figures.counthisto(errs, corrs, path='figures/performance')
#	all_corrs = {}
#	for a in egraph.data:
	#	if(not(assign2hit[a] in all_corrs)):
	#		all_corrs[assign2hit[a]] = {}
	#	all_corrs[assign2hit[a]][a] = egraph.data[a]

#get performance distribution with and without caring about word choice
#	accs1, accs2 = control_anal.acc_against_hits(all_corrs, all_controls, assign2worker, both=True)
#	hitcounts = [count for (count, acc) in accs1]
#	accscores = [acc for (count, acc) in accs1]
#	hitcounts2 = [count for (count, acc) in accs2]
#	accscores2 = [acc for (count, acc) in accs2]
#	figures.perfscatter_both(hitcounts, accscores, hitcounts2, accscores2, path='figures/performance')
"""
#get performance distribution with and without caring about word choice
	ids, idsw = control_anal.accdist(all_corrs, all_controls)
	figures.acchisto(ids, idsw, path='figures/performance')

#get performance distribution
	perfs = control_anal.grade_sents(all_corrs, all_controls)
	figures.perfhisto(perfs, path='figures/performance')

	ds, cs, ins = control_anal.grade_sents_modes(all_corrs, all_controls)
	figures.perfhisto_mode(ds, cs, ins, path='figures/performance')

#get overall accuracy by mode, both kinds of accuracy calc
	avgs, avgsw = control_anal.avgacc_modes(all_corrs, all_controls)		
	figures.avgaccs(avgs, avgsw, path="figures/performance")
"""
#Plot the frequency of edit modes, partitioned based on number of redundancies
#figures.plot_modes(edit_anal.by_mode(rgraph.data), path="figures/agreement")

#Plot the agreement between workers, partitioned based on number of redundancies
#figures.plot_agreements(edit_anal.agreement(rgraph.data), path="figures/agreement")
#edit_anal.agreement(rgraph.data)

#print "...edits by pos..."
#data = edit_anal.by_pos(rgraph.data)[3]
###new_data = {}
#for m in data:
#	new_data[m] = {}
#	for p in data[m]:
#		if(not(p == 'BLANK')):
#			new_data[m][p] = data[m][p]
#figures.plot_pos(new_data, path="figures/agreement")

#print "...agreements by pos..."
#figures.plot_agreements_pos(edit_anal.agreement_pos(rgraph.data, n=3), path="figures/agreement")
#edit_anal.agreement_pos(rgraph.data, n=3)

#print "sanity check..."
#edit_anal.sanitycheck()


#print "writing final sentences to log..."
#log = open("edits.log", "w")


#for r in rgraph.get_revisions():
	#log.write(str(r.id)+" ")
#	r.print_final(log)
#	print r.get_alterations(pos=True)
#log.close()

#print "generating figures..."
#i = 0
#for s in rgraph.data:
#	edit_graph.generate_figures(rgraph.data, s)
#	i += 1	

#edit_graph.generate_figures(rgraph.data, '45480')

#for n in rgraph.data:
#	log.write("------------"+n+"-----------"+'\n')
#	for s in rgraph.data[n]:
#		log.write('\n')
#		#s.print_fates(log)
#		s.print_alterations(log)
#
#log.close()

print "FINISH"
