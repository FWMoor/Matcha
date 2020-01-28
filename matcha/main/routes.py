from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from matcha.db import db_connect, dict_factory

from matcha.decorators import not_logged_in, is_logged_in, is_admin
from math import sin, cos, atan2, sqrt, pi
main = Blueprint('main', __name__,
				template_folder='./templates', static_folder='static')

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
def remove_report(userId, reportedId):
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
	users = []
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [session['id']])
	user = cur.fetchone()
	#get the current user :)
	if user['gender'] and (user['gender'] == 'M' or user['gender'] == 'F'):
		if user['sexuality'] == 'S' or user['sexuality'] == 'G':
			if user['sexuality'] == 'S':
				wanted_sexuality = 'M' if user['gender'] == 'F' else 'F'
			else:
				wanted_sexuality = 'M' if user['gender'] == 'M' else 'F'
	else:
		return render_template('feed.html', setup="Please complete your profile get your match")

	# get Suggested users
	if request.method == 'GET':
		cur.execute('SELECT * FROM users WHERE NOT id =? AND NOT id = 1', [session['id']])
		tmp = cur.fetchall()

	# custom search
	if request.method == 'POST':
		# if user is all setup
		data = []
		SQL = 'SELECT * FROM users WHERE NOT id=? AND NOT id = 1'
		data.append(session['id'])
		
		#gender
		SQL += ' AND gender=? AND sexuality=?'
		data.append(wanted_sexuality)
		data.append(user['sexuality'])

		if request.form['min-age']:
			SQL += " AND age >= ?"
			data.append(request.form['min-age'])

		if request.form['max-age']:
			SQL += " AND age <= ?"
			data.append(request.form['max-age'])

		if request.form['min-fame']:
			SQL += " AND fame >= ?"
			data.append(request.form['min-fame'])

		if request.form['max-fame']:
			SQL += " AND fame <= ?"
			data.append(request.form['max-fame'])

		if request.form.get('tags') == 'on':
			SQL += " AND id IN (SELECT userId FROM usertags WHERE tagId IN (SELECT tagId FROM usertags WHERE userId=?))"
			data.append(session['id'])

		if request.form['search']:
			SQL += " AND (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%')"
		
		# SQL += ' AND complete=1'
		cur.execute(SQL, data)
		tmp = cur.fetchall()

		con.close()

		if request.form['max-dist']:
			maxdist = float(request.form['max-dist'])
		
		if request.form['min-dist']:
			mindist = float(request.form['min-dist'])

	for user in tmp:
		user['distance'] = getdist(user['latCord'], user['lngCord'])
		if user['distance'] <= maxdist and user['distance'] >= mindist:
			users.append(user)
	
	try:
		return render_template('feed.html', users=users)
	except TemplateNotFound:
		abort(404)
