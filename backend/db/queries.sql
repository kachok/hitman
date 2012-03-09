-- select assignments done for languages with per country counts

select name, country, count(*)
from

(select worker_id, max(country) as country from workers w, location l where w.id=l.worker_id group by worker_id) t
,
(select l.name, worker_id, a.id as assignment_id from assignments a, hits h, languages l where h.id=a.hit_id and h.language_id=l.id) t2
where t.worker_id=t2.worker_id
group by name, country order by name, count(*) desc;


select name, country, count(*), sum(total)

-- stats by language by country with total workers and assignments done
select name, country, count(*), sum(total)
from 
(
select ll.name, l.country, w.id, count(*) as total from languages ll, location l, workers w, assignments a, hits h
where h.id=a.hit_id and w.id=a.worker_id and l.assignment_id=a.id and ll.id=h.language_id
group by ll.name, l.country, w.id
) t
group by name, country
order by name, sum(total) desc

-- verify that synonyms grading works correctly
-- display all controls and their values
select assignment_id, data_status, is_control, are_synonyms from syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and sa.data_status<1 and is_control>0 order by shr.assignment_id;

--verify non-synonyms
select assignment_id, data_status, is_control, are_synonyms, ns.word, ns.non_synonym from non_synonyms ns, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and sa.data_status<1 and is_control=2 and ns.id=pair_id
and exists (select * 
from syn_hits_results shr, syn_assignments sa2 
where sa2.id=shr.assignment_id and sa2.data_status<1 and is_control>0 
and sa2.data_status=0 and sa2.id=sa.id)

--verify synonyms
select assignment_id, data_status, is_control, are_synonyms, s.word, s.synonym from synonyms s, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and sa.data_status<1 and is_control=1 and s.id=pair_id
and exists (select * 
from syn_hits_results shr, syn_assignments sa2 
where sa2.id=shr.assignment_id and sa2.data_status<1 and is_control>0 
and sa2.data_status=0 and sa2.id=sa.id)


-- verify rejected synonyms
select assignment_id, data_status, is_control, are_synonyms 
from syn_hits_results shr, syn_assignments sa 
where sa.id=shr.assignment_id and sa.data_status<1 and is_control>0 
and sa.data_status=0
order by shr.assignment_id, is_control;




-- verify Synonyms HITs results
-------------------------------
--select all failed controls
select count(*) from (select * from syn_hits_results where is_control>0 and quality=0) t;
--select all passed controls
select count(*) from (select * from syn_hits_results where is_control>0 and quality=1) t;


-- show all failed non-synonyms
select quality, is_control, are_synonyms, ns.word, ns.non_synonym 
from non_synonyms ns, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and shr.quality=0 and shr.is_control=2 and ns.id=pair_id

--show all failed synonyms
select quality, is_control, are_synonyms, s.word, s.synonym 
from synonyms s, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and shr.quality=0 and is_control=1 and s.id=pair_id


--show all non-failed synonyms
select quality, is_control, are_synonyms, ns.word, ns.non_synonym 
from non_synonyms ns, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and shr.quality=1 and shr.is_control=2 and ns.id=pair_id

--show all non-failed synonyms
select quality, is_control, are_synonyms, s.word, s.synonym 
from synonyms s, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and shr.quality=1 and is_control=1 and s.id=pair_id



-- counts of approved/rejected syn hits
select mturk_status, count(*) from syn_assignments group by mturk_status;

-- detailed stats on syn assignments
select status, mturk_status, data_quality, data_status, count(*) from syn_assignments group by status, mturk_status, data_quality, data_status order by status, mturk_status;


-- counts for vocabulary HITs
select mturk_status, count(*) from voc_assignments group by mturk_status;



-- select all Synonyms HITs with 3+ high quality assignments done
select hit_id, count(*) from syn_assignments where data_quality=1 group by hit_id having count(*)>=3;

-- update Synonyms HITs to be Open (closed if 3+ assignments have high quality)
update hits set status='Open' where hittype_id=77;

-- update Synonyms HITs to be Closed if 3+ assignments of high quality
update hits set status='Closed' where hittype_id=77 and exists (select * from (select hit_id, count(*) from syn_assignments where data_quality=1 group by hit_id having count(*)>=3) t where t.hit_id=id);


mturk=# select count(*) from (select hit_id, count(*) from syn_assignments where data_quality=1 group by hit_id having count(*)>=3) t;
 count 
-------
  2094
(1 row)




select count(*) from hits where hittype_id=77;
mturk=# select count(*) from syn_hits;
 count 
-------
  3246
(1 row)


-- magic formula to get averaged quality from synonyms HITs into syn_hits_data

select pair_id, avg(data_status) from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed' group by pair_id;

select pair_id, are_synonyms, avg(data_status), count(*), avg(data_status)*count(*) from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed' group by pair_id, are_synonyms order by pair_id;


-- total weights for yes/no/related per pair
select pair_id, are_synonyms, avg(data_quality), count(*), sum(data_quality) from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed' and are_synonyms='no' group by pair_id, are_synonyms order by pair_id;
select pair_id, are_synonyms, avg(data_quality), count(*), sum(data_quality) from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed' and are_synonyms='yes' group by pair_id, are_synonyms order by pair_id;
select pair_id, are_synonyms, avg(data_quality), count(*), sum(data_quality/2) from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed' and are_synonyms='related' group by pair_id, are_synonyms order by pair_id;


select pair_id, are_synonyms, avg(data_quality), count(*), sum(data_quality) 
from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed' 
group by pair_id, are_synonyms order by pair_id;


-- ultimate formula for judging if pair is synonymous or not
select pair_id, sum(no) as no, sum(yes+related/2) as yes from
(
select pair_id, are_synonyms, 
case when are_synonyms='no' then data_quality else 0 end as no,
case when are_synonyms='related' then data_quality else 0 end as related,
case when are_synonyms='yes' then data_quality else 0 end as yes,
data_quality
from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed'
) t
group by pair_id;





select count(*) from (
select pair_id, sum(no) as no, sum(yes+related/2) as yes from
(
select pair_id, are_synonyms, 
case when are_synonyms='no' then data_quality else 0 end as no,
case when are_synonyms='related' then data_quality else 0 end as related,
case when are_synonyms='yes' then data_quality else 0 end as yes,
data_quality
from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed'
) t
group by pair_id
) t2



-- for each syn pair return yes or no if it is graded
select pair_id,
case when yes>=no then 'yes' else 'no' end as output,
case when yes>=no then yes/(yes+no) else no/(yes+no) end as data_quality
, yes, no
 from (
select pair_id, sum(no) as no, sum(yes+related/2) as yes from
(
select pair_id, are_synonyms, 
case when are_synonyms='no' then data_quality else 0 end as no,
case when are_synonyms='related' then data_quality else 0 end as related,
case when are_synonyms='yes' then data_quality else 0 end as yes,
data_quality
from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed'
) t
group by pair_id
) t2;



--update pairs with output and quality values

update syn_hits_data shd set output=tt.output, data_quality=tt.data_quality from
(
select pair_id,
case when yes>=no then 'yes' else 'no' end as output,
case when yes>=no then yes/(yes+no) else no/(yes+no) end as data_quality
, yes, no
 from (
select pair_id, sum(no) as no, sum(yes+related/2) as yes from
(
select pair_id, are_synonyms, 
case when are_synonyms='no' then data_quality else 0 end as no,
case when are_synonyms='related' then data_quality else 0 end as related,
case when are_synonyms='yes' then data_quality else 0 end as yes,
data_quality
from syn_hits_results shr, assignments a, syn_hits sh where sh.id=a.hit_id and shr.assignment_id=a.id and sh.status='Closed'
) t
group by pair_id
) t2
) tt  where shd.id=tt.pair_id; 


-- query used to generate syn hits pairs

select * from
	(
	select vhr.translation, d.translation as wikilinks_translation , d.language_id
	from voc_hits_results vhr, dictionary d 
	where d.id=vhr.word_id and is_control=0
	and
	upper(trim(both ' ' from vhr.translation))!=upper(trim(both ' ' from d.translation))
	) t where not exists (select * from syn_hits_data shd where shd.translation=t.translation and shd.synonym=t.wikilinks_translation);
	

-- count
select count(*) from
(
select * from
	(
	select vhr.translation, d.translation as wikilinks_translation , d.language_id
	from voc_hits_results vhr, dictionary d 
	where d.id=vhr.word_id and is_control=0
	and
	upper(trim(both ' ' from vhr.translation))!=upper(trim(both ' ' from d.translation))
	) t where not exists (select * from syn_hits_data shd where shd.translation=t.translation and shd.synonym=t.wikilinks_translation)
) tt





-- select pairs from voc hit results which are not graded yet

select vhr.id, upper(trim(both ' ' from vhr.translation)), upper(trim(both ' ' from d.translation))
from voc_hits_results vhr, dictionary d where d.id=vhr.word_id and is_control=0 and quality is null order by random() limit 10;


--

select vhr.id, upper(trim(both ' ' from vhr.translation)), shd.translation, upper(trim(both ' ' from d.translation)), shd.synonym , shd.output, shd.data_quality
from voc_hits_results vhr, dictionary d, syn_hits_data shd 
where d.id=vhr.word_id and vhr.is_control=0 and vhr.quality is null 
and 
upper(trim(both ' ' from shd.translation))=upper(trim(both ' ' from vhr.translation))
and
upper(trim(both ' ' from shd.synonym))=upper(trim(both ' ' from d.translation)) 
and shd.output is not null
order by random() limit 10;



-- update voc_hits_results with all correct translations (e.g. synonyms=yes)

update voc_hits_results t set quality=0.99 where exists 
(select vhr.id, upper(trim(both ' ' from vhr.translation)), shd.translation, upper(trim(both ' ' from d.translation)), shd.synonym , shd.output, shd.data_quality
from voc_hits_results vhr, dictionary d, syn_hits_data shd 
where d.id=vhr.word_id and vhr.is_control=0 and vhr.quality is null 
and 
upper(trim(both ' ' from shd.translation))=upper(trim(both ' ' from vhr.translation))
and
upper(trim(both ' ' from shd.synonym))=upper(trim(both ' ' from d.translation)) 
and shd.output = 'yes'
and t.id=vhr.id);

-- update voc_hits_results with all incorrect translations (e.g. synonyms=no)
update voc_hits_results t set quality=0 where exists 
(select vhr.id, upper(trim(both ' ' from vhr.translation)), shd.translation, upper(trim(both ' ' from d.translation)), shd.synonym , shd.output, shd.data_quality
from voc_hits_results vhr, dictionary d, syn_hits_data shd 
where d.id=vhr.word_id and vhr.is_control=0 and vhr.quality is null 
and 
upper(trim(both ' ' from shd.translation))=upper(trim(both ' ' from vhr.translation))
and
upper(trim(both ' ' from shd.synonym))=upper(trim(both ' ' from d.translation)) 
and shd.output = 'no'
and t.id=vhr.id);


-- gap between unfinished Syn HITs and Syn data
mturk=# select output, status, count(*) from syn_hits_data shd, hits h where h.id=shd.hit_id group by output, status;

 output | status | count 
--------+--------+-------
 yes    | Closed | 10651
        | Open   |  9214
 no     | Closed |  5909
(3 rows)


-- gap between unfinished voc results
mturk=# select quality, count(*) from voc_hits_results group by quality;                                                                                                                                                                  
quality |  count  
---------+---------
         | 1147321
	   1 |  214138
       0 |   15665       
(3 rows)

-- Some random queries from pgAdmin

select are_synonyms, is_control, word, synonym from syn_hits_results shr, synonyms s where s.id=shr.pair_id and shr.is_control>0 and assignment_id=115 




select are_synonyms, is_control, word, synonym from syn_hits_results shr, synonyms s where s.id=shr.pair_id and shr.is_control>0 
and ( (is_control=1 and are_synonyms='no')) and assignment_id=66096;


select are_synonyms, is_control, word, non_synonym from syn_hits_results shr, non_synonyms s where s.id=shr.pair_id and shr.is_control>0 
and ( (is_control=2 and are_synonyms!='no')) and assignment_id=66096;




select name, country, count(*)
from

(select worker_id, max(country) as country from workers w, location l where w.id=l.worker_id group by worker_id) t
,
(select l.name, worker_id, a.id as assignment_id from assignments a, hits h, languages l where h.id=a.hit_id and h.language_id=l.id) t2
where t.worker_id=t2.worker_id
group by name, country order by name, count(*) desc;


SELECT * from hittypes ht, languages l where ht.language_id=l.id


select * from assignments a, hits h, hittypes ht where a.hit_id=h.id and h.hittype_id=ht.id and ht.typename='synonyms';


update assignments 
set data_status=avg_quality, status='Graded' 
from (select assignment_id as t_id, avg(quality) as avg_quality 
		from syn_hits_results 
		where is_control>0 
		group by assignment_id) t 
where t.t_id=assignments.id;



select * from assignments;

select * from assignments


select assignment_id as t_id, avg(quality) as avg_quality 
		from syn_hits_results 
		where is_control>0 
		group by assignment_id

select * from hits

select hit_id from syn_assignments
where data_quality=1
group by hit_id
having count(*)=3

select * from hits where
exists (
		


select * from assignments;

select * from syn_hits_results order by assignment_id;

select * from 


update syn_hits_results set quality=1 where is_control=2 and are_synonyms='no';
update syn_hits_results set quality=0 where is_control=2 and are_synonyms!='no';
update syn_hits_results set quality=1 where is_control=1 and are_synonyms!='no';
update syn_hits_results set quality=0 where is_control=1 and are_synonyms='no';


update syn_hits_results set quality=avg_quality from (select assignment_id as t_id, avg(quality) as avg_quality from syn_hits_results where is_control>0 group by assignment_id) t where t_id=assignment_id and is_control=0



update assignments set data_status=avg_quality from (select assignment_id as t_id, avg(quality) as avg_quality from syn_hits_results where is_control>0 group by assignment_id) t where t_id=id


select * from syn_assignments;

select * from assignments;
select * from hits where id in (352,353,345,357);

CREATE OR REPLACE VIEW syn_assignments AS 
 SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status
   FROM assignments a, syn_hits sh
  WHERE a.hit_id = sh.id ;



SELECT a.*, sh.mturk_hit_id FROM assignments a, syn_hits sh WHERE a.hit_id = sh.id and a.status='Graded' and (a.mturk_status!='Accepted' and a.mturk_status!='Rejected');

select * from syn_hits_workers_performance


 SELECT w.id, avg(a.data_status) AS quality, count(a.data_status) AS total
   FROM workers w, assignments a, hits h, hittypes ht
  WHERE a.worker_id = w.id AND  a.hit_id = h.id AND h.hittype_id = ht.id AND ht.typename::text = 'synonyms'::text
  GROUP BY w.id;
  
  
  select ht.name, a.status, a.mturk_status, count(*) from assignments a, hits h, hittypes ht, languages l
where
a.hit_id=h.id and h.hittype_id=ht.id
and h.language_id=l.id
group by ht.name, a.status, a.mturk_status
order by ht.name;


95230 

select l.prefix, l.name, t.assignments, t.rejected, t.approved, t.total, t2.completed
from
(select id, prefix, name from languages) l
,
(select language_id, sum(assignments) as assignments, sum(rejected) as rejected, sum(approved) as approved, count(*) as total from hits group by language_id) t
,
(select language_id, count(*) as completed from assignments a, hits h where a.hit_id=h.id group by language_id) t2
where
l.id=t.language_id
and
l.id=t2.language_id;

select language_id,  worker_id, count(*) as completed from assignments a, hits h where a.hit_id=h.id group by language_id, worker_id



update voc_hits_results vhr
set quality=1 
from voc_hits_results r, dictionary d
where r.assignment_id=h.id and h.hittype_id=77 and vhr.id=r.id


voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(vhr.translation)=upper(d.translation);



update voc_hits_results t
set quality=1
where exists (
select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(vhr.translation)=upper(d.translation) and t.id=vhr.id
)


select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(vhr.translation)=upper(d.translation);


select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id group by a.id, mturk_assignment_id having sum(quality)=2;


select * from workers w, assignments


-- assignments per worker

select * from 
(select worker_id, count(*) from assignments a group by worker_id) as total
left join
(select worker_id, count(*) from assignments a where a.mturk_status in ('Approved', 'Rejected') group by worker_id) as paid
on total.worker_id=paid.worker_id


select * from (select worker_id, count(*) from assignments a group by worker_id) as total left join (select worker_id, count(*) from assignments a where a.mturk_status in ('Approved', 'Rejected') group by worker_id) as paid on total.worker_id=paid.worker_id;


select * from assignments where worker_id=26 and mturk_status='Submitted' limit 10;


--all vocabulary control results
select * from voc_hits_results where is_control=0

--all pairs of words to run as synonyms
select vhr.*, d.translation as wikilinks_translation from voc_hits_results vhr, dictionary d where d.id=vhr.word_id and is_control=0


select count(*)
from
(
select vhr.*, d.translation as wikilinks_translation 
from voc_hits_results vhr, dictionary d 
where d.id=vhr.word_id and is_control=0
and
upper(trim(both ' ' from vhr.translation))=upper(trim(both ' ' from d.translation))
) t;


select count(*)
from
(
select vhr.*, d.translation as wikilinks_translation 
from voc_hits_results vhr, dictionary d 
where d.id=vhr.word_id and is_control=0
and
trim(trailing 'S' from upper(trim(both ' ' from vhr.translation)))=trim(trailing 'S' from upper(trim(both ' ' from d.translation)))
) t;


select * from
(
select vhr.translation, d.translation as wikilinks_translation , d.language_id
from voc_hits_results vhr, dictionary d 
where d.id=vhr.word_id and is_control=0
and
upper(trim(both ' ' from vhr.translation))!=upper(trim(both ' ' from d.translation))
) t where not exists (select * from syn_hits_data shd where shd.translation=t.translation and shd.synonym=t.wikilinks_translation)



-- update all non-control records in voc hits results based on 2 graded control per assignment
update voc_hits_results vhr 
set quality=t.avg_quality
from
(
select assignment_id, avg(quality) as avg_quality from voc_hits_results vhr where is_control=0 and quality is not null group by assignment_id having count(*)=2 
) t
where t.assignment_id=vhr.assignment_id and is_control=1;


-- selelct voc_assignments IDs and quality and number of ranked controls

select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 and status!='Closed' group by a.id, mturk_assignment_id having count(quality)=2
select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 group by a.id, mturk_assignment_id having count(quality)=1
select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 group by a.id, mturk_assignment_id having count(quality)=0

select a.id, mturk_assignment_id, avg(quality), count(quality), a.worker_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 group by a.id, mturk_assignment_id;

--mark all voc assignment as graded if they are not Closed and both controls are graded

update assignments a set status='Graded'
from
(select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 and status!='Closed' group by a.id, mturk_assignment_id having count(quality)=2) t
where a.id=t.id;



select count(*)
from
(
select * from
(
select vhr.translation, d.translation as wikilinks_translation , d.language_id
from voc_hits_results vhr, dictionary d 
where d.id=vhr.word_id and is_control=0
and
upper(trim(both ' ' from vhr.translation))!=upper(trim(both ' ' from d.translation))
) t where not exists (select * from syn_hits_data shd where shd.translation=t.translation and shd.synonym=t.wikilinks_translation)
) tt;



select status, count(*) from hits group by status;

select status, count(*) from assignments group by status;

select mturk_status, count(*) from assignments group by mturk_status;

select

select * from hits h, assignments a  where h.id=a.hit_id and h.hittype_id=77;

group by a.hit_id 
  




-- stats queries for dashboard

select * from languages;
select * from languages l left outer join hittypes ht on ht.language_id=l.id left outer join (select hittype_id, count(*) from hits h group by hittype_id) t on t.hittype_id=ht.id;

-- assignments that will be autoapproved in next 12 hours
select count(*) from buffer_assignments where autoapproval_time<now() + '12 hour'::interval and autoapproval_time>now();

--assignmetns by status

mturk=# select status, count(*) from buffer_assignments group by status;
  status   | count  
-----------+--------
 Submitted |  29606
 Rejected  |   1728
 Approved  | 110694
(3 rows)


-- get list of all tables
SELECT tablename FROM pg_tables where tablename not like 'pg_%';

-- create table from query
--create table assignments_2012_02_27 as select * from assignments;


-- CHEATERS!!!

--assignmetns with 5+ untranslated words
select * from voc_hits_workers_performance;
 (select assignment_id, count(*) from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and length(reason)>1 group by assignment_id having(count(*)>5));
 
 
select * from voc_hits_workers_performance p,
(select worker_id, count(*) as empty from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and length(reason)>1 group by worker_id) nt
where p.id=nt.worker_id;
 


select sum(total) from (select worker_id, count(*) as total from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id group by worker_id) t;





select * from 
(select id, avg(quality) as quality2, sum(total) as total2 from voc_hits_workers_performance group by id) t2, 
(select worker_id, count(*) as total from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and length(reason)>1 group by worker_id) t where t.worker_id=t2.id
;

select t.worker_id, quality2, total2, total_empty, total_all, cast(total_empty as float)/cast(total_all as float) as ratio from 
(select id, avg(quality) as quality2, sum(total) as total2 from voc_hits_workers_performance group by id) t2, 
(select worker_id, count(*) as total_empty from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and length(reason)>1 group by worker_id) t, 
(select worker_id, count(*) as total_all from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id group by worker_id) t3 
where t.worker_id=t2.id and t.worker_id=t3.worker_id
order by total_empty desc
;



-- list workers who cheat by answering not a word (can't translate, based on controls)

select t.worker_id, quality2, total2, total_empty, total_all, cast(total_empty as float)/cast(total_all as float) as ratio from 
(select id, avg(quality) as quality2, sum(total) as total2 from voc_hits_workers_performance group by id) t2, 
(select worker_id, count(*) as total_empty from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and vhr.is_control=0 and length(reason)>1 group by worker_id) t, 
(select worker_id, count(*) as total_all from voc_hits_results vhr, assignments a where vhr.is_control=0 and vhr.assignment_id=a.id group by worker_id) t3 
where t.worker_id=t2.id and t.worker_id=t3.worker_id
and cast(total_empty as float)/cast(total_all as float)>0.5 and total_all>20
order by total_empty desc
;


update workers set banned=true
where id in
(select t.worker_id from 
(select id, avg(quality) as quality2, sum(total) as total2 from voc_hits_workers_performance group by id) t2, 
(select worker_id, count(*) as total_empty from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and vhr.is_control=0 and length(reason)>1 group by worker_id) t, 
(select worker_id, count(*) as total_all from voc_hits_results vhr, assignments a where vhr.is_control=0 and vhr.assignment_id=a.id group by worker_id) t3 
where t.worker_id=t2.id and t.worker_id=t3.worker_id
and cast(total_empty as float)/cast(total_all as float)>0.5 and total_all>20 and t.worker_id=id
); 


-- checking controls for a failed Voc HITs based on worker id
select * from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and a.worker_id=163 and vhr.is_control=0;
select vhr.*, w.translation from voc_hits_results vhr, assignments a, dictionary w where vhr.assignment_id=a.id and a.worker_id=163 and vhr.is_control=0 and a.mturk_status='Rejected' and quality=0 and w.id=word_id;


select a.mturk_status, a.status, a.data_status, a.data_quality, vhr.*, d.translation from voc_hits_results vhr, assignments a, dictionary d where vhr.assignment_id=a.id and a.worker_id=163 and vhr.is_control=0 and a.mturk_status='Rejected' and d.id=word_id;
select a.mturk_status, a.status, a.data_status, a.data_quality, vhr.*, d.translation from voc_hits_results vhr, assignments a, dictionary d where vhr.assignment_id=a.id and a.worker_id=163 and vhr.is_control=0 and a.mturk_status='Rejected' and d.id=word_id;




--genereate new Synonyms HITs from Vocabulary HITs

select count(*) from
	(
	select vhr.translation, d.translation as wikilinks_translation , d.language_id
	from voc_hits_results vhr, dictionary d 
	where d.id=vhr.word_id and is_control=0
	and
	trim(trailing 'S' from upper(trim(both ' ' from vhr.translation)))!=trim(trailing 'S' from upper(trim(both ' ' from d.translation)))
	and length(trim(trailing 'S' from upper(trim(both ' ' from vhr.translation))))>0
	and length(trim(trailing 'S' from upper(trim(both ' ' from d.translation))))>0
	) t where not exists (select * from syn_hits_data shd 
	where trim(trailing 'S' from upper(trim(both ' ' from shd.translation)))=trim(trailing 'S' from upper(trim(both ' ' from t.translation))) 
	and trim(trailing 'S' from upper(trim(both ' ' from shd.synonym)))=trim(trailing 'S' from upper(trim(both ' ' from t.wikilinks_translation))));


-- top workers for russian
select * from voc_hits_workers_performance where language_id=2 and total>10 and quality>0.8 order by quality desc;	
	

-- translation of russian
select v.word, vhr.translation from voc_hits_results vhr, assignments a, hits h , vocabulary v 
where a.id=vhr.assignment_id and h.id=a.hit_id and  h.language_id=2 and is_control=1 and v.id=word_id and worker_id in (817, 3346, 1623,3973,3273,2587,1619,3342,3967,3343,127,1,2582,1618,3341,5,2345,782,1625,1614,3076);


-- select most popular translation for russion (from high quality workers)
select word, translation, count(*) from
(
select v.word, vhr.translation from voc_hits_results vhr, assignments a, hits h , vocabulary v 
where a.id=vhr.assignment_id and h.id=a.hit_id and  h.language_id=2 and is_control=1 and v.id=word_id 
and worker_id in (817, 3346, 1623,3973,3273,2587,1619,3342,3967,3343,127,1,2582,1618,3341,5,2345,782,1625,1614,3076)
) t
group by word, translation having count(*)>2 order by count(*) desc;




select word, translation, count(*) from
(
select v.word, vhr.translation from voc_hits_results vhr, assignments a, hits h , vocabulary v 
where a.id=vhr.assignment_id and h.id=a.hit_id and  h.language_id=34 and is_control=1 and v.id=word_id 
and worker_id in (3584, 2440, 162, 163, 929, 2447)
) t
group by word, translation having count(*)>2 order by count(*) desc;




-- languages with small number of controls
select language_id, count(*) from dictionary group by language_id having count(*)<=100;

--52, 85, 86, 91, 74, 6, 61, 94, 95, 62 --less then 10 controls
-- 86, 91?, 74, 62


select * from voc_hits_workers_performance where language_id=2 and total>10 and quality>0.8 order by quality desc;	
	

select word, translation, count(*) from
(
select v.word, vhr.translation from voc_hits_results vhr, assignments a, hits h , vocabulary v 
where a.id=vhr.assignment_id and h.id=a.hit_id and  h.language_id=86 and is_control=1 and v.id=word_id 
and exists (select * from voc_hits_workers_performance where total>10 and quality>0.75 and a.worker_id=id) and translation!=''
) t
group by word, translation having count(*)>2 order by count(*) desc;



-- good filtered list for all languages <100
select * from 

(select language_id, count(*) from dictionary group by language_id having count(*)<=100) small
,

(select word, translation, language_id, count(*) from
(
select v.word, vhr.translation, h.language_id from voc_hits_results vhr, assignments a, hits h , vocabulary v 
where a.id=vhr.assignment_id and h.id=a.hit_id  and is_control=1 and v.id=word_id 
and exists (select * from voc_hits_workers_performance where total>10 and quality>0.75 and a.worker_id=id)  and translation!='' and upper(word)!=upper(translation)
) t
group by word, translation, language_id having count(*)>2 order by count(*) desc
) dict
where dict.language_id=small.language_id;


select dict.language_id, count(*) from 

(select language_id, count(*) from dictionary group by language_id having count(*)<=100) small
,

(select word, translation, language_id, count(*) from
(
select v.word, vhr.translation, h.language_id from voc_hits_results vhr, assignments a, hits h , vocabulary v 
where a.id=vhr.assignment_id and h.id=a.hit_id  and is_control=1 and v.id=word_id 
and exists (select * from voc_hits_workers_performance where total>10 and quality>0.75 and a.worker_id=id)  and translation!='' and upper(word)!=upper(translation)
) t
group by word, translation, language_id having count(*)>2 order by count(*) desc
) dict
where dict.language_id=small.language_id group by dict.language_id;

-- 21 languages have extra controls, 44 languages have <100 controls



-- workers with multiple languages
select w.id, banned, count(*) from workers w, voc_hits_workers_performance p where w.id=p.id group by w.id, banned order by count(*) desc                                                        ;


-- ultimate stats

*Synonyms

*Vocabulary

	*Russian
	*Spanish
	...
	
# HITs
# of HITs Closed
# of Assignmetns
# of Assignments Submitted/Rejected/Approved | Open/Closed
# of Workers
Avg performance


*Workers

* Lookup workers by MTurk id


Languages

--mturk=#  select * from stats limit 1;                                                                                                                                                                    
-- id  | hittype_id | language_id | hittype_name | language_prefix | language_name | hits | hits_closed | assignments | a_closed | a_submitted | a_approved | a_rejected | workers | avg_performance 
-	
-- prepopulate stats table based on languages
insert into stats (language_id, language_name, language_prefix) select id, name, prefix from languages;

-- add hittypes
update stats set hittype_id=ht.id, hittype_name=typename from (select id, typename, language_id from hittypes) as ht where ht.language_id=stats.language_id;

update stats set hits=total from (select hittype_id, count(*) as total from hits group by hittype_id) h where h.hittype_id=stats.hittype_id;
update stats set hits_closed=total from (select hittype_id, count(*) as total from hits where status='Closed' group by hittype_id) h where h.hittype_id=stats.hittype_id;

update stats set assignments=total from (select hittype_id, count(*) as total from hits h, assignments a where a.hit_id=h.id group by hittype_id) h where h.hittype_id=stats.hittype_id;

update stats set a_closed=total from (select hittype_id, count(*) as total from hits h, assignments a where a.hit_id=h.id and a.status='Closed' group by hittype_id) h where h.hittype_id=stats.hittype_id;

update stats set a_submitted=total from (select hittype_id, count(*) as total from hits h, assignments a where a.hit_id=h.id and a.mturk_status='Submitted' group by hittype_id) h where h.hittype_id=stats.hittype_id;
update stats set a_rejected=total from (select hittype_id, count(*) as total from hits h, assignments a where a.hit_id=h.id and a.mturk_status='Rejected' group by hittype_id) h where h.hittype_id=stats.hittype_id;
update stats set a_approved=total from (select hittype_id, count(*) as total from hits h, assignments a where a.hit_id=h.id and a.mturk_status='Approved' group by hittype_id) h where h.hittype_id=stats.hittype_id;

-- update num of unique workers per hittype
update stats set workers=total from (select hittype_id, count(*) as total from
(
	select distinct hittype_id, worker_id from hits h, assignments a where a.hit_id=h.id
) as d
group by hittype_id) h where h.hittype_id=stats.hittype_id;

(select distinct hittype_id, worker_id from hits h, assignments a where a.hit_id=h.id) h where h.hittype_id=stats.hittype_id;

-- distinct worker/hittype_id
select distinct hittype_id, worker_id from hits h, assignments a where a.hit_id=h.id

--num of workers per hittype_id
select hittype_id, count(*) as total from
(
	select distinct hittype_id, worker_id from hits h, assignments a where a.hit_id=h.id
) as d
group by hittype_id


-- avg performance per hittype
update stats set avg_performance=avg_perf from (select  hittype_id, avg(a.data_status) as avg_perf from hits h, assignments a where a.hit_id=h.id group by hittype_id) h where h.hittype_id=stats.hittype_id;
