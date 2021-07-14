import psycopg2
import os
import contextlib

ESCAPE_LIST = [("\b", "\\b"), ("\n", "\\n"), ("\r", "\\r"), ("\t", "\\t")]


def get_table_columns(db_string, table_name):
    with contextlib.closing(psycopg2.connect(db_string)) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            sql = """
                SELECT
                    *
                FROM
                    staging.{}
                WHERE
                    0=1
                ;
            """.format(
                table_name
            )
            cursor.execute(sql)
    return [x[0] for x in cursor.description]


def escape_value(value):
    for e in ESCAPE_LIST:
        if e[0] in value:
            value = value.replace(e[0], e[1])

    return value


def insert_data(object_dd, db_string):
    primary_key_list = object_dd["pk_list"]

    with open("automationtools/templates/sql/{}.sql".format("pk_append"), "r") as f:
        sql = f.read() % {
            "schema": object_dd["schema"],
            "table_name": object_dd["table_name"],
            "column_select": ",".join(
                ['"{}"'.format(x) for x in object_dd["table_columns"]]
            ),
            "delim": "\t",
            "date_append_column": "datetime_updated",
            "primary_key_join": " AND ".join(
                [
                    'a."{0}"=b."{0}"'.format(x)
                    for x in primary_key_list
                    if primary_key_list
                ]
            ),
        }

    with contextlib.closing(psycopg2.connect(db_string)) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            # print(sql)
            cursor.copy_expert(sql, open(object_dd["file_name"], "r", encoding="utf-8"))

        conn.commit()
        os.remove(object_dd["file_name"])
