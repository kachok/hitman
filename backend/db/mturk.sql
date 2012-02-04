--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.vocabulary DROP CONSTRAINT vocabulary_language_id_fk;
ALTER TABLE ONLY public.synonyms DROP CONSTRAINT synonyms_language_id_fk;
ALTER TABLE ONLY public.dictionary DROP CONSTRAINT dictionary_language_id_fk;
ALTER TABLE ONLY public.workers DROP CONSTRAINT workers_id_pk;
ALTER TABLE ONLY public.vocabulary DROP CONSTRAINT vocabulary_id_pk;
ALTER TABLE ONLY public.voc_hits_data DROP CONSTRAINT voc_hits_data_id_pk;
ALTER TABLE ONLY public.voc_hits_results DROP CONSTRAINT voc_hit_results_id_pk;
ALTER TABLE ONLY public.synonyms DROP CONSTRAINT synonyms_id_pk;
ALTER TABLE ONLY public.syn_hits_data DROP CONSTRAINT syn_hits_data_id_pk;
ALTER TABLE ONLY public.syn_hits_results DROP CONSTRAINT syn_hit_results_id_pk;
ALTER TABLE ONLY public.location DROP CONSTRAINT locations_pk_id;
ALTER TABLE ONLY public.languages DROP CONSTRAINT languages_id_pk;
ALTER TABLE ONLY public.hittypes DROP CONSTRAINT hittypes_id_pk;
ALTER TABLE ONLY public.hits DROP CONSTRAINT hits_id_pk;
ALTER TABLE ONLY public.dictionary DROP CONSTRAINT dictionary_id_pk;
ALTER TABLE ONLY public.cookies DROP CONSTRAINT cookies_pk_id;
ALTER TABLE ONLY public.assignments DROP CONSTRAINT assignments_id_pk;
ALTER TABLE public.workers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabulary ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.voc_hits_results ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.voc_hits_data ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.synonyms ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.syn_hits_results ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.syn_hits_data ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.location ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.languages ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.hittypes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.hits ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dictionary ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.cookies ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.assignments ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.workers_id_seq;
DROP SEQUENCE public.vocabulary_id_seq;
DROP TABLE public.vocabulary;
DROP VIEW public.voc_workers_performance;
DROP VIEW public.voc_hits_workers_performance;
DROP SEQUENCE public.voc_hits_results_id_seq;
DROP TABLE public.voc_hits_results;
DROP VIEW public.voc_hits_open;
DROP SEQUENCE public.voc_hits_data_id_seq;
DROP TABLE public.voc_hits_data;
DROP VIEW public.voc_hits_completed;
DROP VIEW public.voc_hits_closed;
DROP VIEW public.voc_assignments_underreview;
DROP VIEW public.voc_assignments_submitted;
DROP VIEW public.voc_assignments_reviewed;
DROP VIEW public.voc_hits;
DROP SEQUENCE public.synonyms_id_seq;
DROP TABLE public.synonyms;
DROP VIEW public.syn_workers_performance;
DROP VIEW public.syn_hits_results_weighted_pairs;
DROP VIEW public.syn_hits_workers_performance;
DROP TABLE public.workers;
DROP SEQUENCE public.syn_hits_results_id_seq;
DROP VIEW public.syn_hits_open;
DROP SEQUENCE public.syn_hits_data_id_seq;
DROP TABLE public.syn_hits_data;
DROP VIEW public.syn_hits_completed;
DROP VIEW public.syn_hits_closed;
DROP VIEW public.syn_hits_assignments_pending;
DROP VIEW public.syn_assignments_underreview;
DROP VIEW public.syn_assignments_submitted;
DROP VIEW public.syn_assignments_reviewed;
DROP VIEW public.syn_hits;
DROP VIEW public.syn_assignments_graded;
DROP TABLE public.syn_hits_results;
DROP SEQUENCE public.location_id_seq;
DROP TABLE public.location;
DROP SEQUENCE public.languages_id_seq;
DROP TABLE public.languages;
DROP SEQUENCE public.hittypes_id_seq;
DROP TABLE public.hittypes;
DROP SEQUENCE public.hits_id_seq;
DROP TABLE public.hits;
DROP SEQUENCE public.dictionary_id_seq;
DROP TABLE public.dictionary;
DROP SEQUENCE public.cookies_id_seq;
DROP TABLE public.cookies;
DROP SEQUENCE public.assignments_id_seq;
DROP TABLE public.assignments;
DROP FUNCTION public.grade_syn_hits_results();
DROP FUNCTION public.grade_syn_assignment(assignment_id2 integer);
DROP FUNCTION public.close_assignment(id2 integer);
DROP FUNCTION public.add_worker(mturk_worker_id2 text, name2 text);
DROP FUNCTION public.add_voc_hits_result(assignment_id2 integer, word_id2 integer, translation2 text, reason2 text, is_control2 integer);
DROP FUNCTION public.add_syn_hits_result(assignment_id2 integer, pair_id2 integer, are_synonyms2 text, misspelled2 text, is_control2 integer);
DROP FUNCTION public.add_syn_hit_data(synonym2 text, translation2 text, is_control2 integer, language_id2 integer);
DROP FUNCTION public.add_location(assignment_id2 integer, worker_id2 integer, ip2 text, city2 text, region2 text, country2 text, zipcode2 text, lat2 text, lng2 text, timestamp2 timestamp without time zone);
DROP FUNCTION public.add_language(name2 text, prefix2 text);
DROP FUNCTION public.add_hittype(name2 text, mturk_hittype_id2 text, language_id2 integer, typename2 text);
DROP FUNCTION public.add_hit(mturk_hit_id2 text, uuid2 text, hittype_id2 integer, language_id2 integer, assignments2 integer, rejected2 integer, approved2 integer);
DROP FUNCTION public.add_assignment(mturk_assignment_id2 text, hit_id2 integer, mturk_worker_id2 text, status2 text, submit_time2 text, result2 text, mturk_status2 text);
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: add_assignment(text, integer, text, text, text, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_assignment(mturk_assignment_id2 text, hit_id2 integer, mturk_worker_id2 text, status2 text, submit_time2 text, result2 text, mturk_status2 text) RETURNS integer
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
		submit_time=submit_time2,
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
	    INSERT INTO assignments (mturk_assignment_id, hit_id, worker_id, status, submit_time, result, mturk_status) 
	    VALUES (mturk_assignment_id2, hit_id2, worker_id2, status2, submit_time2, result2, mturk_status2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_hit(text, text, integer, integer, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_hit(mturk_hit_id2 text, uuid2 text, hittype_id2 integer, language_id2 integer, assignments2 integer, rejected2 integer, approved2 integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE hits 
        SET 
		mturk_hit_id=mturk_hit_id2, 
		uuid=uuid2,
		hittype_id=hittype_id2, 
		language_id=language_id2,
		assignments=assignments2,
		approved=approved2,
		rejected=rejected2
		
        WHERE uuid=uuid2;
        IF found THEN
            RETURN (SELECT id FROM hits WHERE uuid=uuid2);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO hits (mturk_hit_id, uuid, hittype_id, language_id, assignments, rejected, approved) 
	    VALUES (mturk_hit_id2, uuid2, hittype_id2, language_id2, assignments2, rejected2, approved2) 
	    RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_hittype(text, text, integer, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_hittype(name2 text, mturk_hittype_id2 text, language_id2 integer, typename2 text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE hittypes 
        SET 
		name = name2,
		mturk_hittype_id=mturk_hittype_id2,
		language_id=language_id2,
		typename=typename2
        WHERE mturk_hittype_id = mturk_hittype_id2;
	IF found THEN
            RETURN (SELECT id FROM hittypes WHERE mturk_hittype_id=mturk_hittype_id2);
        END IF;        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO hittypes (name, mturk_hittype_id, language_id, typename) 
            VALUES (name2, mturk_hittype_id2, language_id2, typename2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_language(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_language(name2 text, prefix2 text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE languages 
        SET 
		name=name2,
		prefix = prefix2
        WHERE prefix = prefix2;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO languages (name, prefix) VALUES (name2, prefix2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_location(integer, integer, text, text, text, text, text, text, text, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_location(assignment_id2 integer, worker_id2 integer, ip2 text, city2 text, region2 text, country2 text, zipcode2 text, lat2 text, lng2 text, timestamp2 timestamp without time zone) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE location 
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
	    INSERT INTO location (assignment_id, worker_id, ip, city, region, country, zipcode, lat, lng, "timestamp") 
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

CREATE FUNCTION add_syn_hit_data(synonym2 text, translation2 text, is_control2 integer, language_id2 integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE syn_hits_data
        SET 
		is_control=is_control2
        WHERE synonym=synonym2 AND translation=translation2;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO syn_hits_data (synonym, translation, is_control, language_id) 
	    VALUES (synonym2, translation2, is_control2, language_id2);
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

CREATE FUNCTION add_syn_hits_result(assignment_id2 integer, pair_id2 integer, are_synonyms2 text, misspelled2 text, is_control2 integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE syn_hits_results 
        SET 
		are_synonyms=are_synonyms2,
		misspelled=misspelled2
        WHERE assignment_id=assignment_id2 AND pair_id=pair_id2 and is_control=is_control2;
        IF found THEN
            RETURN (SELECT id FROM syn_hits_results WHERE assignment_id=assignment_id2 AND pair_id=pair_id2 and is_control=is_control2);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO syn_hits_results (assignment_id, pair_id, are_synonyms, misspelled, is_control) 
	    VALUES (assignment_id2, pair_id2, are_synonyms2, misspelled2, is_control2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_voc_hits_result(integer, integer, text, text, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_voc_hits_result(assignment_id2 integer, word_id2 integer, translation2 text, reason2 text, is_control2 integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE voc_hits_results 
        SET 
		word_id=word_id2
        WHERE assignment_id=assignment_id2 AND word_id=word_id2;
        IF found THEN
            RETURN (SELECT id FROM voc_hits_results WHERE assignment_id=assignment_id2 AND word_id=word_id2);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO voc_hits_results (assignment_id, word_id, translation, reason, is_control) 
	    VALUES (assignment_id2, word_id2, translation2, reason2, is_control2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_worker(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_worker(mturk_worker_id2 text, name2 text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE workers 
        SET 
		mturk_worker_id=mturk_worker_id2, 
		"name"=name2
        WHERE mturk_worker_id=mturk_worker_id2;
        IF found THEN
            RETURN (SELECT id FROM workers WHERE mturk_worker_id=mturk_worker_id2);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO workers (mturk_worker_id, "name") VALUES (mturk_worker_id2, name2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: close_assignment(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION close_assignment(id2 integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
	hit_id2 integer;
	mturk_status2 character varying;
BEGIN
	UPDATE assignments
	SET status='Reviewed'
	WHERE id=id2;


	-- get values for HIT_id and if assignment was approved/rejected
	SELECT INTO hit_id2, mturk_status2 h.id, a.mturk_status FROM hits h, assignments a
	WHERE h.id=a.hit_id and a.id=id2;

	IF mturk_status2='approved' THEN
		UPDATE hits
		SET approved=approved+1
		WHERE id=hit_id2;
	ELSE	
		UPDATE hits
		SET rejected=rejected+1
		WHERE id=hit_id2;
	END IF;
END;
$$;


--
-- Name: grade_syn_assignment(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION grade_syn_assignment(assignment_id2 integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
	total2 integer;
	quality2 real;
	data_status2 real;
BEGIN

SELECT INTO total2, quality2 p.total, p.quality from syn_hits_workers_performance p, assignments a
WHERE a.id=assignment_id2 and a.worker_id=p.id;


-- get data_status value for assignment in hand
select INTO data_status2 sag.grade/2
from syn_assignments_graded sag
where sag.id=assignment_id2;

IF total2<10 THEN
	-- first 10 assignments auto-approved
	UPDATE assignments
	SET mturk_status='approved'
	WHERE id=assignment_id2;
ELSE

	IF quality2>=0.75 THEN
		-- approve as 75% + high-quality worker
		UPDATE assignments
		SET mturk_status='approved'
		WHERE id=assignment_id2;
	ELSIF quality2<0.5 THEN 
		-- reject as 50% - low-quality worker
		UPDATE assignments
		SET mturk_status='rejected'
		WHERE id=assignment_id2;
	ELSE
		-- approve/reject based on data quality
		IF data_status2>=0.5 THEN
			UPDATE assignments
			SET mturk_status='approved'
			WHERE id=assignment_id2;
		ELSIF data_status2<0.5 THEN
			UPDATE assignments
			SET mturk_status='rejected'
			WHERE id=assignment_id2;	
		END IF;	
	END IF;

END IF;


-- update data quality based on graded results
update assignments a
set data_status=sag.grade/2
from syn_assignments_graded sag
where sag.id=a.id and a.id=assignment_id2;


END;
$$;


--
-- Name: grade_syn_hits_results(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION grade_syn_hits_results() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
 update syn_hits_results r
 set quality=g.grade/2
 from syn_assignments_graded g
 where r.assignment_id=g.id;
END;
$$;


SET default_with_oids = false;

--
-- Name: assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE assignments (
    id integer NOT NULL,
    mturk_assignment_id character varying,
    hit_id integer,
    worker_id integer,
    status character varying,
    submit_time character varying,
    result character varying,
    data_status real,
    mturk_status character varying
);


--
-- Name: assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE assignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE assignments_id_seq OWNED BY assignments.id;


--
-- Name: cookies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE cookies (
    id integer NOT NULL,
    uuid character varying,
    worker_id integer,
    status character varying,
    "timestamp" timestamp without time zone
);


--
-- Name: cookies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE cookies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cookies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE cookies_id_seq OWNED BY cookies.id;


--
-- Name: dictionary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dictionary (
    id integer NOT NULL,
    word character varying,
    sentences character varying,
    language_id integer,
    translation character varying
);


--
-- Name: dictionary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dictionary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dictionary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE dictionary_id_seq OWNED BY dictionary.id;


--
-- Name: hits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE hits (
    id integer NOT NULL,
    mturk_hit_id character varying,
    uuid character varying,
    hittype_id integer,
    language_id integer,
    assignments integer DEFAULT 0,
    rejected integer DEFAULT 0,
    approved integer DEFAULT 0,
    status character varying DEFAULT 'Open'::character varying
);


--
-- Name: hits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE hits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE hits_id_seq OWNED BY hits.id;


--
-- Name: hittypes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE hittypes (
    id integer NOT NULL,
    name character varying,
    mturk_hittype_id character varying,
    language_id integer,
    typename character varying
);


--
-- Name: hittypes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE hittypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hittypes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE hittypes_id_seq OWNED BY hittypes.id;


--
-- Name: languages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE languages (
    id integer NOT NULL,
    name character varying,
    prefix character varying
);


--
-- Name: languages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE languages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: languages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE languages_id_seq OWNED BY languages.id;


--
-- Name: location; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE location (
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
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE location_id_seq OWNED BY location.id;


--
-- Name: syn_hits_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE syn_hits_results (
    id integer NOT NULL,
    assignment_id integer,
    pair_id integer,
    are_synonyms character varying,
    misspelled character varying,
    is_control integer,
    quality real
);


--
-- Name: syn_assignments_graded; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_assignments_graded AS
    SELECT a.id, sum(ga.grade) AS grade FROM assignments a, (SELECT syn_hits_results.id, syn_hits_results.assignment_id, syn_hits_results.pair_id, syn_hits_results.are_synonyms, syn_hits_results.misspelled, syn_hits_results.is_control, syn_hits_results.quality, CASE WHEN ((syn_hits_results.are_synonyms)::text = 'yes'::text) THEN (1)::numeric WHEN ((syn_hits_results.are_synonyms)::text = 'no'::text) THEN (0)::numeric ELSE 0.5 END AS grade FROM syn_hits_results WHERE (syn_hits_results.is_control = 1)) ga WHERE (a.id = ga.assignment_id) GROUP BY a.id;


--
-- Name: syn_hits; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits AS
    SELECT h.id, h.mturk_hit_id, h.uuid, h.hittype_id, h.language_id, h.assignments, h.rejected, h.approved, ht.mturk_hittype_id, h.status FROM hits h, hittypes ht WHERE ((h.hittype_id = ht.id) AND ((ht.typename)::text = 'synonyms'::text));


--
-- Name: syn_assignments_reviewed; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_assignments_reviewed AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, syn_hits sh WHERE ((a.hit_id = sh.id) AND ((a.status)::text = 'Reviewed'::text));


--
-- Name: syn_assignments_submitted; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_assignments_submitted AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, syn_hits sh WHERE ((a.hit_id = sh.id) AND ((a.status)::text = 'Submitted'::text));


--
-- Name: syn_assignments_underreview; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_assignments_underreview AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, syn_hits sh WHERE ((a.hit_id = sh.id) AND ((a.status)::text = 'Under Review'::text));


--
-- Name: syn_hits_assignments_pending; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits_assignments_pending AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, syn_assignments_graded ag WHERE ((a.id = ag.id) AND ((a.status)::text = 'Submitted'::text));


--
-- Name: syn_hits_closed; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits_closed AS
    SELECT syn_hits.id, syn_hits.mturk_hit_id, syn_hits.uuid, syn_hits.hittype_id, syn_hits.language_id, syn_hits.assignments, syn_hits.rejected, syn_hits.approved, syn_hits.mturk_hittype_id, syn_hits.status FROM syn_hits WHERE ((syn_hits.status)::text = 'Closed'::text);


--
-- Name: syn_hits_completed; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits_completed AS
    SELECT syn_hits.id, syn_hits.mturk_hit_id, syn_hits.uuid, syn_hits.hittype_id, syn_hits.language_id, syn_hits.assignments, syn_hits.rejected, syn_hits.approved, syn_hits.mturk_hittype_id, syn_hits.status FROM syn_hits WHERE ((syn_hits.status)::text = 'Completed'::text);


--
-- Name: syn_hits_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE syn_hits_data (
    id integer NOT NULL,
    hit_id integer,
    word_id integer,
    type character varying,
    translation character varying,
    synonym character varying,
    voc_assignment_id integer,
    is_control integer,
    output character varying,
    data_quality real,
    language_id integer
);


--
-- Name: syn_hits_data_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE syn_hits_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syn_hits_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE syn_hits_data_id_seq OWNED BY syn_hits_data.id;


--
-- Name: syn_hits_open; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits_open AS
    SELECT syn_hits.id, syn_hits.mturk_hit_id, syn_hits.uuid, syn_hits.hittype_id, syn_hits.language_id, syn_hits.assignments, syn_hits.rejected, syn_hits.approved, syn_hits.mturk_hittype_id, syn_hits.status FROM syn_hits WHERE ((syn_hits.status)::text = 'Open'::text);


--
-- Name: syn_hits_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE syn_hits_results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syn_hits_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE syn_hits_results_id_seq OWNED BY syn_hits_results.id;


--
-- Name: workers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE workers (
    id integer NOT NULL,
    mturk_worker_id character varying,
    name character varying,
    description character varying,
    banned character varying,
    performance character varying
);


--
-- Name: syn_hits_workers_performance; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits_workers_performance AS
    SELECT w.id, avg(a.data_status) AS quality, count(a.data_status) AS total FROM workers w, assignments a, hits h, hittypes ht WHERE (((((a.worker_id = w.id) AND (a.status IS NOT NULL)) AND (a.hit_id = h.id)) AND (h.hittype_id = ht.id)) AND ((ht.typename)::text = 'synonyms'::text)) GROUP BY w.id;


--
-- Name: syn_hits_results_weighted_pairs; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_hits_results_weighted_pairs AS
    SELECT rr.voc_assignment_id, rr.pair_id, rr.are_synonyms, max(rr.weight) AS max FROM (SELECT r.voc_assignment_id, r.pair_id, r.are_synonyms, avg(r.worker_performance) AS weight FROM (SELECT shd.voc_assignment_id, a.hit_id, a.id AS assignment_id, shr.quality, shr.pair_id, shwp.quality AS worker_performance, shr.are_synonyms FROM assignments a, syn_hits_completed shc, syn_hits_results shr, syn_hits_data shd, syn_hits_workers_performance shwp WHERE (((((((shd.hit_id = a.hit_id) AND (shd.id = shr.pair_id)) AND (a.hit_id = shc.id)) AND (shr.assignment_id = a.id)) AND (shr.is_control = 0)) AND (a.worker_id = shwp.id)) AND (a.data_status > (0.5)::double precision))) r GROUP BY r.voc_assignment_id, r.pair_id, r.are_synonyms) rr GROUP BY rr.voc_assignment_id, rr.pair_id, rr.are_synonyms;


--
-- Name: syn_workers_performance; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW syn_workers_performance AS
    SELECT w.id AS worker_id, avg(a.data_status) AS quality, count(a.data_status) AS total FROM workers w, assignments a, hits h, hittypes ht WHERE (((((a.worker_id = w.id) AND (a.status IS NOT NULL)) AND (a.hit_id = h.id)) AND (h.hittype_id = ht.id)) AND ((ht.typename)::text = 'synonyms'::text)) GROUP BY w.id;


--
-- Name: synonyms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonyms (
    id integer NOT NULL,
    word character varying,
    synonym character varying,
    language_id integer
);


--
-- Name: synonyms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE synonyms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: synonyms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE synonyms_id_seq OWNED BY synonyms.id;


--
-- Name: voc_hits; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_hits AS
    SELECT h.id, h.mturk_hit_id, h.uuid, h.hittype_id, h.language_id, h.assignments, h.rejected, h.approved, ht.mturk_hittype_id, h.status FROM hits h, hittypes ht WHERE ((h.hittype_id = ht.id) AND ((ht.typename)::text = 'vocabulary'::text));


--
-- Name: voc_assignments_reviewed; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_assignments_reviewed AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, voc_hits vh WHERE ((a.hit_id = vh.id) AND ((a.status)::text = 'Reviewed'::text));


--
-- Name: voc_assignments_submitted; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_assignments_submitted AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, voc_hits vh WHERE ((a.hit_id = vh.id) AND ((a.status)::text = 'Submitted'::text));


--
-- Name: voc_assignments_underreview; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_assignments_underreview AS
    SELECT a.id, a.mturk_assignment_id, a.hit_id, a.worker_id, a.status, a.submit_time, a.result, a.data_status, a.mturk_status FROM assignments a, voc_hits vh WHERE ((a.hit_id = vh.id) AND ((a.status)::text = 'Under Review'::text));


--
-- Name: voc_hits_closed; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_hits_closed AS
    SELECT voc_hits.id, voc_hits.mturk_hit_id, voc_hits.uuid, voc_hits.hittype_id, voc_hits.language_id, voc_hits.assignments, voc_hits.rejected, voc_hits.approved, voc_hits.mturk_hittype_id, voc_hits.status FROM voc_hits WHERE ((voc_hits.status)::text = 'Closed'::text);


--
-- Name: voc_hits_completed; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_hits_completed AS
    SELECT voc_hits.id, voc_hits.mturk_hit_id, voc_hits.uuid, voc_hits.hittype_id, voc_hits.language_id, voc_hits.assignments, voc_hits.rejected, voc_hits.approved, voc_hits.mturk_hittype_id, voc_hits.status FROM voc_hits WHERE ((voc_hits.status)::text = 'Completed'::text);


--
-- Name: voc_hits_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE voc_hits_data (
    id integer NOT NULL,
    hit_id integer,
    word_id integer,
    output character varying,
    data_quality real,
    language_id integer
);


--
-- Name: voc_hits_data_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE voc_hits_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: voc_hits_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE voc_hits_data_id_seq OWNED BY voc_hits_data.id;


--
-- Name: voc_hits_open; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_hits_open AS
    SELECT voc_hits.id, voc_hits.mturk_hit_id, voc_hits.uuid, voc_hits.hittype_id, voc_hits.language_id, voc_hits.assignments, voc_hits.rejected, voc_hits.approved, voc_hits.mturk_hittype_id, voc_hits.status FROM voc_hits WHERE ((voc_hits.status)::text = 'Open'::text);


--
-- Name: voc_hits_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE voc_hits_results (
    id integer NOT NULL,
    assignment_id integer,
    word_id integer,
    translation character varying,
    reason character varying,
    is_control integer,
    quality real
);


--
-- Name: voc_hits_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE voc_hits_results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: voc_hits_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE voc_hits_results_id_seq OWNED BY voc_hits_results.id;


--
-- Name: voc_hits_workers_performance; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_hits_workers_performance AS
    SELECT w.id, ht.language_id, avg(a.data_status) AS quality, count(a.data_status) AS total FROM workers w, assignments a, hits h, hittypes ht WHERE (((((a.worker_id = w.id) AND (a.status IS NOT NULL)) AND (a.hit_id = h.id)) AND (h.hittype_id = ht.id)) AND ((ht.typename)::text = 'vocabulary'::text)) GROUP BY w.id, ht.language_id;


--
-- Name: voc_workers_performance; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW voc_workers_performance AS
    SELECT w.id AS worker_id, ht.language_id, avg(a.data_status) AS quality, count(a.data_status) AS total FROM workers w, assignments a, hits h, hittypes ht WHERE (((((a.worker_id = w.id) AND (a.status IS NOT NULL)) AND (a.hit_id = h.id)) AND (h.hittype_id = ht.id)) AND ((ht.typename)::text = 'vocabulary'::text)) GROUP BY w.id, ht.language_id;


--
-- Name: vocabulary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vocabulary (
    id integer NOT NULL,
    word character varying,
    sentences text,
    language_id integer
);


--
-- Name: vocabulary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabulary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vocabulary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabulary_id_seq OWNED BY vocabulary.id;


--
-- Name: workers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE workers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: workers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE workers_id_seq OWNED BY workers.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE assignments ALTER COLUMN id SET DEFAULT nextval('assignments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE cookies ALTER COLUMN id SET DEFAULT nextval('cookies_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE dictionary ALTER COLUMN id SET DEFAULT nextval('dictionary_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE hits ALTER COLUMN id SET DEFAULT nextval('hits_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE hittypes ALTER COLUMN id SET DEFAULT nextval('hittypes_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE languages ALTER COLUMN id SET DEFAULT nextval('languages_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE location ALTER COLUMN id SET DEFAULT nextval('location_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE syn_hits_data ALTER COLUMN id SET DEFAULT nextval('syn_hits_data_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE syn_hits_results ALTER COLUMN id SET DEFAULT nextval('syn_hits_results_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE synonyms ALTER COLUMN id SET DEFAULT nextval('synonyms_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE voc_hits_data ALTER COLUMN id SET DEFAULT nextval('voc_hits_data_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE voc_hits_results ALTER COLUMN id SET DEFAULT nextval('voc_hits_results_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabulary ALTER COLUMN id SET DEFAULT nextval('vocabulary_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE workers ALTER COLUMN id SET DEFAULT nextval('workers_id_seq'::regclass);


--
-- Name: assignments_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY assignments
    ADD CONSTRAINT assignments_id_pk PRIMARY KEY (id);


--
-- Name: cookies_pk_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cookies
    ADD CONSTRAINT cookies_pk_id PRIMARY KEY (id);


--
-- Name: dictionary_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_id_pk PRIMARY KEY (id);


--
-- Name: hits_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY hits
    ADD CONSTRAINT hits_id_pk PRIMARY KEY (id);


--
-- Name: hittypes_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY hittypes
    ADD CONSTRAINT hittypes_id_pk PRIMARY KEY (id);


--
-- Name: languages_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY languages
    ADD CONSTRAINT languages_id_pk PRIMARY KEY (id);


--
-- Name: locations_pk_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY location
    ADD CONSTRAINT locations_pk_id PRIMARY KEY (id);


--
-- Name: syn_hit_results_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY syn_hits_results
    ADD CONSTRAINT syn_hit_results_id_pk PRIMARY KEY (id);


--
-- Name: syn_hits_data_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY syn_hits_data
    ADD CONSTRAINT syn_hits_data_id_pk PRIMARY KEY (id);


--
-- Name: synonyms_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY synonyms
    ADD CONSTRAINT synonyms_id_pk PRIMARY KEY (id);


--
-- Name: voc_hit_results_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY voc_hits_results
    ADD CONSTRAINT voc_hit_results_id_pk PRIMARY KEY (id);


--
-- Name: voc_hits_data_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY voc_hits_data
    ADD CONSTRAINT voc_hits_data_id_pk PRIMARY KEY (id);


--
-- Name: vocabulary_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_id_pk PRIMARY KEY (id);


--
-- Name: workers_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY workers
    ADD CONSTRAINT workers_id_pk PRIMARY KEY (id);


--
-- Name: dictionary_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


--
-- Name: synonyms_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY synonyms
    ADD CONSTRAINT synonyms_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


--
-- Name: vocabulary_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


--
-- PostgreSQL database dump complete
--

