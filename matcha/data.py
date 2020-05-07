import sqlite3
import os
import requests
from random import randrange, uniform
from db import db_connect, dict_factory, setup_tables
import time
import json

users =[]

input_file = open("users.json")
json_array = json.load(input_file)
store_list = []



def fakedata():
	while True:
		query = input('Do you want add users to the db? ')
		Fl = query[0].lower()
		if query == '' or not Fl in ['y','n']:
			print('Please answer with yes or no!')
		else:
			break
	if Fl == 'y':
		con = db_connect()
		cur = con.cursor()
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify) VALUES (?, ?, ?, ?, ?, ?)', 
			['System', 'System', 'system', 'System@mailcatch.com', '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None])
		i = 1
		for user in json_array:
			num = randrange(999)
			user['email'] = user['username'] + '@mailcatch.com'
			user['bio'] = str(num)
			user['gender'] = 'M' if randrange(100) % 2 == 0 else 'F'
			user['sexuality'] = 'S' if randrange(100) % 2 == 0 else 'G'
			user['age'] = randrange(100)
			user['latCord'] = round(uniform(-22.573568,-34.434213), 7)
			user['lngCord'] = round(uniform(33.047712,19.336774), 7)
			url = 'http://nominatim.openstreetmap.org/reverse?format=json&lat='+ str(user['latCord']) +'&lon=' + str(user['lngCord'])
			try:
				city = requests.get(url).json()['address']['city']
			except:
				city = "Pretoria"
			user['city'] = city
			print(user)
			cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age, latCord, lngCord, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			[user['name'], user['surname'], user['username'], user['email'], '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None, user['bio'], user['gender'], user['sexuality'], user['age'], user['latCord'], user['lngCord'], user['city']])
			i += 1
			print("Adding user:" + str(i))
			cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		# Set users add here
		
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age, lngCord, latCord) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			['Frederick', 'Moor', 'fwmoor', 'fwmoor10@gmail.com', '5658acbfe570c18325a539e8904f0364b1da18a3bae0b0c66556e402c5827ee706ff8bbff9caad5d4b0c2aad10d630a8865114dc26df878e3aa201f27fa11edb1612df8b781a486f2dcefa3ecc6cfe32a1c5c2aa24bcc24b1aa0890f23d3a38c', None, 'Freddy', 'M', 'S', 19, 18.45, 20.45])
		i += 1
		cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age, lngCord, latCord) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			['Mikey', 'Meyer', 'mikefmeyer', 'gicom52548@mailon.ws', '4481473052b1d04e3fb29a02b4871259b5428ccb49e823248b81c6a65068ac5c37dc0a50c0b46cfa3de98f76e34da847783c889a94858aa3e6ff279f75fe5ba3d4616bb7a5f4ed849172b0347b5884a3e795e1f4b323dc36d90a6fc9ac2d5dfc', None, 'Mikey', 'M', 'S', 22, 20.45, 40.41234])
		i += 1
		cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age, lngCord, latCord) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			['Ruben', 'Coetzer', 'rubzy0422', 'rcoetzer5@gmail.com', '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None, 'Rubzy', 'M', 'S', 19, -10.5456, 24.567])
		i += 1
		cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		con.commit()
		con.close()
		print ("Users added!")
setup_tables()
fakedata()
