import sqlite3
import os

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'site.db')

def db_connect(db_path=DEFAULT_PATH):
	con = sqlite3.connect(db_path)
	return con

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def setup_tables():
	con = db_connect()
	cur = con.cursor()
	cur.execute("""CREATE TABLE IF NOT EXISTS users (
		id integer PRIMARY KEY,
		fname text NOT NULL,
		lname text NOT NULL,
		username text NOT NULL,
		email text NOT NULL,
		password text NOT NULL
		);""")
	con.commit()
	con.close()
