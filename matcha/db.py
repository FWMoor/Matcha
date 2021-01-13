import sqlite3
import os

SQL_PATH = os.path.join(os.path.dirname(__file__), 'matcha.sql')
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
	with open(SQL_PATH, 'r') as sqlfile:
		sql = sqlfile.read()
	cur.executescript(sql)
	# Add admin account
	cur.execute('INSERT INTO users (fname, lname, username, email, password, verify) VALUES (?, ?, ?, ?, ?, ?)', 
	['System', 'System', 'system', 'System@mailcatch.com', '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None])
	con.commit()
	con.close()
