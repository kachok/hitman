# This is an example settings file. Customize these values for your
# app and rename the file as settings.py.

settings = {
    # put your AWS account access key and secret here
	"aws_access_key_id": "xxxx",
	"aws_secret_access_key": "xxxx"
	"service_name":"AWSMechanicalTurkRequester",
	"service_version":"2007-03-12",,
	"service_url":"http://mechanicalturk.sandbox.amazonaws.com",
	"external_submit":"http://workersandbox.mturk.com/mturk/externalSubmit"

	"vocabularyHITtype":{
		"AssignmentDurationInSeconds":"600",
		"Description":"Translate 10 words from foreign language to english",
		'Reward.1.Amount':'0.01',
		'Reward.1.CurrencyCode':'USD',
		"Title":"Word translation from foreign language to english",
		"AutoApprovalDelayInSeconds":"2592000",
		"Keywords":"translation, vocabulary, dictionary, foreign, english, language",
		"QualificationRequirement.1.QualificationTypeId":"00000000000000000040", # Worker_NumberHITsApproved
		"QualificationRequirement.1.Comparator":"GreaterThan",
		"QualificationRequirement.1.IntegerValue":"1",
	},

	"languages_file":"data/languages/ru.txt",

}
