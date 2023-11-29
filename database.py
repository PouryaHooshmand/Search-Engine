import sqlite3
from sqlite3 import Error

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return cursor
    except Error as e:
        print(f"The error '{e}' occurred")

def create_table(connection, table_name, fields, types, has_id):
    if has_id:
        id_query = "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    else:
        id_query = ""
    fields_query = ", ".join([fields[i]+" "+types[i]+" NOT NULL" for i in range(len(fields))])
    query = f"CREATE TABLE IF NOT EXISTS {table_name}({id_query}{fields_query});"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return cursor
    except Error as e:
        print(f"The error '{e}' occurred")

def add_to_table(connection, table_name, values, unique_field_idx = None, unique_field_name = None):
    if unique_field_idx is not None:
        if type(values[unique_field_idx]) is str:
            unique_value = "'"+values[unique_field_idx]+"'"
        id_query = f"(select id from {table_name} where {unique_field_name} = {unique_value}),"
        values_query = ", ".join([":"+str(i) for i in range(len(values))])
    var_dict = {}
    for i in range(len(values)):
        var_dict[str(i)] = values[i]
    insert_query = f"INSERT OR REPLACE INTO {table_name} values ({id_query} {values_query});"
    
    cursor = connection.cursor()
    try:
        cursor.execute(insert_query, var_dict)
        connection.commit()
        return cursor
    except Error as e:
        print(f"The error '{e}' occurred")

def get_row(connection, table_name, id_list, website = None):
    if website is None:
        query = f"SELECT * FROM {table_name} where id in {id_list}"
    else:
        query = f"SELECT * FROM {table_name} where id in {id_list} and link like \'%{website}%\' --case-insensitive"
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

 