
from django.db import connection

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def cursor_rows(sql, params=[]):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = dictfetchall(cursor)
    return row
    
def cursor_one_row(sql, params=[]):
    return cursor_rows(sql, params)[0]

def cursor_one_column(sql, params=[]):
    r=[]
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows=cursor.fetchall()
        for row in rows:
            r.append(row[0])
    return r
        
def cursor_one_field(sql, params=[]):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
    return row[0]
