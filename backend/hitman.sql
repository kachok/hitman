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
ALTER TABLE ONLY public.dictionary DROP CONSTRAINT dictionary_language_id_fk;
ALTER TABLE ONLY public.vocabularyhitsdata DROP CONSTRAINT vocabularyhitsdata_id_pk;
ALTER TABLE ONLY public.vocabularyhits DROP CONSTRAINT vocabularyhits_id_pk;
ALTER TABLE ONLY public.vocabulary DROP CONSTRAINT vocabulary_id_pk;
ALTER TABLE ONLY public.synonymshitsdata DROP CONSTRAINT synonymshitsdata_id_pk;
ALTER TABLE ONLY public.synonymshits DROP CONSTRAINT synonymshits_id_pk;
ALTER TABLE ONLY public.languages DROP CONSTRAINT languages_id_pk;
ALTER TABLE ONLY public.hittypes DROP CONSTRAINT hittypes_id_pk;
ALTER TABLE ONLY public.dictionary DROP CONSTRAINT dictionary_id_pk;
ALTER TABLE public.workers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabularyhitsdata ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabularyhits ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabularyhitresults ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabulary ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.synonymshitresults ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.synonymshitassignments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.languages ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.hittypes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dictionary ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.workers_id_seq;
DROP TABLE public.workers;
DROP SEQUENCE public.vocabularyhitsdata_id_seq;
DROP TABLE public.vocabularyhitsdata;
DROP SEQUENCE public.vocabularyhits_id_seq;
DROP TABLE public.vocabularyhits;
DROP SEQUENCE public.vocabularyhitresults_id_seq;
DROP TABLE public.vocabularyhitresults;
DROP SEQUENCE public.vocabulary_id_seq;
DROP TABLE public.vocabulary;
DROP TABLE public.synonymshitsdata;
DROP SEQUENCE public.synonymshitsdata_id_seq;
DROP TABLE public.synonymshits;
DROP SEQUENCE public.synonymshits_id_seq;
DROP SEQUENCE public.synonymshitresults_id_seq;
DROP SEQUENCE public.synonymshitassignments_id_seq;
DROP TABLE public.synonyms_raw;
DROP VIEW public.passed_synonymsassignments;
DROP VIEW public.mturk_update_pending_synonymassignments;
DROP TABLE public.synonymshitassignments;
DROP TABLE public.location;
DROP SEQUENCE public.languages_id_seq;
DROP TABLE public.languages;
DROP SEQUENCE public.hittypes_id_seq;
DROP TABLE public.hittypes;
DROP TABLE public.foreignenglishspeakersurvey;
DROP VIEW public.failed_synonymsassignments;
DROP TABLE public.synonymshitresults;
DROP TABLE public.englishspeakersurvey;
DROP SEQUENCE public.dictionary_id_seq;
DROP TABLE public.dictionary;
DROP FUNCTION public.update_synonymassignment(id2 integer);
DROP FUNCTION public.review_synonymsassignments();
DROP FUNCTION public.add_worker(workerid text, workername text);
DROP FUNCTION public.add_vocabularyhitresult(hitid text, assignmentid text, workerid text, result text, submittime text, wordid integer, translation2 text, reason2 text, iscontrol integer);
DROP FUNCTION public.add_synonymshitresult(assignmentid integer, pairid integer, aresynonyms text, misspelled2 text, iscontrol integer, quality2 text, control2 text);
DROP FUNCTION public.add_synonymshitassignment(hitid text, assignmentid text, workerid text, status2 text, submittime text, result2 text, control2 text, quality2 text);
DROP FUNCTION public.add_location(workerid integer, ip2 text, city2 text, region2 text, country2 text, zipcode2 text, lat2 text, lng2 text, timestamp2 timestamp without time zone);
DROP FUNCTION public.add_language(langname text, langprefix text);
DROP FUNCTION public.add_hittype(hittypeid text, hittypename text, languageid integer, hittypelanguage text, hittypetype text);
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
-- Name: add_hittype(text, text, integer, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_hittype(hittypeid text, hittypename text, languageid integer, hittypelanguage text, hittypetype text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE hittypes 
        SET 
		mturk_hittype_id=hittypeid,
		name = hittypename,
		language_id=languageid,
		language=hittypelanguage,
		typename=hittypetype
        WHERE mturk_hittype_id = hittypeid;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO hittypes (mturk_hittype_id, name, language_id, language, typename) VALUES (hittypeid, hittypename, languageid, hittypelanguage, hittypetype);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_language(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_language(langname text, langprefix text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    LOOP
        -- first try to update the key
        UPDATE languages 
        SET 
		name=langname,
		prefix = langprefix
        WHERE prefix = langprefix;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
            INSERT INTO languages (name, prefix) VALUES (langname, langprefix);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_location(integer, text, text, text, text, text, text, text, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_location(workerid integer, ip2 text, city2 text, region2 text, country2 text, zipcode2 text, lat2 text, lng2 text, timestamp2 timestamp without time zone) RETURNS void
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
        WHERE worker_id=workerid;
        IF found THEN
            RETURN;
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO location (worker_id, ip, city, region, country, zipcode, lat, lng, "timestamp") 
	    VALUES (workerid, ip2, city2, region2, country2, zipcode2, lat2, lng2, timestamp2);
            RETURN;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_synonymshitassignment(text, text, text, text, text, text, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_synonymshitassignment(hitid text, assignmentid text, workerid text, status2 text, submittime text, result2 text, control2 text, quality2 text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE synonymshitassignments 
        SET 
		mturk_hit_id=hitid, 
		mturk_assignment_id=assignmentid, 
		mturk_worker_id=workerid, 
		result=result2, 
		submit_time=submittime,
		status=status2,
		control=control2,
		quality=quality2
        WHERE mturk_assignment_id=assignmentid;
        IF found THEN
            RETURN (SELECT id FROM synonymshitassignments WHERE mturk_assignment_id=assignmentid);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO synonymshitassignments (mturk_hit_id, mturk_assignment_id, mturk_worker_id, status, result, submit_time, quality, control) 
	    VALUES (hitid, assignmentid, workerid, status2, result2, submittime, quality2, control2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_synonymshitresult(integer, integer, text, text, integer, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_synonymshitresult(assignmentid integer, pairid integer, aresynonyms text, misspelled2 text, iscontrol integer, quality2 text, control2 text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE synonymshitresults 
        SET 
		are_synonyms=aresynonyms,
		misspelled=misspelled2,
		is_control=iscontrol,
		quality=quality2,
		control=control2
        WHERE assignment_id=assignmentid AND pair_id=pairid;
        IF found THEN
            RETURN (SELECT id FROM synonymshitresults WHERE assignment_id=assignmentid AND pair_id=pairid);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO synonymshitresults (assignment_id, pair_id, are_synonyms, misspelled, is_control, quality, control) 
	    VALUES (assignmentid, pairid, aresynonyms, misspelled2, iscontrol, quality2, control2) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: add_vocabularyhitresult(text, text, text, text, text, integer, text, text, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_vocabularyhitresult(hitid text, assignmentid text, workerid text, result text, submittime text, wordid integer, translation2 text, reason2 text, iscontrol integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE vocabularyhitresults 
        SET 
		mturk_hit_id=hitid, 
		mturk_assignment_id=assignmentid, 
		mturk_worker_id=workerid, 
		results=result, 
		submit_time=submittime
        WHERE mturk_assignment_id=assignmentid AND word_id=wordid;
        IF found THEN
            RETURN (SELECT id FROM vocabularyhitresults WHERE mturk_assignment_id=assignmentid AND word_id=wordid);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO vocabularyhitresults (mturk_hit_id, mturk_assignment_id, mturk_worker_id, results, submit_time, word_id, translation, reason, is_control) VALUES (hitid, assignmentid, workerid, result, submittime, wordid, translation2, reason2, iscontrol) RETURNING id into newid;
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

CREATE FUNCTION add_worker(workerid text, workername text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	newid INTEGER;
BEGIN
    LOOP
        -- first try to update the key
        UPDATE workers 
        SET 
		mturk_worker_id=workerid, 
		"name"=workername
        WHERE mturk_worker_id=workerid;
        IF found THEN
            RETURN (SELECT id FROM workers WHERE mturk_worker_id=workerid);
        END IF;
        -- not there, so try to insert the key
        -- if someone else inserts the same key concurrently,
        -- we could get a unique-key failure
        BEGIN
	    INSERT INTO workers (mturk_worker_id, "name") VALUES (workerid, workername) RETURNING id into newid;
            RETURN newid;
        EXCEPTION WHEN unique_violation THEN
            -- do nothing, and loop to try the UPDATE again
        END;
    END LOOP;
END;
$$;


--
-- Name: review_synonymsassignments(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION review_synonymsassignments() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
	UPDATE synonymshitassignments sa
	SET control='passed'
	WHERE
	EXISTS (select * from passed_synonymsassignments v where v.assignment_id=sa.id);
    
	UPDATE synonymshitassignments sa
	SET control='failed'
	WHERE
	EXISTS (select * from failed_synonymsassignments v where v.assignment_id=sa.id);
    
END;
$$;


--
-- Name: update_synonymassignment(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION update_synonymassignment(id2 integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
	UPDATE synonymshitassignments
	SET status='Reviewed'
	WHERE id=id2;
END;
$$;


SET default_with_oids = false;

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
-- Name: englishspeakersurvey; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE englishspeakersurvey (
    worker_id integer,
    "timestamp" time without time zone,
    native_english_speaker boolean,
    years_speaking_english character varying,
    country character varying,
    born_country character varying,
    language character varying,
    language_id integer
);


--
-- Name: synonymshitresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshitresults (
    id integer NOT NULL,
    control character varying,
    quality character varying,
    pair_id integer,
    are_synonyms character varying,
    misspelled character varying,
    is_control integer,
    assignment_id integer
);


--
-- Name: failed_synonymsassignments; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW failed_synonymsassignments AS
    SELECT synonymshitresults.assignment_id, count(synonymshitresults.assignment_id) AS count FROM synonymshitresults WHERE ((synonymshitresults.is_control = 1) AND ((synonymshitresults.are_synonyms)::text = 'no'::text)) GROUP BY synonymshitresults.assignment_id HAVING (count(synonymshitresults.assignment_id) = 2);


--
-- Name: foreignenglishspeakersurvey; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE foreignenglishspeakersurvey (
    worker_id integer,
    "timestamp" time without time zone,
    native_speaker boolean,
    years_speaking_foreign character varying,
    native_english_speaker boolean,
    years_speaking_english character varying,
    country character varying,
    born_country character varying,
    language character varying,
    language_id integer
);


--
-- Name: hittypes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE hittypes (
    id integer NOT NULL,
    name character varying,
    mturk_hittype_id character varying,
    language_id integer,
    language character varying,
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
-- Name: synonymshitassignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshitassignments (
    id integer NOT NULL,
    mturk_hit_id character varying,
    mturk_assignment_id character varying,
    mturk_worker_id character varying,
    status character varying,
    submit_time character varying,
    result character varying,
    control character varying,
    quality character varying
);


--
-- Name: mturk_update_pending_synonymassignments; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW mturk_update_pending_synonymassignments AS
    SELECT synonymshitassignments.id, synonymshitassignments.mturk_hit_id, synonymshitassignments.mturk_assignment_id, synonymshitassignments.mturk_worker_id, synonymshitassignments.status, synonymshitassignments.submit_time, synonymshitassignments.result, synonymshitassignments.control, synonymshitassignments.quality FROM synonymshitassignments WHERE (((synonymshitassignments.status)::text = 'Submitted'::text) AND ((synonymshitassignments.control)::text = ANY ((ARRAY['passed'::character varying, 'failed'::character varying])::text[])));


--
-- Name: passed_synonymsassignments; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW passed_synonymsassignments AS
    SELECT synonymshitresults.assignment_id, count(synonymshitresults.assignment_id) AS count FROM synonymshitresults WHERE ((synonymshitresults.is_control = 1) AND ((synonymshitresults.are_synonyms)::text <> 'no'::text)) GROUP BY synonymshitresults.assignment_id HAVING (count(synonymshitresults.assignment_id) > 0);


--
-- Name: synonyms_raw; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonyms_raw (
    id integer,
    mturk_assignment_id character varying,
    translation character varying,
    translation_raw character varying,
    word_id integer
);


--
-- Name: synonymshitassignments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE synonymshitassignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: synonymshitassignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE synonymshitassignments_id_seq OWNED BY synonymshitassignments.id;


--
-- Name: synonymshitresults_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE synonymshitresults_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: synonymshitresults_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE synonymshitresults_id_seq OWNED BY synonymshitresults.id;


--
-- Name: synonymshits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE synonymshits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: synonymshits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshits (
    id integer DEFAULT nextval('synonymshits_id_seq'::regclass) NOT NULL,
    mturk_hit_id character varying,
    uuid character varying,
    mturk_hittype_id character varying,
    hittype_id integer,
    hit_id integer,
    language_id integer,
    assignments integer DEFAULT 0
);


--
-- Name: synonymshitsdata_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE synonymshitsdata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: synonymshitsdata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshitsdata (
    id integer DEFAULT nextval('synonymshitsdata_id_seq'::regclass) NOT NULL,
    word_id integer,
    type character varying,
    mturk_hit_id character varying,
    hit_id integer,
    translation character varying,
    synonym character varying
);


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
-- Name: vocabularyhitresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vocabularyhitresults (
    id integer NOT NULL,
    mturk_hit_id character varying,
    mturk_assignment_id character varying,
    mturk_worker_id character varying,
    results character varying,
    control character varying,
    submit_time character varying,
    word_id integer,
    translation character varying,
    reason character varying,
    is_control integer,
    quality character varying
);


--
-- Name: vocabularyhitresults_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabularyhitresults_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vocabularyhitresults_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabularyhitresults_id_seq OWNED BY vocabularyhitresults.id;


--
-- Name: vocabularyhits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vocabularyhits (
    id integer NOT NULL,
    mturk_hit_id character varying,
    uuid character varying,
    mturk_hittype_id character varying,
    hittype_id integer,
    hit_id integer,
    language_id integer
);


--
-- Name: vocabularyhits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabularyhits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vocabularyhits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabularyhits_id_seq OWNED BY vocabularyhits.id;


--
-- Name: vocabularyhitsdata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vocabularyhitsdata (
    id integer NOT NULL,
    word_id integer,
    type character varying,
    mturk_hit_id character varying,
    hit_id integer
);


--
-- Name: vocabularyhitsdata_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabularyhitsdata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vocabularyhitsdata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabularyhitsdata_id_seq OWNED BY vocabularyhitsdata.id;


--
-- Name: workers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE workers (
    id integer NOT NULL,
    mturk_worker_id character varying,
    name character varying
);


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

ALTER TABLE dictionary ALTER COLUMN id SET DEFAULT nextval('dictionary_id_seq'::regclass);


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

ALTER TABLE synonymshitassignments ALTER COLUMN id SET DEFAULT nextval('synonymshitassignments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE synonymshitresults ALTER COLUMN id SET DEFAULT nextval('synonymshitresults_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabulary ALTER COLUMN id SET DEFAULT nextval('vocabulary_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabularyhitresults ALTER COLUMN id SET DEFAULT nextval('vocabularyhitresults_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabularyhits ALTER COLUMN id SET DEFAULT nextval('vocabularyhits_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabularyhitsdata ALTER COLUMN id SET DEFAULT nextval('vocabularyhitsdata_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE workers ALTER COLUMN id SET DEFAULT nextval('workers_id_seq'::regclass);


--
-- Name: dictionary_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_id_pk PRIMARY KEY (id);


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
-- Name: synonymshits_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY synonymshits
    ADD CONSTRAINT synonymshits_id_pk PRIMARY KEY (id);


--
-- Name: synonymshitsdata_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY synonymshitsdata
    ADD CONSTRAINT synonymshitsdata_id_pk PRIMARY KEY (id);


--
-- Name: vocabulary_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_id_pk PRIMARY KEY (id);


--
-- Name: vocabularyhits_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabularyhits
    ADD CONSTRAINT vocabularyhits_id_pk PRIMARY KEY (id);


--
-- Name: vocabularyhitsdata_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabularyhitsdata
    ADD CONSTRAINT vocabularyhitsdata_id_pk PRIMARY KEY (id);


--
-- Name: dictionary_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


--
-- Name: vocabulary_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


--
-- PostgreSQL database dump complete
--

