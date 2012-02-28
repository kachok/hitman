-- select assignments done for languages with per country counts

select name, country, count(*)
from

(select worker_id, max(country) as country from workers w, location l where w.id=l.worker_id group by worker_id) t
,
(select l.name, worker_id, a.id as assignment_id from assignments a, hits h, languages l where h.id=a.hit_id and h.language_id=l.id) t2
where t.worker_id=t2.worker_id
group by name, country order by name, count(*) desc;


-- verify that synonyms grading works correctly
-- display all controls and their values
select assignment_id, data_status, is_control, are_synonyms from syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and sa.data_status<1 and is_control>0 order by shr.assignment_id;

--verify non-synonyms
select assignment_id, data_status, is_control, are_synonyms, ns.word, ns.non_synonym from non_synonyms ns, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and sa.data_status<1 and is_control=2 and ns.id=pair_id;

--verify synonyms
select assignment_id, data_status, is_control, are_synonyms, s.word, s.synonym from synonyms s, syn_hits_results shr, syn_assignments sa where sa.id=shr.assignment_id and sa.data_status<1 and is_control=1 and s.id=pair_id;


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


	
	

