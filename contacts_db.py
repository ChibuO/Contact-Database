#for contacts_app.py
#this is the code that only interacts with the database

import sqlite3

#add queries separately so it's easier to change later on
CREATE_CONTACTS_TABLE = """CREATE TABLE IF NOT EXISTS contacts 
(id INTEGER PRIMARY KEY, fname TEXT, lname TEXT, major TEXT, year INTEGER, state TEXT, met TEXT);"""

INSERT_CONTACT = "INSERT INTO contacts (fname, lname, major, year, state, met) VALUES (?, ?, ?, ?, ?, ?);" #include inputs for ? when used

GET_ALL_CONTACTS = "SELECT * FROM contacts;"
GET_ALL_CONTACTS_REV = "SELECT * FROM contacts ORDER BY id DESC;"
SORT_BY = "SELECT * FROM contacts ORDER BY {field};"
SORT_BY_REV = "SELECT * FROM contacts ORDER BY {field} DESC;"

GET_CONTACTS_BY_FIRST_NAME = "SELECT * FROM contacts WHERE fname = ?;"

REMOVE_CONTACT = "DELETE FROM contacts WHERE id = ?;"

EDIT_CONTACT = """UPDATE contacts
SET fname = ?, lname = ?, major = ?, year = ?, state = ?, met = ?
WHERE id = ?;"""

def connect():
    #open data file. if not there, create one
    return sqlite3.connect("contact_data.db", isolation_level=None)

def create_tables(connection):
    #context manager, when we create database, it gets saved to the ^^ file
    with connection:
        connection.execute(CREATE_CONTACTS_TABLE)

def add_contact(connection, fname, lname, major, year, state, met):
    with connection:
        connection.execute(INSERT_CONTACT, (fname, lname, major, year, state, met)) #second param has to be tuple

def get_all_contacts(connection):
    with connection:
        return connection.execute(GET_ALL_CONTACTS_REV).fetchall()

def sort_by_field(connection, field):
    with connection:
        return connection.execute(SORT_BY.format(field=field)).fetchall()
        #fetch all gives us a list of rows

def reverse_sort_by_field(connection, field):
    if ("First Name" in field):
        field = "fname"
    elif ("Last Name" in field):
        field = "lname"
    elif ("State" in field):
        field = "state"
    elif ("Major" in field):
        field = "major"
    elif ("Year" in field):
        field = "year"
    elif ("Met" in field):
        field = "met"
    elif ("Date Added" in field):
        field = "id"
    else:
        field = "id"

    with connection:
        return connection.execute(SORT_BY_REV.format(field=field)).fetchall()
        #fetch all gives us a list of rows

def remove_contact(connection, id):
    with connection:
        connection.execute(REMOVE_CONTACT, (id,)) #second param has to be tuple

def update_contact(connection, id, fname, lname, major, year, state, met):
    with connection:
        connection.execute(EDIT_CONTACT, (fname, lname, major, year, state, met, id)) #second param has to be tuple
