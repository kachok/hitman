#from pyx import *
#import numpy as np
#import matplotlib.pyplot as plt
import datetime

NODE_WIDTH = 1 
NODE_HEIGHT = 0.5 

#Remove csv special characters and replace with normal ascii characters
def undo_csv_format(string):
    string = string.strip()
    string = string.replace("&amp;", '&')
    string = string.replace("&#44;", ',')
    string = string.replace("&gt;", '>')
    string = string.replace("&lt;", '<')
    string = string.replace("&quot;", '"')
    string = string.replace("&#39;", "'")
    return string

#Draw graph of errors added to controls
def draw_controls(revs, name):
	c = canvas.canvas()
	y = len(revs)	
	for r in revs:
		x = 0
		for w in r.words:
			if(w.is_blank):
				c.stroke(path.circle(x + (0.5*NODE_WIDTH), y + (0.5*NODE_HEIGHT), 0.25* NODE_WIDTH))
			else:
				c.stroke(path.rect(x, y, NODE_WIDTH, NODE_HEIGHT))

			c.text(x+(0.5*NODE_WIDTH), y+(0.5*NODE_HEIGHT), undo_csv_format(w.text), [text.halign.boxcenter, text.valign.middle])
			if(y < len(revs)): #not the original sentence
				for p in w.parent:
					px = NODE_WIDTH*(p.pos) + (0.5 * NODE_WIDTH)
					py = y + 4*NODE_HEIGHT
					c.stroke(path.line(px, py, x + (0.5 * NODE_WIDTH), y + NODE_HEIGHT))
			x += 1
		y -= 4*NODE_HEIGHT
	print name
	c.writePDFfile(name)

#Draw graph of edits to sentence
def draw_revisions(revs, name):
	c = canvas.canvas()
	print revs
	y = len(revs)	
	for r in revs:
		x = 0
		for w in r.words:
			changed = False
			if(w.is_blank):
				if(not(r == revs[0]) and (len(w.parent) > 1 or w.text != w.parent[0].text)):
				#	changed = True
					c.stroke(path.circle(x + (0.5*NODE_WIDTH), y + (0.5*NODE_HEIGHT), 0.25* NODE_WIDTH))
					c.fill(path.circle(x + (0.5*NODE_WIDTH), y + (0.5*NODE_HEIGHT), 0.25* NODE_WIDTH), [color.rgb.blue])
				else:
					c.stroke(path.circle(x + (0.5*NODE_WIDTH), y + (0.5*NODE_HEIGHT), 0.25* NODE_WIDTH))
			else:
				if(not(r == revs[0]) and (len(w.parent) > 1 or w.text != w.parent[0].text)):
				#	changed = True
					c.stroke(path.rect(x, y, NODE_WIDTH, NODE_HEIGHT))
					c.fill(path.rect(x, y, NODE_WIDTH, NODE_HEIGHT), [color.rgb.blue])
				else:
					c.stroke(path.rect(x, y, NODE_WIDTH, NODE_HEIGHT))

			c.text(x+(0.5*NODE_WIDTH), y+(0.5*NODE_HEIGHT), undo_csv_format(w.text), [text.halign.boxcenter, text.valign.middle])
			if(y < len(revs)): #not the original sentence
				for p in w.parent:
					px = NODE_WIDTH*(p.pos) + (0.5 * NODE_WIDTH)
					py = y + 4*NODE_HEIGHT
					c.stroke(path.line(px, py, x + (0.5 * NODE_WIDTH), y + NODE_HEIGHT))
				#	if(changed):
				#		if p.is_blank:
				#			c.fill(path.circle(px + (0.5*NODE_WIDTH), py + (0.5*NODE_HEIGHT), 0.25* NODE_WIDTH), [color.rgb.blue])
				#		else:	
				#			c.fill(path.rect(px, py, NODE_WIDTH, NODE_HEIGHT), [color.rgb.blue])
			x += 1
		y -= 4*NODE_HEIGHT
	c.writePDFfile(name)

def plot_agreements(data, n=0, path=None):
	fig = plotbyn(data, n, path)
	plt.suptitle("Annotator agreement across edit modes")
	if(not(path==None)):
		dt = datetime.datetime.now()
		name = dt.strftime("agr-%Y-%m-%d-%H:%M:%S")
		plt.savefig(path+"/"+name)
	plt.show()

def plot_pos(data, n=0, path=None):
        fig = plotbypos(data, path)
        plt.suptitle("Parts of speech edited across edit modes")
        if(not(path==None)):
                dt = datetime.datetime.now()
                name = dt.strftime("pos-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
        plt.show()
	
def plot_agreements_pos(data, n=0, path=None):
        fig = plotbypos(data, path)
        plt.suptitle("Annotator across parts of speech")
        if(not(path==None)):
                dt = datetime.datetime.now()
                name = dt.strftime("posagr-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
        plt.show()
	
def plot_modes(data, n=0, path=None):
	fig = plotbyn(data, n, path)
	plt.suptitle("Number of edits by edit mode")
	if(not(path==None)):
		dt = datetime.datetime.now()
		name = dt.strftime("mod-%Y-%m-%d-%H:%M:%S")
		plt.savefig(path+"/"+name)
	plt.show()
	

def __plotone(data, n, path):
	fig = plt.figure()
	lbls = data[n].keys()
	yax = [data[n][k] for k in lbls]
	xax = range(len(yax)) 
	fig1 = fig.add_subplot(111)
	fig1.bar(xax, yax, align="center")
	fig1.set_xticks(xax)
	fig1.set_xticklabels(lbls)
	fig1.set_title(str(n)+" x redundant")
	return fig

def plotbypos(data, path=None):
	names = {'': "n/a", 'ADV': "adv.", 'VD': "verb (past)", 'P': "prep.", 'ADJ': "adj.", 'PRO': "pro.", 'V': "verb (inf)", ',': "comma", 'VN': "verb (part.)", 'WH': "wh pro./det.", 'TO': "to", 'N': "noun", 'VBP': "verb (be)", '.': "end punc.", 'VBZ': "verb (pres.)", ':': "colon", 'CNJ': "conj.", 'MOD': "mod. aux.", 'VG': "verb (ger.)", 'NUM': "num (card.)", 'EX': "num (ord.)", 'DET': "det." }
	locs = {'change' : 221, 'insert' : 222, 'delete' : 223, 'reorder' : 224}
        fig = plt.figure()
	for nn in data: 
		lbls = data[nn].keys()
		yax = [data[nn][k] for k in lbls] 
		xax = range(len(yax))
		fig1 = fig.add_subplot(locs[nn]) 
		fig1.bar(xax, yax, align="center") 
		fig1.set_xticks(xax) 
		fig1.set_xticklabels([names[k] for k in lbls])
		fig1.set_title(nn)
		plt.setp(fig1.get_xticklabels(), fontsize=8, rotation='vertical')
		plt.tight_layout()
      #  fig.autofmt_xdate()
	return fig

def plotbyn(data, n=0, path=None):
	if(n == 0):
		locs = {1 : 221, 2 : 222, 3 : 223, 4 : 224}
		fig = plt.figure()
		for nn in data:
			lbls = data[nn].keys()
			yax = [data[nn][k] for k in lbls]
			xax = range(len(yax)) 
			fig1 = fig.add_subplot(locs[nn])
			fig1.bar(xax, yax, align="center")
			fig1.set_xticks(xax)
			fig1.set_xticklabels(lbls)
			fig1.set_title(str(nn)+" x redundant")
		return fig
	else:
		__plotone(data, n, path)

def avgaccs(avgs1, avgs2, path=None):
	width = 0.5
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	lbls = ['Delete', 'Change', 'Insert']
	xax = np.arange(len(lbls)) #range(len(avgs1)) 
	fig1.bar(xax, avgs1, width, align="center", color="blue")
	fig1.bar(xax+width, avgs2, width, align="center", color="red")
	fig1.set_title("Average error correction accuracy by error type")
	plt.ylabel("Average accuracy")
	plt.legend(('Error correctly identified', 'Error correctly identified and edited'), loc=8)
	fig1.set_xticks(xax)
	fig1.set_xticklabels(lbls)
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("avgaccs-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()
	
	
def perfhisto(perfs, path=None):
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	fig1.hist(perfs, bins=10)
	fig1.set_title("Error correction accuracy by turkers on artificially-generated errors")
	plt.xlabel("Percent of errors corrected")
	plt.ylabel("Number of sentences")
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("perfhisto-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()


def counthisto(errs, corrs, path=None):
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	fig1.hist([errs, corrs], bins=10)
	fig1.set_title("Number of errors present per sentence")
	plt.xlabel("Number of errors")
	plt.ylabel("Number of sentences")
	plt.legend(('Number of actual errors present', 'Number of corrections made by turkers'))
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("counthisto-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()
	
def acchisto(ids, idsw, path=None):
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	fig1.hist([ids, idsw], bins=10)
	fig1.set_title("Error identification and correction accuracy by turkers on artificially-generated errors")
	plt.xlabel("Percent of errors corrected")
	plt.ylabel("Number of sentences")
	plt.legend(('Error correctly identified', 'Error correctly identified and edited'))
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("acchisto-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()
	
def perfhisto_mode(dels, chgs, ints, path=None):
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	fig1.hist([dels, chgs, ints], bins=10)
	fig1.set_title("Error correction accuracy by turkers on artificially-generated errors, by error type")
	plt.xlabel("Percent of errors corrected")
	plt.ylabel("Number of sentences")
	plt.legend(('Deletions', 'Changes', 'Inserts'))
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("perfhistomode-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()

def perfscatter(hitcounts, accs, path=None):
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	fig1.scatter(hitcounts, accs)
	fig1.set_title("Worker accuracy against number of HITs submitted")
	plt.xlabel("Number of HITs submitted")
	plt.ylabel("Average accuracy per HIT")
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("perfscatter-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()

def perfscatter_both(hitcounts1, accs1, hitcounts2, accs2, path=None):
	fig = plt.figure()
	fig1 = fig.add_subplot(111)
	fig1.scatter(hitcounts1, accs1, color='blue')
	fig1.scatter(hitcounts2, accs2, color='red')
	fig1.set_title("Worker accuracy against number of HITs submitted")
	plt.xlabel("Number of HITs submitted")
	plt.ylabel("Average accuracy per HIT")
	if(path):
                dt = datetime.datetime.now()
                name = dt.strftime("perfscatterb-%Y-%m-%d-%H:%M:%S")
                plt.savefig(path+"/"+name)
	plt.show()





