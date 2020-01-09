from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
from jinja2 import TemplateNotFound

from matcha.decorators import is_logged_in
from matcha.db import db_connect, dict_factory

users = Blueprint('users', __name__,
				  template_folder='./templates', static_folder='static')

@users.route('/profile', defaults={'username': None})
@users.route('/profile/<username>')
@is_logged_in
def profile(username):
	if username == None:
		username = session['username']
	username = username.lower()
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute(
		"""SELECT * FROM users WHERE username=?""", [username])
	result = cur.fetchone()
	con.close()

	if result:
		try:
			if result['password']:
				del result['password']
			return render_template('profile.html', user=result, username=username)
		except TemplateNotFound:
			abort(404)
	else:
		abort(404)
