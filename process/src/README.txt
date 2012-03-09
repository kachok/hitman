WORKFLOWS:
	Publish Vocabualry HITs workflow:
		Use wikilanguages-pipeline to preprocess data

		Use hitman-backend scripts to add new languages and publish HITs to MTurk
	
	Main flow
		Get all submitted assignments from MTurk into buffer table

		Push all assignments from buffer table into primary assignments table
		
		Pay all new workers for first 10 tasks only
		TODO: check with blocked list
		TODO: check how manu languages workers did (max)
		
		Review Vocabulary HITs and pay all workers with verifyable controls (~30%)
		
		Generate Synonyms HITs based on Vocabulary HITs results (using control words)
		
		Publish Synonyms HITs to MTurk
		
		Review Synonyms HITs and pay all workers
		
		Review Vcabulary HITs and pay all the workers
		
		
		(repeat) 
		 
--
RULES:

	Payment to new workers:
		For all workers calculate # of tasks done, # of tasks paid for
		Select workers with <10 tasks paid
			# of tasks to pay = 10 - # of tasks paid for
			pay top (# of tasks to pay) tasks for this worker			
			

	Vocabulary HITs review
		For all assignments
			Set quality=1 for all control words (2 out of 10) if worker translation match wiki-links based translation of control 
				(case insensitive, spaces removed from begining and end of the both strings and 'S' removed from end of the both words)
		For all not Closed assignments where sum(quality)=2 for controls 
			pay
			mark status as "Closed" and "Approved"


	Vocabulary HITs review
		select all Synonyms HITs that have 3 assignments completed with good quality
		for each Synonym HIT calculate average quality for all non controls
		assign quality to Synonyms HIT data based on average qualities
		
		
		For each vocabulary result, lookup synonyms data for match
		If match found assign quality to vocabulary result control
			value is synonym, assign 1
			value is non_synonym (control failed), assign 0
		
	Vocabulary HITs review
		select all vocabulary controls where value is empty or notaword (can't translate) (if you are 75% bump up)
			assign quality as 0 (failed control)		


		for all Vocabulary HITs assignments with both controls graded, calculate average quality between controls (e.g. 0, 0.5, 1)
			If workers performance >0.75, assume quality as 1
			
			if 1 - Approve, pay
			if 0.5 - Approve, pay
			if 0 - Reject, no pay
			if 0.5 - ??? Reject, no pay
			
	Synonyms HITs review
		select all synonyms HITs controls
			assign quality 1 for correect control and 0 for incorrect control
			assign average of two controls as quality to non control synonym pairs
			
			If worker's performance > 75%, bump up quality to 1
			If worker's performance <=50%, reject and assign quality to 0
			Otherwize reject/approve based on quality 0/1

--


pay_for_first10_tasks.py

	pay every worker for first 10 tasks 


multi_test.py

	downloads every single assignment from MTurk into buffer table
	
	estimated run time on 100K HITs ~6 min
	
	
buffer_update.py

	pushes all assignmetns from buffer table into assignments table	
	keeps buffer table intact (should be deleted afterwards)
	
	estimated run time on 60K assignments ~10 min
	
	doesn't modify status in assignmetns (only mturk_status)

review_vocabulary_hits.py

	finds all vocabulary hits results that are have correct controls and pays them
	runs on all assignmetns, tries to pay them even if they are paid already (just ignores mturk exceptions)
	modifies assignemtns to be in Closed/Approved status/mturk_status
	
	
review_synonyms_hits.py
	autograde all results using controls
	mark all assignments as Graded
	propagate all changes to MTurk
	mark all synonyms as Closed
	
	modifies assignments status to Closed, modifies mturk_status to Approved/Rejected
	75%+ workers results mod quality to 1	
	
generate_syn_hits.py

	UNDER CONSTRUCTION


get_assignments_multi.py
	RETIRED (replaced by multi_test.py)

russian_fix.py
	RETIRED (one time fix to loop through russina HITs and update HITType in MTurk)
