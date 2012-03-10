
-- update Synonyms HITs to be Open (closed if 3+ assignments have high quality)
update hits set status='Open' where hittype_id=77;

-- update Synonyms HITs to be Closed if 3+ assignments of high quality
update hits set status='Closed' where hittype_id=77 and exists (select * from (select hit_id, count(*) from syn_assignments where data_quality=1 group by hit_id having count(*)>=3) t where t.hit_id=id);


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


-- grade all controls that have result matching wiki-links translation first
update voc_hits_results t set quality=1 where exists (select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and trim(trailing 'S' from upper(trim(both ' ' from vhr.translation)))=trim(trailing 'S' from upper(trim(both ' ' from d.translation))) and t.id=vhr.id);

-- update voc_hits_results with all correct translations (e.g. synonyms=yes)

update voc_hits_results t set quality=1 where exists 
(select vhr.id, upper(trim(both ' ' from vhr.translation)), shd.translation, upper(trim(both ' ' from d.translation)), shd.synonym , shd.output, shd.data_quality
from voc_hits_results vhr, dictionary d, syn_hits_data shd 
where d.id=vhr.word_id and vhr.is_control=0 and vhr.quality is null 
and 
trim(trailing 'S' from upper(trim(both ' ' from shd.translation)))=trim(trailing 'S' from upper(trim(both ' ' from vhr.translation)))
and
trim(trailing 'S' from upper(trim(both ' ' from shd.synonym)))=trim(trailing 'S' from upper(trim(both ' ' from d.translation))) 
and shd.output = 'yes'
and t.id=vhr.id);

-- update voc_hits_results with all incorrect translations (e.g. synonyms=no)
update voc_hits_results t set quality=0 where exists 
(select vhr.id, upper(trim(both ' ' from vhr.translation)), shd.translation, upper(trim(both ' ' from d.translation)), shd.synonym , shd.output, shd.data_quality
from voc_hits_results vhr, dictionary d, syn_hits_data shd 
where d.id=vhr.word_id and vhr.is_control=0 and vhr.quality is null 
and 
trim(trailing 'S' from upper(trim(both ' ' from shd.translation)))=trim(trailing 'S' from upper(trim(both ' ' from vhr.translation)))
and
trim(trailing 'S' from upper(trim(both ' ' from shd.synonym)))=trim(trailing 'S' from upper(trim(both ' ' from d.translation))) 
and shd.output = 'no'
and t.id=vhr.id);

-- update voc_hits_results with empty or can't translate values (quality=0)
update voc_hits_results t set quality=0 
where ((reason !='' and reason!='englishword') and trim(' ' from translation)='') and is_control=0

--update all non-controls based on average controls quality (when both controls are graded)
update voc_hits_results set quality=avg_quality from (select assignment_id as t_id, avg(quality) as avg_quality from voc_hits_results where is_control=0 group by assignment_id having count(quality)=2) t where t_id=assignment_id and is_control=1;

--update all voc assignmetns as Graded and calculate average quality, if both controls are graded
update assignments set data_status=avg_quality, status='Graded' 
from (select assignment_id as t_id, avg(quality) as avg_quality from voc_hits_results where is_control=0 group by assignment_id having count(quality)=2) t where t_id=id and status='Open';


