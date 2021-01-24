TRUNCATE TABLE staging.%(table_name)s;
COPY staging.%(table_name)s (%(column_select)s)
FROM STDIN
WITH
    DELIMITER AS '%(delim)s'
    HEADER
    CSV
    QUOTE E'\b'
    ESCAPE E'\b'
;

DELETE FROM %(schema)s.%(table_name)s a
USING
    staging.%(table_name)s b
WHERE
    %(primary_key_join)s
;

INSERT INTO %(schema)s.%(table_name)s
    (%(column_select)s)
SELECT
    %(column_select)s
FROM
    staging.%(table_name)s
;