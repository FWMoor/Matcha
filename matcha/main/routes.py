from flask import Blueprint, render_template, abort, session
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

@main.route('/feed')
@is_logged_in
def feed():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [session['id']])
	user = cur.fetchone()
	if user['gender'] and (user['gender'] == 'M' or user['gender'] == 'F'):
		print(user)
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
