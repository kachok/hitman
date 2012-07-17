-- Table: vocabulary

-- DROP TABLE esl_sentences;

CREATE TABLE esl_sentences
(
  id serial NOT NULL,
  sentence character varying,
  sequence_num integer,

  language_id integer,
  CONSTRAINT esl_sentences_id_pk PRIMARY KEY (id ),
  CONSTRAINT esl_sentences_language_id_fk FOREIGN KEY (language_id)
      REFERENCES languages (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE esl_sentences
  OWNER TO dkachaev;


-- Table: esl_hits_data

DROP TABLE esl_hits_data;

CREATE TABLE esl_hits_data
(
  id serial NOT NULL,
  hit_id integer,
  esl_sentence_id integer,
  output character varying,
  data_quality real,
  language_id integer,
  sentence_num integer,
  CONSTRAINT esl_hits_data_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE esl_hits_data
  OWNER TO dkachaev;


-- View: esl_hits

-- DROP VIEW esl_hits;

CREATE OR REPLACE VIEW esl_hits AS 
 SELECT h.id, h.mturk_hit_id, h.uuid, h.hittype_id, h.language_id, h.assignments, h.rejected, h.approved, ht.mturk_hittype_id, h.status
   FROM hits h, hittypes ht
  WHERE h.hittype_id = ht.id AND ht.typename::text = 'esl'::text;

ALTER TABLE esl_hits
  OWNER TO dkachaev;

CREATE TABLE esl_hits_results
(
  id serial NOT NULL,
  assignment_id integer,
  esl_sentence_id integer,
  CONSTRAINT esl_hit_results_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE esl_hits_results
  OWNER TO dkachaev;

CREATE TABLE esl_edits
(
  id serial NOT NULL,
  assignment_id integer,
  edit_num integer,
  esl_sentence_id integer,
  span_start integer,
  span_end integer,
  old_word text,
  new_word text,
  edit_type text,
  annotation text,
  CONSTRAINT esl_hit_results_id_pk PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE esl_edits
  OWNER TO dkachaev;

--
-- Name: location; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE esl_location (
    id integer NOT NULL,
    assignment_id integer,
    worker_id integer,
    ip character varying,
    city character varying,
    region character varying,
    country character varying,
    zipcode character varying,
    lat character varying,
    lng character varying,
    "timestamp" timestamp without time zone
);

--
-- Name: add_assignment(text, integer, text, text, text, varying, varying, varying, text, text); Type: FUNCTION; Schema: public; Owner: -
--

--CREATE FUNCTION add_assignment(mturk_assignment_id2 text, hit_id2 integer, mturk_worker_id2 text, accept_time2 text, submit_time2 text, autoapproval_time2 varying, approval_time2 varying, rejection_time2 varying, result2 text, mturk_status2 text) RETURNS integer
CREATE FUNCTION add_esl_assignment(mturk_assignment_id2 text, hit_id2 integer, mturk_worker_id2 text, accept_time2 text, submit_time2 text, result2 text, mturk_status2 text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
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
--		autoapproval_time=autoapproval_time2,
--		approval_time=approval_time2,
--		reject_time=reject_time2,
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
            INSERT INTO assignments (mturk_assignment_id, hit_id, worker_id, accept_time, submit_time, result, mturk_status)
            VALUES (mturk_assignment_id2, hit_id2, worker_id2, accept_time2, submit_time2, result2, mturk_status2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_location(integer, integer, text, text, text, text, text, text, text, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_esl_location(assignment_id2 integer, worker_id2 integer, ip2 text, city2 text, region2 text, country2 text, zipcode2 text, lat2 text, lng2 text, timestamp2 timestamp without time zone) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE esl_location
        SET
                ip=ip2,
                city=city2,
                region=region2,
                country=country2,
                zipcode=zipcode2,
                lat=lat2,
                lng=lng2,
                "timestamp"=timestamp2
        WHERE assignment_id=assignment_id2;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO esl_location (assignment_id, worker_id, ip, city, region, country, zipcode, lat, lng, "timestamp")
            VALUES (assignment_id2, worker_id2, ip2, city2, region2, country2, zipcode2, lat2, lng2, timestamp2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
  -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;

--
-- Name: add_syn_hit_data(text, text, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_esl_hits_data(hit_id2 integer, esl_sentence_id2 integer, mturk_hit_id2 integer, language_id2 integer ) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        --UPDATE esl_hits_data
        ---IF found THEN
        --    RETURN;
        ---END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO esl_hits_data (hit_id, esl_sentence_id, mturk_hit_id, language_id)
            VALUES (hit_id2, esl_sentence_id2, mturk_hit_id2, language_id2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;

--
-- Name: add_syn_hits_result(integer, integer, text, text, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_esl_hits_result(assignment_id2 integer, esl_sentence_id2 integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        --UPDATE esl_hits_results
        ---IF found THEN
          ---  RETURN;
        ---END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO esl_hits_results (assignment_id, esl_sentence_id)
            VALUES (assignment_id2, esl_sentence_id2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;

--
-- Name: add_esl_edit(integer, integer, integer, integer, integer, text, text, text, text); Type: FUNCTION; Schema: public; Owner: -
--
CREATE FUNCTION add_esl_edit(assignment_id2 integer, edit_num2 integer, esl_sentence_id2 integer, span_start2 integer, span_end2 integer, old_word2 text, new_word2 text, edit_type2 text, annotation2 text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        --UPDATE esl_edits
       --- IF found THEN
         ---   RETURN;
      ---  END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO esl_edits (assignment_id, edit_num, esl_sentence_id, span_start, span_end, old_word, new_word, edit_type, annotation)
            VALUES (assignment_id2, edit_num2, esl_sentence_id2, span_start2, span_end2, old_word2, new_word2, edit_type2, annotation2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;

--
-- Name: add_worker(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_esl_worker(mturk_worker_id2 text, name2 text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
        newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE esl_workers
        SET
                mturk_worker_id=mturk_worker_id2,
                "name"=name2
        WHERE mturk_worker_id=mturk_worker_id2;
       --- IF found THEN
       ---     RETURN (SELECT id FROM esl_workers WHERE mturk_worker_id=mturk_worker_id2);
        ---END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO esl_workers (mturk_worker_id, "name") VALUES (mturk_worker_id2, name2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


