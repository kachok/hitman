insert into similar_hits_data (tweet_id, translation, similar_sentence, tensentences_assignment_id, language_id)
	select t.tweet_id, t.translation, tt.translation, a.id, h.language_id from tensentences_hits_results t, translations tt, assignments a, hits h
	where is_control=0 and 
	t.assignment_id=a.id and a.hit_id=h.id
	and tt.id=t.tweet_id
	and
	not exists (select * from similar_hits_data s where s.tensentences_assignment_id=t.assignment_id);
