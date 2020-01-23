from flask import Blueprint, render_template, abort, session, request
from jinja2 import TemplateNotFound
from matcha.db import db_connect, dict_factory

from matcha.decorators import not_logged_in, is_logged_in

main = Blueprint('main', __name__,
				 template_folder='./templates', static_folder='static')

@main.route('/')
@not_logged_in
def home():
	try:
		return render_template('home.html')
	except TemplateNotFound:
		abort(404)

@main.route('/feed', methods=['GET', 'POST'])
@is_logged_in
def feed():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	if request.method == 'POST':
		minage = request.form['min-age'] if request.form['min-age'] else '0'
		maxage = request.form['max-age'] if request.form['max-age'] else '412414'
		if request.form.get('tags') == 'on':
			cur.execute("SELECT * FROM users WHERE id IN (SELECT userId FROM usertags WHERE tagId IN (SELECT tagId FROM usertags WHERE userId=?)) AND NOT id=? AND (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND NOT UPPER(username)='SYSTEM'", [session['id'], session['id']])
			users = cur.fetchall()
		else:
			cur.execute("SELECT * FROM users WHERE (username LIKE '%" + request.form['search'] + "%' OR fname LIKE '%" + request.form['search'] + "%' OR lname LIKE '%" + request.form['search'] + "%') AND (age >= " + minage + " AND age <= " + maxage + ") AND NOT UPPER(username)='SYSTEM'")
			users = cur.fetchall()
	else:
		cur.execute("SELECT * FROM users WHERE id=?", [session['id']])
		user = cur.fetchone()
		if user['gender'] and (user['gender'] == 'M' or user['gender'] == 'F'):
			if user['sexuality'] == 'S' or user['sexuality'] == 'G':
				if user['sexuality'] == 'S':
					wanted_sexuality = 'M' if user['gender'] == 'F' else 'F'
				else:
					wanted_sexuality = 'M' if user['gender'] == 'M' else 'F'
				cur.execute("SELECT * FROM users WHERE NOT id=? AND gender=? AND sexuality=?", [session['id'], wanted_sexuality, user['sexuality']])
			else:
				cur.execute("SELECT * FROM users WHERE NOT id=? AND (gender=? OR gender=?)", [session['id'], 'M', 'F'])
		else:
			cur.execute("SELECT * FROM users WHERE NOT id=? AND NOT UPPER(username)=?", [session['id'], 'SYSTEM'])
		users = cur.fetchall()
	cur.close()
	try:
		return render_template('feed.html', users=users)
	except TemplateNotFound:
		abort(404)
