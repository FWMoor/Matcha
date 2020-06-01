from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from matcha.db import db_connect, dict_factory

from matcha.decorators import not_logged_in, is_logged_in, is_admin
from math import sin, cos, atan2, sqrt, pi

main = Blueprint('main', __name__,
				template_folder='./templates', static_folder='static')

AMOUNT_PER_PAGE = 5

@main.route('/')
@not_logged_in
def home():
	try:
		return render_template('home.html')
	except TemplateNotFound:
		abort(404)

@main.route('/admin')
@is_admin
def admin():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id IN (SELECT reportedId FROM reports)")
	reporteds = cur.fetchall()
	con.close()
	try:
		return render_template('admin.html', users=reporteds)
	except TemplateNotFound:
		abort(404)

@main.route('/ban/<reportedId>')
@is_admin
def ban_user(userId, reportedId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("DELETE FROM reports WHERE reportedId=?", [reportedId])
	cur.execute("DELETE FROM users WHERE id=?", [reportedId])
	con.commit()
	con.close()
	try:
		flash('User has been banned!', 'success')
		return redirect(url_for('main.admin'))
	except TemplateNotFound:
		abort(404)

@main.route('/remove/<reportedId>')
@is_admin
def remove_report(reportedId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("DELETE FROM reports WHERE reportedId=?", [reportedId])
	con.commit()
	con.close()
	try:
		flash('Report has been removed!', 'success')
		return redirect(url_for('main.admin'))
	except TemplateNotFound:
		abort(404)

def deg2radiant(deg):
	return deg * (pi / 180)

def getdist(lat, lng):
	lat2 = float(session['latCord'])
	lng2 = float(session['lngCord'])
	R = 6371
	dLat = deg2radiant(lat2-lat)
	dLng = deg2radiant(lng2-lng)
	a = sin(dLat/2) * sin(dLat/2) + cos(deg2radiant(lat)) * cos(deg2radiant(lat2)) * sin(dLng/2) * sin(dLng/2)
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	d = R * c
	return round(d,4)

@main.route('/feed', methods=['GET', 'POST'])
@is_logged_in
def feed():
	maxdist = 2147483647
	mindist = 0
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [session['id']])
	user = cur.fetchone()
	#get the current user :)
	if user['complete'] == 1:
		if user['sexuality'] == 'S' or user['sexuality'] == 'G':
			if user['sexuality'] == 'S':
				wanted_sexuality = 'M' if user['gender'] == 'F' else 'F'
			else:
				wanted_sexuality = 'M' if user['gender'] == 'M' else 'F'
		else:
			wanted_sexuality = 'A'
	else:
		flash("Please complete your profile to view the feed!", "danger")
		return render_template('feed.html', setup="Profile is not complete",form=request.form)

	# custom search
	if request.method == 'POST':
		# pagination
		if (request.form['submit'] == 'Search'):
			session['page'] = 1

		data = []
		SQL = 'SELECT * FROM users WHERE NOT id=? AND NOT id = 1'
		data.append(session['id'])
		
		#gender
		if not wanted_sexuality == 'A':
			SQL += ' AND gender=? AND sexuality=?'
			data.append(wanted_sexuality)
			data.append(user['sexuality'])
		else:
			if (user['gender'] == 'M'):
				SQL += " AND ((sexuality = 'B') or (sexuality = 'G' AND gender = 'M') or (sexuality = 'S' AND gender = 'F'))"
			else:
				SQL += " AND ((sexuality = 'B') or (sexuality = 'G' AND gender = 'F') or (sexuality = 'S' AND gender = 'M'))"

		if request.form['MinAge']:
			SQL += " AND age >= ?"
			data.append(request.form['MinAge'])

		if request.form['MaxAge']:
			SQL += " AND age <= ?"
			data.append(request.form['MaxAge'])

		if request.form['MinFame']:
			SQL += " AND fame >= ?"
			data.append(request.form['MinFame'])

		if request.form['MaxFame']:
			SQL += " AND fame <= ?"
			data.append(request.form['MaxFame'])

		if request.form.get('tags') == 'on':
			SQL += " AND id IN (SELECT userId FROM usertags WHERE tagId IN (SELECT tagId FROM usertags WHERE userId=?))"
			data.append(session['id'])

		if request.form['search']:
			SQL += " AND (UPPER(username) LIKE '%" + request.form['search'].upper() + "%' OR UPPER(fname) LIKE '%" + request.form['search'].upper() + "%' OR UPPER(lname) LIKE '%" + request.form['search'].upper() + "%')"

		if request.form['city']:
			SQL += ' AND city = ? '
			data.append(request.form['city'])

		SQL += ' AND complete=1'
		if request.form['Order']:
			if request.form['Order'] == "Username":
				SQL += ' ORDER BY username ASC'
			elif request.form['Order'] == "Age":
				SQL += ' ORDER BY age ASC'
			elif request.form['Order'] == "Fame":
				SQL += ' ORDER BY fame ASC'
			elif request.form['Order'] != 'Distance':
				print(request.form['Order'] + ' Cant be sorted by !')
	
		cur.execute(SQL, data)
		tmp = cur.fetchall()
		if not tmp:
			flash("No users were found!", "danger")
			return render_template('feed.html', form=request.form)
		temp = []
		users = []
		# no pagination

		if request.form['MaxDist']:
			maxdist = float(request.form['MaxDist'])
		
		if request.form['MinDist']:
			mindist = float(request.form['MinDist'])

		for user in tmp:
			user['distance'] = getdist(user['latCord'], user['lngCord'])
			if user['distance'] <= maxdist and user['distance'] >= mindist:
				temp.append(user)
			# sort by distance
		if (request.method == 'POST' and request.form['Order'] == 'Distance'):
			temp = sorted(temp, key=lambda user: user['distance'])
		
		#for bug that fred showed add stop
		start = (session['page'] - 1) * AMOUNT_PER_PAGE
		stop = start + AMOUNT_PER_PAGE
		if (request.form['submit'] == 'Next'):
			if (len(temp) >= stop):
				session['page'] += 1

		if (request.form['submit'] == "Previous"):
			if (session['page'] > 1):
				session['page'] -= 1
		# for update
		start = (session['page'] - 1) * AMOUNT_PER_PAGE
		stop = start + AMOUNT_PER_PAGE
		users = (temp[start:stop])
		con.close()


	# get Suggested users
	if request.method == 'GET':
		if (wanted_sexuality == 'A'):
			qstr = "SELECT * FROM users WHERE"
			if (user['gender'] == 'M'):
				qstr += " ((sexuality = 'B') or (sexuality = 'G' AND gender = 'M') or (sexuality = 'S' AND gender = 'F'))"
			else:
				qstr += " ((sexuality = 'B') or (sexuality = 'G' AND gender = 'F') or (sexuality = 'S' AND gender = 'M'))"
			qstr += " AND NOT id =? AND NOT id = 1 AND complete = 1 ORDER BY fame DESC LIMIT 0, 10"
			cur.execute(qstr, [session['id']])
		else:
			cur.execute('SELECT * FROM users WHERE NOT id =? AND NOT id = 1 AND gender=? AND sexuality=? AND complete = 1 ORDER BY fame  DESC, totalviews DESC LIMIT 0, 10', [session['id'], wanted_sexuality, user['sexuality']])
		users = cur.fetchall()
		con.close()
		if users:
			for user in users:
				user['distance'] = getdist(user['latCord'], user['lngCord'])
		else:
			flash("No users were found!", "danger")

	try:
		return render_template('feed.html', users=users, form=request.form)
	except TemplateNotFound:
		abort(404)
