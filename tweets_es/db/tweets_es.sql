-- Table: tweets

-- DROP TABLE tweets;

CREATE TABLE tweets
(
  id serial NOT NULL,
  tweetid text,
  tweet text,
  language_id integer,
  CONSTRAINT tweets_id_pk PRIMARY KEY (id ),
  CONSTRAINT tweets_language_id_fk FOREIGN KEY (language_id)
      REFERENCES languages (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tweets
  OWNER TO dkachaev;


-- Table: translations

-- DROP TABLE translations;

CREATE TABLE translations
(
  id serial NOT NULL,
  tweetid text,
  tweet text,
  translation text,
  google text,
  bing text,
  language_id integer,
  CONSTRAINT translations_id_pk PRIMARY KEY (id ),
  CONSTRAINT translations_language_id_fk FOREIGN KEY (language_id)
      REFERENCES languages (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE translations
  OWNER TO dkachaev;

-- Table: parallel

-- DROP TABLE parallel;

CREATE TABLE parallel
(
  id serial NOT NULL,
  text1 text,
  text2 text,
  text3 text,
  text4 text,
  nottext text,
  language_id integer,
  CONSTRAINT parallel_id_pk PRIMARY KEY (id ),
  CONSTRAINT parallel_language_id_fk FOREIGN KEY (language_id)
      REFERENCES languages (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE parallel
  OWNER TO dkachaev;


-- Table: tensentences_hits_data

-- DROP TABLE tensentences_hits_data;

CREATE TABLE tensentences_hits_data
(
  id serial NOT NULL,
  hit_id integer,
  tweet_id integer,
  output character varying,
  data_quality real,
  language_id integer,
  CONSTRAINT tensentences_hits_data_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tensentences_hits_data
  OWNER TO dkachaev;
-- Table: tensentences_hits_results

-- DROP TABLE tensentences_hits_results;

CREATE TABLE tensentences_hits_results
(
  id serial NOT NULL,
  assignment_id integer,
  tweet_id integer,
  translation character varying,
  reason character varying,
  is_control integer,
  quality real,
  CONSTRAINT tensentences_hit_results_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tensentences_hits_results
  OWNER TO dkachaev;

-- Index: tshr_match

-- DROP INDEX tshr_match;

CREATE INDEX tshr_match
  ON tensentences_hits_results
  USING btree
  (assignment_id , tweet_id );

-- View: tensentences_hits

-- DROP VIEW tensentences_hits;

CREATE OR REPLACE VIEW tensentences_hits AS 
 SELECT h.id, h.mturk_hit_id, h.uuid, h.hittype_id, h.language_id, h.assignments, h.rejected, h.approved, ht.mturk_hittype_id, h.status
   FROM hits h, hittypes ht
  WHERE h.hittype_id = ht.id AND ht.typename::text = 'tensentences'::text;

ALTER TABLE tensentences_hits
  OWNER TO dkachaev;


-- Table: similar_hits_data

-- DROP TABLE similar_hits_data;

CREATE TABLE similar_hits_data
(
  id serial NOT NULL,
  hit_id integer,
  tweet_id integer,
  type character varying,
  translation character varying,
  similar_sentence character varying,
  tensentences_assignment_id integer,
  is_control integer,
  output character varying,
  data_quality real,
  language_id integer,
  CONSTRAINT similar_hits_data_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE similar_hits_data
  OWNER TO dkachaev;


-- Table: similar_hits_results

-- DROP TABLE similar_hits_results;

CREATE TABLE similar_hits_results
(
  id serial NOT NULL,
  assignment_id integer,
  pair_id integer,
  same character varying,
  good character varying,
  native character varying,
  correct character varying,
  machine character varying,
  is_control integer,
  quality real,
  CONSTRAINT similar_hit_results_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE similar_hits_results
  OWNER TO dkachaev;


-- Index: sshr_match

-- DROP INDEX sshr_match;

CREATE INDEX sshr_match
  ON similar_hits_results
  USING btree
  (assignment_id , pair_id , is_control );



CREATE INDEX sshr_match
  ON similar_hits_results
  USING btree
  (assignment_id , pair_id , is_control );

-- View: syn_hits

-- DROP VIEW syn_hits;

CREATE OR REPLACE VIEW similar_hits AS 
 SELECT h.id, h.mturk_hit_id, h.uuid, h.hittype_id, h.language_id, h.assignments, h.rejected, h.approved, ht.mturk_hittype_id, h.status
   FROM hits h, hittypes ht
  WHERE h.hittype_id = ht.id AND ht.typename::text = 'similar'::text;

ALTER TABLE similar_hits
  OWNER TO dkachaev;

-- Table: parallel

-- DROP TABLE parallel;

CREATE TABLE parallel
(
  id serial NOT NULL,
  text1 text,
  text2 text,
  text3 text,
  text4 text,
  nottext text,
  google text,
  bing text,
  language_id integer,
  active boolean,
  CONSTRAINT parallel_id_pk PRIMARY KEY (id ),
  CONSTRAINT parallel_language_id_fk FOREIGN KEY (language_id)
      REFERENCES languages (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE parallel
  OWNER TO dkachaev;


-- Function: add_tensentences_hits_result(integer, integer, text, text, integer)

-- DROP FUNCTION add_tensentences_hits_result(integer, integer, text, text, integer);

CREATE OR REPLACE FUNCTION add_tensentences_hits_result(assignment_id2 integer, tweet_id2 integer, translation2 text, reason2 text, is_control2 integer)
  RETURNS void AS
$BODY$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE tensentences_hits_results 
        SET 
		tweet_id=tweet_id2
        WHERE assignment_id=assignment_id2 AND tweet_id=tweet_id2;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO tensentences_hits_results (assignment_id, tweet_id, translation, reason, is_control) 
	    VALUES (assignment_id2, tweet_id2, translation2, reason2, is_control2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION add_tensentences_hits_result(integer, integer, text, text, integer)
  OWNER TO dkachaev;

-- Function: add_syn_hits_result(integer, integer, text, text, integer)

-- DROP FUNCTION add_syn_hits_result(integer, integer, text, text, integer);

CREATE OR REPLACE FUNCTION add_similar_hits_result(assignment_id2 integer, pair_id2 integer, same2 text, good2 text, native2 text, correct2 text, machine2 text, is_control2 integer)
  RETURNS void AS
$BODY$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE similar_hits_results 
        SET 
		same=same,
		good=good2,
		native=native2,
		correct=correct2,
		machine=machine2
        WHERE assignment_id=assignment_id2 AND pair_id=pair_id2 and is_control=is_control2;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO similar_hits_results (assignment_id, pair_id, same, good, native, correct, machine, is_control) 
	    VALUES (assignment_id2, pair_id2, same2, good2, native2, correct2, machine2,  is_control2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION add_similar_hits_result(integer, integer, text, text, text, text, text, integer)
  OWNER TO dkachaev;

-- Function: add_assignment(text, integer, text, timestamp without time zone, timestamp without time zone, timestamp without time zone, timestamp without time zone, timestamp without time zone, text, text)

-- DROP FUNCTION add_assignment(text, integer, text, timestamp without time zone, timestamp without time zone, timestamp without time zone, timestamp without time zone, timestamp without time zone, text, text);

CREATE OR REPLACE FUNCTION add_assignment(mturk_assignment_id2 text, hit_id2 integer, mturk_worker_id2 text, accept_time2 timestamp without time zone, submit_time2 timestamp without time zone, autoapproval_time2 timestamp without time zone, approval_time2 timestamp without time zone, rejection_time2 timestamp without time zone, result2 text, mturk_status2 text)
  RETURNS integer AS
$BODY$
DECLARE
newid INTEGER;
worker_id2 INTEGER;
BEGIN
    SELECT INTO worker_id2 id FROM workers
    WHERE mturk_worker_id=mturk_worker_id2;

    LOOP
        -- first try to update the key
        UPDATE assignments 
        SET 

mturk_assignment_id=mturk_assignment_id2, 
hit_id=hit_id2,
worker_id=worker_id2, 
accept_time=accept_time2,
submit_time=submit_time2,
approval_time=approval_time2,
rejection_time=rejection_time2,
autoapproval_time=autoapproval_time2,
result=result2,
mturk_status=mturk_status2

        WHERE mturk_assignment_id=mturk_assignment_id2;
        IF found THEN
            RETURN (SELECT id FROM assignments WHERE mturk_assignment_id=mturk_assignment_id2);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
    INSERT INTO assignments (mturk_assignment_id, hit_id, worker_id, accept_time, submit_time, autoapproval_time, approval_time, rejection_time, result, mturk_status) 
    VALUES (mturk_assignment_id2, hit_id2, worker_id2, accept_time2, submit_time2, autoapproval_time2, approval_time2, rejection_time2, result2, mturk_status2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION add_assignment(text, integer, text, timestamp without time zone, timestamp without time zone, timestamp without time zone, timestamp without time zone, timestamp without time zone, text, text)
  OWNER TO dkachaev;


