CREATE TABLE languages (
    id serial NOT NULL,
    name character varying,
    prefix character varying
);
ALTER TABLE ONLY languages
    ADD CONSTRAINT languages_id_pk PRIMARY KEY (id);

CREATE TABLE dictionary (
    id serial NOT NULL,
    word character varying,
    sentences character varying,
    language_id integer,
    translation character varying
);
ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_id_pk PRIMARY KEY (id);
ALTER TABLE ONLY dictionary
    ADD CONSTRAINT dictionary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);

CREATE TABLE vocabulary (
    id serial NOT NULL,
    word character varying,
    sentences text,
    language_id integer
);
ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_id_pk PRIMARY KEY (id);
ALTER TABLE ONLY vocabulary
    ADD CONSTRAINT vocabulary_language_id_fk FOREIGN KEY (language_id) REFERENCES languages(id);



CREATE TABLE hittypes (
    id serial NOT NULL,
    name character varying,
	hittypeid character varying
);
ALTER TABLE ONLY hittypes
    ADD CONSTRAINT hittypes_id_pk PRIMARY KEY (id);

CREATE TABLE vocabularyhits (
    id serial NOT NULL,
    hitid character varying,
	hittype_id integer,
	uuid character varying
);
ALTER TABLE ONLY vocabularyhits
    ADD CONSTRAINT vocabularyhits_id_pk PRIMARY KEY (id);
ALTER TABLE ONLY vocabularyhits
    ADD CONSTRAINT vocabularyhits_hittypes_id_fk FOREIGN KEY (hittype_id) REFERENCES hittypes(id);


CREATE TABLE vocabularyhitsdata (
    id serial NOT NULL,
    hit_id integer,
	word_id integer,
	type character varying
);
ALTER TABLE ONLY vocabularyhitsdata
    ADD CONSTRAINT vocabularyhitsdata_id_pk PRIMARY KEY (id);
ALTER TABLE ONLY vocabularyhitsdata
    ADD CONSTRAINT vocabularyhitsdata_vocabularyhits_id_fk FOREIGN KEY (hit_id) REFERENCES vocabularyhits(id);
