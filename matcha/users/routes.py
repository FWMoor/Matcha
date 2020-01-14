from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
from jinja2 import TemplateNotFound

from matcha.auth.utils import hash_password
from matcha.decorators import is_logged_in
from matcha.db import db_connect, dict_factory

users = Blueprint('users', __name__,
				  template_folder='./templates', static_folder='../static')

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
	cur.execute("SELECT * FROM users WHERE username=?", [username])
	result = cur.fetchone()
	if result:
		cur.execute("SELECT * FROM photos WHERE userId=?", [result['id']])
		pics = cur.fetchall()
		cur.execute("SELECT * FROM photos WHERE userId=? AND profile=1", [result['id']])
		profile = cur.fetchone()
		con.close()
		image = profile.path if profile != None else 'default.jpeg'
		image_file = url_for('static', filename='photos/' + image)
		try:
			if result['password']:
				del result['password']
			return render_template('profile.html', user=result, username=username, profile=image_file, pics=pics, amount=len(pics))
		except TemplateNotFound:
			abort(404)
	else:
		abort(404)

@users.route('/profile/edit', methods=['GET', 'POST'])
@is_logged_in
def edit():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	if request.method == 'POST':
		notif = 1 if request.form.get('notifications') else 0
		cur.execute("SELECT * FROM users WHERE (username=? OR email=?) AND NOT id=?", [request.form.get('username'), request.form.get('email'), session['id']])
		results = cur.fetchall()
		if results:
			flash('Username or email already in use!', 'danger')
			return redirect(url_for('users.edit'))
		else:
			cur.execute("UPDATE users SET fname=?, lname=?, username=?, email=?, bio=?, notifications=? WHERE id=?", [request.form.get('fname'), request.form.get('lname'), request.form.get('username'), request.form.get('email'), request.form.get('bio'), notif, session['id']])
			con.commit()
			con.close()
			session['username'] = request.form.get('username')
			session['fname'] = request.form.get('fname')
			session['lname'] = request.form.get('lname')
			session['email'] = request.form.get('email')
			try:
				flash('Profile was updated!', 'success')
				return redirect(url_for('users.profile', username=request.form.get('username')))
			except TemplateNotFound:
				abort(404)
	else:
		username = session['username'].lower()
		cur.execute("SELECT * FROM users WHERE username=?", [username])
		result = cur.fetchone()
		con.close()
		if result:
			try:
				return render_template('edit.html', user=result)
			except TemplateNotFound:
				abort(404)
		else:
			abort(404)

@users.route('/profile/password', methods=['GET', 'POST'])
@is_logged_in
def password():
	if request.method == 'POST':
		password = request.form.get('password')
		confirm = request.form.get('confirm')
		if (password == confirm):
			password = hash_password(password)
			con = db_connect()
			cur = con.cursor()
			cur.execute("UPDATE users SET password=? WHERE id=?", [password, session['id']])
			con.commit()
			con.close()
			try:
				flash('Password was updated!', 'success')
				return redirect(url_for('users.profile', username=request.form.get('username')))
			except TemplateNotFound:
				abort(404)
		else:
			flash('Password don\'t match!', 'danger')
			return redirect(url_for('users.password'))
	else:
		try:
			return render_template('password.html')
		except TemplateNotFound:
			abort(404)
