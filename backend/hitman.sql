--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.1
-- Dumped by pg_dump version 9.1.0
-- Started on 2012-01-10 11:29:27 EST

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
ALTER TABLE ONLY public.languages DROP CONSTRAINT languages_id_pk;
ALTER TABLE ONLY public.hittypes DROP CONSTRAINT hittypes_id_pk;
ALTER TABLE ONLY public.dictionary DROP CONSTRAINT dictionary_id_pk;
ALTER TABLE public.vocabularyhitsdata ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabularyhits ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.vocabulary ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.languages ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.hittypes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dictionary ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.vocabularyhitsdata_id_seq;
DROP TABLE public.vocabularyhitsdata;
DROP SEQUENCE public.vocabularyhits_id_seq;
DROP TABLE public.vocabularyhits;
DROP TABLE public.vocabularyhitresults;
DROP SEQUENCE public.vocabulary_id_seq;
DROP TABLE public.vocabulary;
DROP TABLE public.synonymshitsdata;
DROP TABLE public.synonymshits;
DROP TABLE public.synonymshitresults;
DROP TABLE public.synonyms_raw;
DROP SEQUENCE public.languages_id_seq;
DROP TABLE public.languages;
DROP SEQUENCE public.hittypes_id_seq;
DROP TABLE public.hittypes;
DROP SEQUENCE public.dictionary_id_seq;
DROP TABLE public.dictionary;
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- TOC entry 2184 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 178 (class 3079 OID 11906)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2185 (class 0 OID 0)
-- Dependencies: 178
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_with_oids = false;

--
-- TOC entry 164 (class 1259 OID 16584)
-- Dependencies: 5
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
-- TOC entry 163 (class 1259 OID 16582)
-- Dependencies: 164 5
-- Name: dictionary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dictionary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2186 (class 0 OID 0)
-- Dependencies: 163
-- Name: dictionary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE dictionary_id_seq OWNED BY dictionary.id;


--
-- TOC entry 170 (class 1259 OID 16698)
-- Dependencies: 5
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
-- TOC entry 169 (class 1259 OID 16696)
-- Dependencies: 5 170
-- Name: hittypes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE hittypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2187 (class 0 OID 0)
-- Dependencies: 169
-- Name: hittypes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE hittypes_id_seq OWNED BY hittypes.id;


--
-- TOC entry 162 (class 1259 OID 16573)
-- Dependencies: 5
-- Name: languages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE languages (
    id integer NOT NULL,
    name character varying,
    prefix character varying
);


--
-- TOC entry 161 (class 1259 OID 16571)
-- Dependencies: 5 162
-- Name: languages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE languages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2188 (class 0 OID 0)
-- Dependencies: 161
-- Name: languages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE languages_id_seq OWNED BY languages.id;


--
-- TOC entry 177 (class 1259 OID 16802)
-- Dependencies: 5
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
-- TOC entry 176 (class 1259 OID 16799)
-- Dependencies: 5
-- Name: synonymshitresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshitresults (
);


--
-- TOC entry 174 (class 1259 OID 16793)
-- Dependencies: 5
-- Name: synonymshits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshits (
);


--
-- TOC entry 175 (class 1259 OID 16796)
-- Dependencies: 5
-- Name: synonymshitsdata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE synonymshitsdata (
);


--
-- TOC entry 166 (class 1259 OID 16600)
-- Dependencies: 5
-- Name: vocabulary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vocabulary (
    id integer NOT NULL,
    word character varying,
    sentences text,
    language_id integer
);


--
-- TOC entry 165 (class 1259 OID 16598)
-- Dependencies: 5 166
-- Name: vocabulary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabulary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2189 (class 0 OID 0)
-- Dependencies: 165
-- Name: vocabulary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabulary_id_seq OWNED BY vocabulary.id;


--
-- TOC entry 173 (class 1259 OID 16787)
-- Dependencies: 5
-- Name: vocabularyhitresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vocabularyhitresults (
    id integer,
    mturk_hit_id character varying,
    mturk_assignment_id character varying,
    mturk_worker_id character varying,
    results character varying,
    control character varying,
    quality real
);


--
-- TOC entry 172 (class 1259 OID 16723)
-- Dependencies: 5
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
-- TOC entry 171 (class 1259 OID 16721)
-- Dependencies: 172 5
-- Name: vocabularyhits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabularyhits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2190 (class 0 OID 0)
-- Dependencies: 171
-- Name: vocabularyhits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabularyhits_id_seq OWNED BY vocabularyhits.id;


--
-- TOC entry 168 (class 1259 OID 16682)
-- Dependencies: 5
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
-- TOC entry 167 (class 1259 OID 16680)
-- Dependencies: 5 168
-- Name: vocabularyhitsdata_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE vocabularyhitsdata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2191 (class 0 OID 0)
-- Dependencies: 167
-- Name: vocabularyhitsdata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE vocabularyhitsdata_id_seq OWNED BY vocabularyhitsdata.id;


--
-- TOC entry 2162 (class 2604 OID 16587)
-- Dependencies: 163 164 164
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE dictionary ALTER COLUMN id SET DEFAULT nextval('dictionary_id_seq'::regclass);


--
-- TOC entry 2165 (class 2604 OID 16701)
-- Dependencies: 169 170 170
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE hittypes ALTER COLUMN id SET DEFAULT nextval('hittypes_id_seq'::regclass);


--
-- TOC entry 2161 (class 2604 OID 16576)
-- Dependencies: 162 161 162
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE languages ALTER COLUMN id SET DEFAULT nextval('languages_id_seq'::regclass);


--
-- TOC entry 2163 (class 2604 OID 16603)
-- Dependencies: 165 166 166
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabulary ALTER COLUMN id SET DEFAULT nextval('vocabulary_id_seq'::regclass);


--
-- TOC entry 2166 (class 2604 OID 16726)
-- Dependencies: 171 172 172
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabularyhits ALTER COLUMN id SET DEFAULT nextval('vocabularyhits_id_seq'::regclass);


--
-- TOC entry 2164 (class 2604 OID 16685)
-- Dependencies: 168 167 168
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE vocabularyhitsdata ALTER COLUMN id SET DEFAULT nextval('vocabularyhitsdata_id_seq'::regclass);


--
-- TOC entry 2170 (class 2606 OID 16592)
-- Dependencies: 164 164
-- Name: dictionary_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_id_pk PRIMARY KEY (id);


--
-- TOC entry 2176 (class 2606 OID 16706)
-- Dependencies: 170 170
-- Name: hittypes_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY hittypes
    ADD CONSTRAINT hittypes_id_pk PRIMARY KEY (id);


--
-- TOC entry 2168 (class 2606 OID 16581)
-- Dependencies: 162 162
-- Name: languages_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY languages
    ADD CONSTRAINT languages_id_pk PRIMARY KEY (id);


--
-- TOC entry 2172 (class 2606 OID 16608)
-- Dependencies: 166 166
-- Name: vocabulary_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_id_pk PRIMARY KEY (id);


--
-- TOC entry 2178 (class 2606 OID 16731)
-- Dependencies: 172 172
-- Name: vocabularyhits_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabularyhits
    ADD CONSTRAINT vocabularyhits_id_pk PRIMARY KEY (id);


--
-- TOC entry 2174 (class 2606 OID 16690)
-- Dependencies: 168 168
-- Name: vocabularyhitsdata_id_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabularyhitsdata
    ADD CONSTRAINT vocabularyhitsdata_id_pk PRIMARY KEY (id);


--
-- TOC entry 2179 (class 2606 OID 16593)
-- Dependencies: 162 2167 164
-- Name: dictionary_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


--
-- TOC entry 2180 (class 2606 OID 16609)
-- Dependencies: 162 166 2167
-- Name: vocabulary_language_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);


-- Completed on 2012-01-10 11:29:28 EST

--
-- PostgreSQL database dump complete
--

