# this script scraps english to foreign translations of "Barack Obama" and "Australia" in 100 languages (from wikipedia)


import wikipydia
import codecs

words=["Barack Obama", "Australia"]

langs="ru,ur,de,fr,eu,eo,sl,fi,ca,sv,lt,war,nl,da,sk,he,pl,cs,hr,hu,it,bg,sr,kk,uk,ro,ja,ms,pt,ko,vi,tr,es,fa,id,ar,zh,hi,io,an,mk,mg,pms,ka,bs,wa,ga,cv,diq,ht,nds,nap,sq,hy,sh,tt,qu,yo,ceb,th,ne,ku,am,te,tl,su,ml,mr,jv,ta,gu,sw,no,kn,pnb".split(",")

lang="en"

dict={}

for word in words:
	#print "------"
	#print word
	#print "-"
	links= wikipydia.query_language_links(title=word, language=lang, limit=1000)
	#print len(links)
	for link in links:
		if link in dict:
			dict[link][word]=(links[link])
		else:
			dict[link]={word:links[link]}
		#print link, " - ",links[link]
		
print "# of languages: ",len(langs)

for l in langs:
	if l in dict:
		text=l+" : "
		for word in words:
			if word in dict[l]:
				text=text+dict[l][word]+" : "
			else:
				text=text+word+" : "
				
		
		print text
	else:
		print "---"		
		
print "prep str2img files"

fw=codecs.open("support_sentences.txt", 'w', 'utf-8')

fs=open("support_sequence.txt","w")

for l in langs:
	text=""
	for i, word in enumerate(words):
		#print i, len(words)
		if word in dict[l]:
			text=text+dict[l][word]
			if i!=len(words)-1: 
				text=text+" and "
		else:
			text=text+word
			if i!=len(words)-1: 
				text=text+" and "
			
	fw.write(text+"\n")
	fs.write(l+"\n")
	print text
	print l

fw.close()
fs.close()

