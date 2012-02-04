#!/usr/bin/env python

# Import libraries
import time
import hmac
import sha
import base64
import urllib
import xml.dom.minidom

import settings
import logging

from boto.mturk.connection import MTurkConnection

from time import sleep

## simple commands that use boto library

def conn():
	return MTurkConnection(aws_access_key_id=settings.settings["aws_access_key_id"],
	                      aws_secret_access_key=settings.settings["aws_secret_access_key"],
	                      host=settings.settings["service_url"].replace("https://",""))


# Define authentication routines
def generate_timestamp(gmtime):
	return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

def generate_signature(service, operation, timestamp, secret_access_key):
	my_sha_hmac = hmac.new(secret_access_key, service + operation + timestamp, sha)
	my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
	return my_b64_hmac_digest

def escape(s):
	s=s.replace("<","&lt;")
	s=s.replace(">","&gt;")
	#str=str.replace("&","&amp;")
	return s

def generate_params(operation):
	# assemble common parameters for MTurk call
	timestamp = generate_timestamp(time.gmtime())
	signature = generate_signature('AWSMechanicalTurkRequester', operation, timestamp, settings.settings["aws_secret_access_key"])
	
	# Construct the request
	parameters = {
	    'Service': settings.settings["service_name"],
	    'Version': settings.settings["service_version"],
	    'AWSAccessKeyId': settings.settings["aws_access_key_id"],
	    'Timestamp': timestamp,
	    'Signature': signature,
	    'Operation': operation,
	    }
	
	return parameters
	
def call_turk(operation, params2):
	# returns xml string with MTurk call results
	params=generate_params(operation)
	# Make the request
	url = settings.settings["service_url"]
	
	#parameters=dict(params.items()+params2.items())
	parameters=params.copy()
	parameters.update(params2)
	logging.debug(parameters)
	logging.debug(urllib.urlencode(params))

	result_xmlstr = urllib.urlopen(url, urllib.urlencode(parameters)).read()
	return result_xmlstr


def get_val(output, element):
	#returns value of specified element in output XML string
	result_xml = xml.dom.minidom.parseString(output)

	# Check for and print results and errors
	errors_nodes = result_xml.getElementsByTagName('Errors')
	if errors_nodes:
		print 'There was an error processing your request:'
		for errors_node in errors_nodes:
			for error_node in errors_node.getElementsByTagName('Error'):
				print '  Error code:    ' + error_node.getElementsByTagName('Code')[0].childNodes[0].data
				print '  Error message: ' + error_node.getElementsByTagName('Message')[0].childNodes[0].data
	
	nodes = result_xml.getElementsByTagName(element)
	return nodes[0].childNodes[0].data


def show():
	# search for HITs that are ready for review
	operation="SearchHITs"	
	params2={}
	result_xmlstr=call_turk(operation, params2)

	results=get_val(result_xmlstr,"NumResults")
	total=get_val(result_xmlstr,"TotalNumResults")
	logging.debug("results: %s, total:%s" % (results, total))

	result_xml = xml.dom.minidom.parseString(result_xmlstr)
	# Check for and print results and errors
	errors_nodes = result_xml.getElementsByTagName('Errors')
	if errors_nodes:
		print 'There was an error processing your request:'
		for errors_node in errors_nodes:
			for error_node in errors_node.getElementsByTagName('Error'):
				print '  Error code:    ' + error_node.getElementsByTagName('Code')[0].childNodes[0].data
				print '  Error message: ' + error_node.getElementsByTagName('Message')[0].childNodes[0].data

	print result_xmlstr

	nodes = result_xml.getElementsByTagName('HITId')
	for node in nodes:
		hit_id=node.childNodes[0].data

		print hit_id

def review():
	# search for HITs that are ready for review
	operation="GetReviewableHITs"	
	params2={}
	result_xmlstr=call_turk(operation, params2)

	results=get_val(result_xmlstr,"NumResults")
	total=get_val(result_xmlstr,"TotalNumResults")
	logging.debug("results: %s, total:%s" % (results, total))

	result_xml = xml.dom.minidom.parseString(result_xmlstr)
	# Check for and print results and errors
	errors_nodes = result_xml.getElementsByTagName('Errors')
	if errors_nodes:
		print 'There was an error processing your request:'
		for errors_node in errors_nodes:
			for error_node in errors_node.getElementsByTagName('Error'):
				print '  Error code:    ' + error_node.getElementsByTagName('Code')[0].childNodes[0].data
				print '  Error message: ' + error_node.getElementsByTagName('Message')[0].childNodes[0].data

	print result_xmlstr

	nodes = result_xml.getElementsByTagName('HITId')
	for node in nodes:
		hit_id=node.childNodes[0].data

		print hit_id

def cleanup():
	# search and disable/remove all HITs (except ones with Assignments or smth, see MTurk API docs)
	# TODO: probably better cleanup routine needed (some HITs may survive this cleanup)
	results=-1
	total=0
	while results<total:
		operation="SearchHITs"	
		params2={}
		result_xmlstr=call_turk(operation, params2)
		try:
			results=get_val(result_xmlstr,"NumResults")
			total=get_val(result_xmlstr,"TotalNumResults")
			logging.debug("results: %s, total:%s" % (results, total))
			print "results: %s, total:%s" % (results, total)

			result_xml = xml.dom.minidom.parseString(result_xmlstr)
			# Check for and print results and errors
			errors_nodes = result_xml.getElementsByTagName('Errors')
			if errors_nodes:
				print 'There was an error processing your request:'
				for errors_node in errors_nodes:
					for error_node in errors_node.getElementsByTagName('Error'):
						print '  Error code:    ' + error_node.getElementsByTagName('Code')[0].childNodes[0].data
						print '  Error message: ' + error_node.getElementsByTagName('Message')[0].childNodes[0].data
	

			nodes = result_xml.getElementsByTagName('HITId')
			for node in nodes:
				hit_id=node.childNodes[0].data
		
				operation="DisableHIT"
				params2={"HITId":hit_id}
				call_turk(operation, params2)
		except Exception:
			sleep(10)
		
"""
<?xml version="1.0"?>
<SearchHITsResponse><OperationRequest><RequestId>427ab760-8879-4689-bbf4-6367f5433211</RequestId></OperationRequest>
<SearchHITsResult><Request><IsValid>True</IsValid></Request>
<NumResults>10</NumResults><TotalNumResults>11</TotalNumResults>
<PageNumber>1</PageNumber>
<HIT><HITId>2VMBLYHVI44O3Q89JA4NHZSBEW5W2G</HITId><HITTypeId>2PFZ9O9Z6KW4AAYN6JIROFQ0OPL3CK</HITTypeId><CreationTime>2011-12-01T19:03:34Z</CreationTime><Title>Word translation from foreign language to english</Title><Description>Translate 10 words from foreign language to english</Description><Keywords>translation, vocabulary, dictionary, foreign, english, language</Keywords><HITStatus>Assignable</HITStatus><MaxAssignments>3</MaxAssignments><Reward><Amount>0.01</Amount><CurrencyCode>USD</CurrencyCode><FormattedPrice>$0.01</FormattedPrice></Reward><AutoApprovalDelayInSeconds>2592000</AutoApprovalDelayInSeconds><Expiration>2011-12-05T10:39:35Z</Expiration><AssignmentDurationInSeconds>600</AssignmentDurationInSeconds><NumberOfAssignmentsPending>0</NumberOfAssignmentsPending><NumberOfAssignmentsAvailable>3</NumberOfAssignmentsAvailable><NumberOfAssignmentsCompleted>0</NumberOfAssignmentsCompleted></HIT>
...
<HIT><HITId>2LOOQ1SNQQ7QHVOTQSBCQR12XXCR7O</HITId><HITTypeId>2PFZ9O9Z6KW4AAYN6JIROFQ0OPL3CK</HITTypeId><CreationTime>2011-12-01T19:03:35Z</CreationTime><Title>Word translation from foreign language to english</Title><Description>Translate 10 words from foreign language to english</Description><Keywords>translation, vocabulary, dictionary, foreign, english, language</Keywords><HITStatus>Assignable</HITStatus><MaxAssignments>3</MaxAssignments><Reward><Amount>0.01</Amount><CurrencyCode>USD</CurrencyCode><FormattedPrice>$0.01</FormattedPrice></Reward><AutoApprovalDelayInSeconds>2592000</AutoApprovalDelayInSeconds><Expiration>2011-12-05T10:39:35Z</Expiration><AssignmentDurationInSeconds>600</AssignmentDurationInSeconds><NumberOfAssignmentsPending>0</NumberOfAssignmentsPending><NumberOfAssignmentsAvailable>3</NumberOfAssignmentsAvailable><NumberOfAssignmentsCompleted>0</NumberOfAssignmentsCompleted></HIT>
</SearchHITsResult></SearchHITsResponse>


<?xml version="1.0"?>
<DisableHITResponse><OperationRequest><RequestId>5952287a-28c9-4738-9576-e57967d1a059</RequestId></OperationRequest><DisableHITResult><Request><IsValid>True</IsValid></Request></DisableHITResult></DisableHITResponse>
<?xml version="1.0"?>
<DisableHITResponse><OperationRequest><RequestId>d540041c-f51d-4832-bb76-e8b37a0045bf</RequestId></OperationRequest><DisableHITResult><Request><IsValid>True</IsValid></Request></DisableHITResult></DisableHITResponse>
"""
