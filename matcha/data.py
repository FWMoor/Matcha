import sqlite3
import os
from random import randrange
from db import db_connect, dict_factory, setup_tables

users =[{ "name":'Jonas', "surname":'Herman' }, { "name":'Prescott', "surname":'Suarez' }, { "name":'Griffin', "surname":'Obrien' }, { "name":'Zoe', "surname":'Cortez' }, { "name":'Kenyon', "surname":'Weaver' }, { "name":'Suki', "surname":'Goff' }, { "name":'Austin', "surname":'Buchanan' }, { "name":'Rebekah', "surname":'Good' }, { "name":'Xena', "surname":'Schroeder' }, { "name":'Germane', "surname":'Lloyd' }, { "name":'Hunter', "surname":'Gordon' }, { "name":'Jemima', "surname":'Chan' }, { "name":'Jeanette', "surname":'Curtis' }, { "name":'Kaden', "surname":'Kemp' }, { "name":'Tanek', "surname":'Rivera' }, { "name":'Donovan', "surname":'Mcintyre' }, { "name":'Shoshana', "surname":'Boyle' }, { "name":'Yvonne', "surname":'Bruce' }, { "name":'Aphrodite', "surname":'Robertson' }, { "name":'Kim', "surname":'Buck' }, { "name":'August', "surname":'Simpson' }, { "name":'Josiah', "surname":'Miller' }, { "name":'Ginger', "surname":'Solis' }, { "name":'Laith', "surname":'Mcguire' }, { "name":'Ezekiel', "surname":'Rogers' }, { "name":'Harding', "surname":'Barlow' }, { "name":'Joseph', "surname":'Powers' }, { "name":'Judith', "surname":'Weaver' }, { "name":'Shad', "surname":'Mercado' }, { "name":'Harrison', "surname":'Lyons' }, { "name":'Mollie', "surname":'Wiggins' }, { "name":'Clinton', "surname":'Hodge' }, { "name":'Callie', "surname":'Harmon' }, { "name":'Kareem', "surname":'Spence' }, { "name":'Neville', "surname":'Ingram' }, { "name":'Ross', "surname":'Baldwin' }, { "name":'Serina', "surname":'Aguirre' }, { "name":'Yoshio', "surname":'Hamilton' }, { "name":'Macy', "surname":'Wallace' }, { "name":'Orla', "surname":'Ferguson' }, { "name":'Callum', "surname":'Hutchinson' }, { "name":'Yvette', "surname":'Bean' }, { "name":'Carol', "surname":'Marks' }, { "name":'Devin', "surname":'Mayer' }, { "name":'Serena', "surname":'Tran' }, { "name":'Kylee', "surname":'Moreno' }, { "name":'Erasmus', "surname":'Stein' }, { "name":'Nora', "surname":'Osborn' }, { "name":'Cecilia', "surname":'Mckinney' }, { "name":'Victoria', "surname":'Ellison' }, { "name":'Demetria', "surname":'Herman' }, { "name":'Hayden', "surname":'Reid' }, { "name":'Porter', "surname":'Hicks' }, { "name":'Charles', "surname":'Tran' }, { "name":'Lila', "surname":'Mcpherson' }, { "name":'Tanek', "surname":'Mayo' }, { "name":'Eaton', "surname":'Grimes' }, { "name":'Dawn', "surname":'Buchanan' }, { "name":'Grady', "surname":'Mcneil' }, { "name":'Harriet', "surname":'Flynn' }, { "name":'Kiona', "surname":'Miller' }, { "name":'Baker', "surname":'Berry' }, { "name":'Gillian', "surname":'Kim' }, { "name":'Sandra', "surname":'Cleveland' }, { "name":'Aurora', "surname":'Matthews' }, { "name":'Kaden', "surname":'Whitfield' }, { "name":'Stella', "surname":'Yang' }, { "name":'Quin', "surname":'Lopez' }, { "name":'Emery', "surname":'Gilbert' }, { "name":'Pamela', "surname":'Spencer' }, { "name":'Megan', "surname":'Shaw' }, { "name":'Harding', "surname":'Dunn' }, { "name":'Gareth', "surname":'Cardenas' }, { "name":'Raymond', "surname":'Jefferson' }, { "name":'Joseph', "surname":'George' }, { "name":'Micah', "surname":'Bridges' }, { "name":'Iona', "surname":'Mcgee' }, { "name":'Alvin', "surname":'House' }, { "name":'Sasha', "surname":'Turner' }, { "name":'Sean', "surname":'Huffman' }, { "name":'Keaton', "surname":'Barnett' }, { "name":'William', "surname":'Ryan' }, { "name":'Alisa', "surname":'Brooks' }, { "name":'Kaitlin', "surname":'Huber' }, { "name":'Kato', "surname":'Cox' }, { "name":'Fleur', "surname":'Kline' }, { "name":'Neve', "surname":'Valentine' }, { "name":'Brennan', "surname":'Cooley' }, { "name":'Naida', "surname":'Wallace' }, { "name":'Davis', "surname":'Welch' }, { "name":'Urielle', "surname":'Cannon' }, { "name":'Fitzgerald', "surname":'Crane' }, { "name":'Price', "surname":'Watkins' }, { "name":'Sarah', "surname":'Blackwell' }, { "name":'Claudia', "surname":'Davidson' }, { "name":'Yoko', "surname":'Watson' }, { "name":'Brett', "surname":'Foreman' }, { "name":'Beck', "surname":'Roberson' }, { "name":'Rina', "surname":'Nichols' }, { "name":'Malachi', "surname":'Russo'}]

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
			['System', 'System', 'System', 'System@mailcatch.com', '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None])
		i = 1
		for user in users:
			num = randrange(999)
			user['username'] = (user['name'] + str(num)).lower()
			user['email'] = user['username'] + '@mailcatch.com'
			user['bio'] = str(num)
			user['gender'] = 'M' if randrange(100) % 2 == 0 else 'F'
			user['sexuality'] = 'S' if randrange(100) % 2 == 0 else 'G'
			user['age'] = randrange(100)
			cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			[user['name'], user['surname'], user['username'], user['email'], '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None, user['bio'], user['gender'], user['sexuality'], user['age']])
			i += 1
			cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		# Set users add here
		
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			['Frederick', 'Moor', 'fwmoor', 'fwmoor10@gmail.com', '5658acbfe570c18325a539e8904f0364b1da18a3bae0b0c66556e402c5827ee706ff8bbff9caad5d4b0c2aad10d630a8865114dc26df878e3aa201f27fa11edb1612df8b781a486f2dcefa3ecc6cfe32a1c5c2aa24bcc24b1aa0890f23d3a38c', None, 'Freddy', 'M', 'S', 19])
		i += 1
		cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			['Mikey', 'Meyer', 'mikefmeyer', 'gicom52548@mailon.ws', '4481473052b1d04e3fb29a02b4871259b5428ccb49e823248b81c6a65068ac5c37dc0a50c0b46cfa3de98f76e34da847783c889a94858aa3e6ff279f75fe5ba3d4616bb7a5f4ed849172b0347b5884a3e795e1f4b323dc36d90a6fc9ac2d5dfc', None, 'Mikey', 'M', 'S', 22])
		i += 1
		cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		cur.execute('INSERT INTO users (fname, lname, username, email, password, verify, bio, gender, sexuality, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			['Ruben', 'Coetzer', 'rubzy0422', 'rcoetzer5@gmail.com', '70d6d3db2b8cee727994e89f9b8c21622e39840ad579dd82da37aadd441473aab9996dd749d652b8023791f3862ca3cc584f9ff9c27222217e77af241d3b3abd54486eeb78c733c57aab7aa7ff5709ec90655dee193c4a32e46ffb2796049d0b', None, 'Rubzy', 'M', 'S', 19])
		i += 1
		cur.execute('INSERT INTO matches (user1,user2) VALUES (1, ?)', [i])
		con.commit()
		con.close()
		print ("Users added!")
setup_tables()
fakedata()
