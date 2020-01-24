from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from matcha.db import db_connect, dict_factory

from matcha.decorators import not_logged_in, is_logged_in, is_admin

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

@main.route('/feed', methods=['GET', 'POST'])
@is_logged_in
def feed():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [session['id']])
	user = cur.fetchone()
	if request.method == 'POST':
		minage = request.form['min-age'] if request.form['min-age'] else '0'
		maxage = request.form['max-age'] if request.form['max-age'] else '412414'
		minfame = request.form['min-fame'] if request.form['min-fame'] else '0'
		maxfame = request.form['max-fame'] if request.form['max-fame'] else '5'
		if user['gender'] and (user['gender'] == 'M' or user['gender'] == 'F'):
			if user['sexuality'] == 'S' or user['sexuality'] == 'G':
				if user['sexuality'] == 'S':
					wanted_sexuality = 'M' if user['gender'] == 'F' else 'F'
				else:
					wanted_sexuality = 'M' if user['gender'] == 'M' else 'F'
				if request.form.get('tags') == 'on':
					cur.execute("SELECT * FROM users WHERE id IN (SELECT userId FROM usertags WHERE tagId IN (SELECT tagId FROM usertags WHERE userId=?)) AND NOT id=? AND (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND (fame >= " + minfame + " AND fame <= " + maxfame + ") AND NOT UPPER(username)='SYSTEM' AND gender=? AND sexuality=? AND complete=1", [session['id'], session['id'], wanted_sexuality, user['sexuality']])
				else:
					cur.execute("SELECT * FROM users WHERE (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND (fame >= " + minfame + " AND fame <= " + maxfame + ") AND NOT UPPER(username)='SYSTEM' AND gender=? AND sexuality=?", [wanted_sexuality, user['sexuality']])
			else:
				if request.form.get('tags') == 'on':
					cur.execute("SELECT * FROM users WHERE id IN (SELECT userId FROM usertags WHERE tagId IN (SELECT tagId FROM usertags WHERE userId=?)) AND NOT id=? AND (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND (fame >= " + minfame + " AND fame <= " + maxfame + ") AND NOT UPPER(username)='SYSTEM' AND (gender=? OR gender=?) AND complete=1", [session['id'], session['id'], 'M', 'F'])
				else:
					cur.execute("SELECT * FROM users WHERE (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND (fame >= " + minfame + " AND fame <= " + maxfame + ") AND NOT UPPER(username)='SYSTEM' AND (gender=? OR gender=?)", ['F', 'M'])
		else:
			if request.form.get('tags') == 'on':
				cur.execute("SELECT * FROM users WHERE id IN (SELECT userId FROM usertags WHERE tagId IN (SELECT tagId FROM usertags WHERE userId=?)) AND NOT id=? AND (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND (fame >= " + minfame + " AND fame <= " + maxfame + ") AND NOT UPPER(username)='SYSTEM' AND complete=1", [session['id'], session['id']])
			else:
				cur.execute("SELECT * FROM users WHERE (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND (fame >= " + minfame + " AND fame <= " + maxfame + ") AND NOT UPPER(username)='SYSTEM' AND complete=1")
	else:
		if user['gender'] and (user['gender'] == 'M' or user['gender'] == 'F'):
			if user['sexuality'] == 'S' or user['sexuality'] == 'G':
				if user['sexuality'] == 'S':
					wanted_sexuality = 'M' if user['gender'] == 'F' else 'F'
				else:
					wanted_sexuality = 'M' if user['gender'] == 'M' else 'F'
				cur.execute("SELECT * FROM users WHERE NOT id=? AND gender=? AND sexuality=? AND NOT UPPER(username)=? AND complete=1", [session['id'], wanted_sexuality, user['sexuality'], 'SYSTEM'])
			else:
				cur.execute("SELECT * FROM users WHERE NOT id=? AND (gender=? OR gender=?) AND NOT UPPER(username)=? AND complete=1", [session['id'], 'M', 'F', 'SYSTEM'])
		else:
			cur.execute("SELECT * FROM users WHERE NOT id=? AND NOT UPPER(username)=? AND complete=1", [session['id'], 'SYSTEM'])
	users = cur.fetchall()
	con.close()
	try:
		return render_template('feed.html', users=users)
	except TemplateNotFound:
		abort(404)
