from flask import session, flash, render_template
from matcha.db import db_connect, dict_factory
from matcha.utils.general import getdist, get_age
from datetime import date

# Define some reuseable vars
userQuery = """SELECT u.fname, u.lname, u.email, u.id, u.username, u.gender, u.password, u.bio, u.birthdate, u.sexuality, u.verify, u.complete,
l.latCord, l.lngCord, l.city, p.path as path
FROM users AS u
LEFT JOIN location AS l ON u.id = l.userid
INNER JOIN photos AS p on u.id = p.userId
WHERE p.profile = 1"""
AMOUNT_PER_PAGE = 5

def get_currentUser(id):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute(userQuery + ' AND u.id=?', [id])
	user = cur.fetchone()
	con.close()
	return user

def get_wantedsexuality(sexuality, gender):
	if sexuality == 'S' or sexuality == 'G':
		if sexuality == 'S':
			wanted_sexuality = 'M' if gender == 'F' else 'F'
		else:
			wanted_sexuality = 'M' if gender == 'M' else 'F'
	else:
		wanted_sexuality = 'A'
	return wanted_sexuality

def search_users(form, gender, sexuality):
	maxdist = 2147483647
	mindist = 0
	minage = 18
	maxage = 150
	data = []
	# Do pagination
	if (form['submit'] == 'Search'):
		session['page'] = 1

	qstr = userQuery + ' AND NOT u.id=? AND NOT u.id = 1'
	data.append(session['id'])
	# Add parts at this point

	#gender
	wanted_sexuality = get_wantedsexuality(sexuality, gender)
	qstr += AddSexualPref(gender, data, wanted_sexuality, sexuality)

	#Fame Check
	if form['MinFame']:
		qstr += " AND fame >= ?"
		data.append(form['MinFame'])

	if form['MaxFame']:
		qstr += " AND fame <= ?"
		data.append(form['MaxFame'])

	#tag check
	if form.get('tags') == 'on':
		qstr += " AND u.id IN (SELECT ut.userId FROM usertags as ut WHERE ut.tagId IN (SELECT ut.tagId FROM usertags as ut WHERE ut.userId=?))"
		data.append(session['id'])

	# This Search check
	# probably needs to be patched
	if form['search']:
		qstr += " AND (UPPER(username) LIKE '%" + form['search'].upper() + "%' OR UPPER(fname) LIKE '%" + form['search'].upper() + "%' OR UPPER(lname) LIKE '%" + form['search'].upper() + "%')"

	if form['city']:
		qstr += ' AND city = ? '
		data.append(form['city'])

	qstr += ' AND complete=1'

	# Now Order 
	if form['Order']:
		if form['Order'] == "Username":
			qstr += ' ORDER BY username ASC'
		elif form['Order'] == "Fame":
			qstr += ' ORDER BY fame ASC'
		elif not (form['Order'] == 'Distance' or form['Order'] == 'Age'):
			print(form['Order'] + ' Cant be sorted by that!')

	# do the DB stuff
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	
	cur.execute(qstr, data)
	tmp = cur.fetchall()
	if not tmp:
		flash("No users were found!", "danger")
		render_template('feed.html', form=form)
		return []
	
	temp = []
	users = []
	#Max dist min dist format
	if form['MaxDist']:
		maxdist = float(form['MaxDist'])
	
	if form['MinDist']:
		mindist = float(form['MinDist'])
	
	if form['MinAge']:
		minage = int(form['MinAge'])

	if form['MaxAge']:
		maxage = int(form['MaxAge'])
	
	for user in tmp:
		user['distance'] = getdist(user['latCord'], user['lngCord'])
		
		data = user['birthdate'].split("-")
		user['age'] = get_age(date(int(data[0]), int(data[1]), int(data[2])))
		
		if (user['distance'] <= maxdist and user['distance'] >= mindist and user['age'] >= minage and user['age'] <= maxage):
			temp.append(user)

		
	# sort by distance
	if (form['Order'] == 'Distance'):
		temp = sorted(temp, key=lambda user: user['distance'])
	# sort by age
	if (form['Order'] == 'Age'):
		temp = sorted(temp, key=lambda user: user['age'])

	#for bug that Fred showed add stop
	start = (session['page'] - 1) * AMOUNT_PER_PAGE
	stop = start + AMOUNT_PER_PAGE
	if (form['submit'] == 'Next'):
		if (len(temp) >= stop):
			session['page'] += 1
	if (form['submit'] == "Previous"):
		if (session['page'] > 1):
			session['page'] -= 1
	
	start = (session['page'] - 1) * AMOUNT_PER_PAGE
	stop = start + AMOUNT_PER_PAGE
	users = (temp[start:stop])
	con.close()
	return users

def AddSexualPref(gender,data, wanted_sexuality, sexuality):
	qstr = ''
	if not wanted_sexuality == 'A':
			qstr += ' AND gender=? AND sexuality=?'
			data.append(wanted_sexuality)
			data.append(sexuality)
	else:
		if (gender == 'M'):
			qstr += " AND ((sexuality = 'B') or (sexuality = 'G' AND gender = 'M') or (sexuality = 'S' AND gender = 'F'))"
		else:
			qstr += " AND ((sexuality = 'B') or (sexuality = 'G' AND gender = 'F') or (sexuality = 'S' AND gender = 'M'))"
	return qstr

def addUserdistances(users):
	if users:
		for user in users:
			# also update user profile pictures 
			user['distance'] = getdist(user['latCord'], user['lngCord'])
	return users

def get_SuggestedUsers(sexuality, Usergender):
	# array to store all values of SQL that's getting built
	data = []
	wanted_sexuality = get_wantedsexuality(sexuality, Usergender)
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	sexualitySQL= AddSexualPref(Usergender, data, wanted_sexuality, sexuality)
	qstr = userQuery + sexualitySQL
	qstr += " AND NOT u.id = ? AND NOT u.id = 1 AND complete = 1 ORDER BY fame DESC, totalviews DESC LIMIT 0, 10"
	data.append(session['id'])
	cur.execute(qstr, data)	
	users = cur.fetchall()
	con.close()
	users = addUserdistances(users)
	return users

