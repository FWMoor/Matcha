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
	cur.execute("""CREATE TABLE IF NOT EXISTS blocked (
		userId INTEGER NOT NULL,
		blockedId	INTEGER NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS reports (
		userId INTEGER NOT NULL,
		reportedId	INTEGER NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS matches (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user1	INTEGER NOT NULL,
		user2	INTEGER NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS likes (
		user1	INTEGER NOT NULL,
		user2	INTEGER NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		matchId INTEGER NOT NULL,
		senderId INTEGER NOT NULL,
		receiveId	INTEGER NOT NULL,
		message TEXT NOT NULL,
		time TEXT NOT NULL,
		seen INTEGER DEFAULT 0
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS notifications (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		userId INTEGER NOT NULL,
		notificationFrom INTEGER NOT NULL,
		notification TEXT NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS photos (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		userId INTEGER NOT NULL,
		path TEXT NOT NULL,
		profile INTEGER
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS tags (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		tags TEXT NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS usertags (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		userId INTEGER NOT NULL,
		tagId INTEGER NOT NULL
	);""")
	con.commit()
	cur.execute("""CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		fname	TEXT NOT NULL,
		lname	TEXT NOT NULL,
		username TEXT NOT NULL,
		email	TEXT NOT NULL,
		password TEXT NOT NULL,
		verify TEXT,
		banned INTEGER NOT NULL DEFAULT 0,
		gender TEXT,
		bio TEXT,
		age INTEGER,
		path TEXT,
		sexuality TEXT DEFAULT 'S',
		tags TEXT,
		location TEXT,
		complete INTEGER DEFAULT 0,
		notifications INTERGER NOT NULL DEFAULT 1,
		fame INTEGER NOT NULL DEFAULT 0,
		online INTEGER NOT NULL DEFAULT 0,
		lastonline TEXT,
		birthdate TEXT,
		passreset TEXT
		);""")
	con.commit()
	con.close()
