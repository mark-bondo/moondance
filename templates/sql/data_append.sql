TRUNCATE TABLE staging.%(table_name)s;
COPY staging.%(table_name)s (%(column_select)s)
FROM STDIN
WITH
    DELIMITER AS '%(delim)s'
    HEADER
    CSV
    QUOTE AS E'\b'
;

DELETE FROM %(schema)s.%(table_name)s
WHERE
    %(date_append_column)s BETWEEN '%(start_date)s' AND '%(end_date)s'
;

INSERT INTO %(schema)s.%(table_name)s
    (%(column_select)s)
SELECT
    %(column_select)s
FROM
    staging.%(table_name)s
WHERE
    %(date_append_column)s BETWEEN '%(start_date)s' AND '%(end_date)s'
;