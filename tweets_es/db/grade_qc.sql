
update similar_hits_results set quality=1 where quality is null;
	
update similar_hits_results set quality=0 where is_control=1 and same='no';
update similar_hits_results set quality=0 where is_control=2 and same='yes';
update similar_hits_results set quality=0 where is_control=3 and same='yes';
update similar_hits_results set quality=0.5 where is_control=3 and same='yes' and machine='no';
update similar_hits_results set quality=0.75 where is_control=3 and same='yes'and machine ='maybe';
update similar_hits_results set quality=1 where is_control=3 and same='yes'and machine ='yes';
update similar_hits_results set quality=0.5 where is_control=3 and same='no'and machine ='yes';
update similar_hits_results set quality=0.25 where is_control=3 and same='no'and machine ='maybe';
update similar_hits_results set quality=0 where is_control=3 and same='no'and machine ='no';

	
-- update individual non-control results for similar HIT
update similar_hits_results shr set quality=(select quality from 
	(
		select assignment_id, avg(quality) as quality from similar_hits_results 
		where is_control>0
		group by assignment_id
	) t
	where t.assignment_id=shr.assignment_id
)
where is_control=0;

--update similar HITs assignments with quality data (used for accepting/rejecting mturk work)
update assignments set data_status=avg_quality
from (
	select assignment_id as t_id, avg(quality) as avg_quality 
	from similar_hits_results 
	
	where is_control>0 group by assignment_id) t 
where t_id=id;



-- update similar HITs source data to trace results back to 10 sentence translation HITs

-- need to adjust to grade similar_hits_data only for HITs with 3 good assignments

update similar_hits_data
set data_quality=avg_quality,
	same=avg_same,
	machine=avg_machine
from (
	select r.pair_id, avg(r.quality) as avg_quality, avg(r.same) as avg_same,  avg(r.machine) as avg_machine
	from
		similar_hits_data d,
		(
				select assignment_id, pair_id, quality, 
					case when same='yes' then 1 else 0 end as same,
					case when machine='yes' then 1 when machine='maybe' then 0.5 else 0 end as machine
				from similar_hits_results  where is_control=0 and quality=1
			) r,
		hits h,
		assignments a
	where 
		r.assignment_id=a.id and
		a.hit_id=h.id and
		d.hit_id=h.id and
		d.id=r.pair_id	
	group by r.pair_id
	having count(*)>=3
) t where t.pair_id=similar_hits_data.id;




