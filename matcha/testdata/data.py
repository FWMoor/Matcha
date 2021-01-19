import os,sys,inspect
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import sqlite3
import requests
from random import randrange, uniform, randint
from db import db_connect, dict_factory, setup_tables
import time
import json
import secrets
import urllib.request

import shutil
from threading import Thread
import datetime

users =[]
HCODE = 500
input_file = open(os.path.join(current_dir, 'users.json'),encoding="utf-8")
json_array = json.load(input_file)
jsonlen = len(json_array)
store_list = []


def intTryParse(value):
	try:
		return int(value), True
	except ValueError:
		return value, False

def clear(): 
	if os.name == 'nt':
		_ = os.system('cls') 
	else: 
		_ = os.system('clear') 

def clean():
	mypath = os.path.join(current_dir, "../static/photos")
	for f in os.listdir(mypath):
		fpath = os.path.join(mypath, f)
		if os.path.isfile(fpath):
			if (f == '.gitkeep' or f == 'default.jpeg'):
				pass
			else:
				os.remove(fpath)
	dbloc = os.path.join(current_dir,"../site.db")
	dbjournalloc = os.path.join(current_dir,"../site.db-journal")
	if os.path.exists(dbloc):
  		os.remove(dbloc)
	if os.path.exists(dbjournalloc):
		os.remove(dbjournalloc)

def fakedata(useramount):
	while True:
		query = input('Do you want generate the db?\n[WARNING]\tThis action will remove all current records\n[Y/N]\n')
		Fl = query[0].lower()
		if query == '' or not Fl or not Fl in ['y','n']:
			print('Please answer with yes or no!')
		else:
			break
	if Fl == 'y':
		try:
			clean()
			setup_tables()
			string = " CREATEING " + str(useramount) + " RECORDS "
			print(string.center(100, '='))
			con = db_connect()
			cur = con.cursor()
			tag_arr_len = add_tags(cur)[0]
			add_users(cur, useramount)
			set_user_tags(cur, useramount, tag_arr_len)
			con.commit()
			con.close()
		except Exception as ex:
			print('Could not generate the data!' + str(ex))

def add_tags(cur):
	tagarr = ["tag", "love", "games", "coding", "WTC", "intern", "design", "art"]

	for tag in tagarr:
		cur.execute("SELECT * FROM tags WHERE UPPER(tags) = UPPER(?)", [tag])
		result = cur.fetchall()
		if result:
			# print('Tag already exists skipping!')
			pass
		else:
			cur.execute("INSERT INTO tags (tags) VALUES (UPPER(?))", [tag])
	cur.execute("SELECT COUNT(*) FROM tags")
	result = cur.fetchone()
	return result	

def set_user_tags(cur, useramount, tag_arr_len):
	usernum = 2

	tagnum = randrange(tag_arr_len)
	while usernum < useramount:
		cur.execute("SELECT * FROM usertags WHERE tagId = ? AND userId = ?", [tagnum, usernum])
		result = cur.fetchall()
		if result:
			# print('Tag already exists for this user, skipping!')
			pass
		else:
			cur.execute("INSERT INTO usertags (userId, tagId) VALUES (?,?)", [usernum, tagnum])
		usernum = usernum + 1

def random_date(start, end):
	delta = end - start
	int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
	random_second = randrange(int_delta)
	return start + timedelta(seconds=random_second)

def randbirthday(now):
	max = (now.year - 18)
	min = (now.year - 80)
	year = randint(min, max)
	month = randint(1, 12)
	day = randint(1, 28)
	age = now.year - year
	if now.month < month or (now.month == month and now.day < day):
		age -= 1
		# yyyy-mm-dd
	if month < 10:
		month = "0" + str(month)
	else:
		month = str(month)
	if day < 10:
		day = "0" + str(day)
	else:
		day = str(day)
	
	birthday = str(year) + "-" + month +"-" + day
	
	return birthday, age

def add_users(cur, useramount):
	# RECORD 1 ALWAYS SYSTEM
	gender_arr = ['M', 'F']
	sexuality_arr = ['S', 'G', 'B']
	i = 2
	now = datetime.datetime.now()
	for user in json_array:
		max = len(json_array)
		if useramount < max:
			max = useramount
		if i <= (useramount) and i <= max:
			user['email'] = user['username'] + '@mailcatch.com'
			user['bio'] = "blah blah blah blah blah blah blah blah blah blah blah"
			user['gender'] = gender_arr[randrange(len(gender_arr))]
			user['sexuality'] = sexuality_arr[randrange(len(sexuality_arr))]
			user['birthdate'], user['age'] = randbirthday(now)
			user['totalviews'] = randrange(300)
			printProgressBar(i, max, msgcomplete = "Users Added Succesfully!")
			active, _ = images(i, cur)
			cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
			cur.execute('INSERT INTO users (fname, lname, username, email, verify, bio, gender, sexuality, complete, birthdate, totalviews, password) VALUES (?,?,?,?, ?,?,?,?, ?,?,?,?)', 
			[user['name'],
			user['surname'],
			user['username'],
			user['email'],
			
			None,
			user['bio'],
			user['gender'],
			user['sexuality'],
			
			active,
			user['birthdate'],
			user['totalviews'], 
			'70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b'])
			
			cur.execute('INSERT INTO location (latCord, lngCord, city, userid) VALUES (?, ?, ?, ?)', [user['latCord'], user['lngCord'], user['city'], i])
			i += 1

def get_picture(uid):
	download = 0
	
	random_hex = secrets.token_hex(8)
	picture_fn = str(uid) + "." + str(random_hex) + ".jpg"
	picture_path = os.path.join(os.path.join(current_dir,"../static/photos"), picture_fn)
	
	if download == 1:
		url = "https://picsum.photos/200"
		page = requests.get(url)
		with open(picture_path, 'wb') as f:
			f.write(page.content)
			f.close()
		return picture_fn
	else:
		dst = picture_path
		src = os.path.join(current_dir,'photos/') + str(randrange(19) + 1) + '.jpg'
		Thread(target=shutil.copy, args=[src, dst]).start()
		return picture_fn

def images(uid, cur):
	pfp = None
	num = randrange(5)
	photo = 0
	while photo < num:		
		cur.execute("SELECT * FROM photos WHERE userId=?", [uid])
		tot = cur.fetchall()
		if len(tot) < 5:
			picture_file = get_picture(uid)
			if picture_file != 'Empty':
				cur.execute("SELECT * FROM photos WHERE userId=?", [uid])
				pics = cur.fetchall()
				if not pics:
					pfp = picture_file
					cur.execute("INSERT INTO photos (userId, path, profile) VALUES (?, ?, 1)", [uid, picture_file])
				else:
					cur.execute("INSERT INTO photos (userId, path) VALUES (?, ?)", [uid, picture_file])
		photo = photo + 1
	if (num > 0):
		return 1, pfp
	else:
		return 0, pfp

def printProgressBar (iteration, total, prefix = 'Progress', suffix = '', decimals = 1, length = 100, fill = '#', printEnd = "\r", msgcomplete = ''):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
	if iteration == total: 
		print()
		string = " " + str(msgcomplete) + " "
		print(string.center(100, '='))

def main():
	string = " DATA CREATOR MAIN MENU "
	print(string.center(100, "="))
	print("    / \/ \         * This utility can remove or create new DB data")
	print("    \    /         * Program: Matcha")
	print("     \  /          * Author: Ruben Coetzer")
	print("      \/           * Version: 1.0.0")
	print(''.center(100, "="))
	print("OPTIONS")
	print("1. Generate New DATA")
	print("2. Clean Data")
	dopart = input("> ")

	if dopart == "1":
		# print(dopart)
		value = input("Amount of records to generate (MAX =" + str(HCODE) + ") \n>")
		val, success = intTryParse(value)
		if (success):
			if (val > HCODE or val < 2):
				print("invalid amount, needs to have between 2 and " + str(HCODE))
				return
			fakedata(val)
		else:
			clear()
			main()
	if dopart == "2":
		clean()

main()