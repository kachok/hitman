DROP FUNCTION add_hittype(hittypeid TEXT, hittypename TEXT, languageid INT, hittypelanguage TEXT, hittypetype TEXT);
CREATE FUNCTION add_hittype(hittypeid TEXT, hittypename TEXT, languageid INT, hittypelanguage TEXT, hittypetype TEXT) RETURNS VOID AS
$$
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
$$
LANGUAGE plpgsql;

DROP FUNCTION add_language(langname TEXT, langprefix TEXT);
CREATE FUNCTION add_language(langname TEXT, langprefix TEXT) RETURNS VOID AS
$$
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
$$
LANGUAGE plpgsql;


DROP FUNCTION add_vocabularyhitresult(hitid TEXT, assignmentid TEXT, workerid TEXT, result TEXT, submittime TEXT, wordid INT, translation2 TEXT, reason2 TEXT, iscontrol INT);
CREATE FUNCTION add_vocabularyhitresult(hitid TEXT, assignmentid TEXT, workerid TEXT, result TEXT, submittime TEXT, wordid INT, translation2 TEXT, reason2 TEXT, iscontrol INT) RETURNS INTEGER AS
$$
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
$$
LANGUAGE plpgsql;

DROP FUNCTION add_worker(workerid TEXT, workername TEXT);
CREATE FUNCTION add_worker(workerid TEXT, workername TEXT) RETURNS INTEGER AS
$$
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
$$
LANGUAGE plpgsql;



DROP FUNCTION add_location(workerid INT, ip2 TEXT, city2 TEXT, region2 TEXT, country2 TEXT, zipcode2 TEXT, lat2 TEXT, lng2 TEXT, timestamp2 TIMESTAMP);
CREATE FUNCTION add_location(workerid INT, ip2 TEXT, city2 TEXT, region2 TEXT, country2 TEXT, zipcode2 TEXT, lat2 TEXT, lng2 TEXT, timestamp2 TIMESTAMP) RETURNS VOID AS
$$
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
$$
LANGUAGE plpgsql;