# -*- coding: utf-8 -*-
# library to work with languages and their properites in relationship to Wikipedia projects

import codecs
import logging

def get_languages_list(filename, target_language):
	logging.info("loading list of languages")
	langs=[]

	fd = codecs.open( filename ,"r","utf-16")
	line=fd.readline() #skip headers
	for line in fd:
		# process content
		content = line.split("	")

		#print content[0]," - ",content[1]
		lang=content[3]
		if (lang!=target_language):
			langs.append(lang)

	#print langs
	return langs

def get_languages_properties(filename, target_language):
	logging.info("loading list of languages' properties")
	langs_properties={}

	fd = codecs.open( filename ,"r","utf-16")
	line=fd.readline() #skip headers
	for line in fd:
		# process content
		content = line.split("	")

		#print content
		#print content[0]," - ",content[1]
		lang=content[3]
		name=content[1]
		direction=content[4]
		non_latin=content[5]
		rendering=content[6]
		constructed=content[7]
		langs_properties[lang]={"name":name,"direction":direction,"non-latin":non_latin,"rendering":rendering,"constructed":constructed}

	#print langs
	return langs_properties