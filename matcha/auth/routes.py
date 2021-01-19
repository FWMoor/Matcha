from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort, escape
import re
from jinja2 import TemplateNotFound
from datetime import datetime, date

from matcha.utils.general import get_age
from matcha.auth.utils import hash_password, verify_password
from matcha.utils.decorators import not_logged_in, is_logged_in, is_admin_or_logged_in
from matcha.db import db_connect, dict_factory
from matcha.chat.routes import getsystemmessages, getmessagecount
from matcha.auth.email import send_email
from matcha.auth.validation import validateRegistration, validatePasswords

import string
import secrets

auth = Blueprint('auth', __name__,
				 template_folder='./templates', static_folder='static')

@auth.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
	if request.method == 'POST':
		if validateRegistration(request.form):
			# Do Actual Registration
			uid = request.form['username'].lower()
			fname = escape(request.form['fname'])
			lname = escape(request.form['lname'])
			email = request.form['email'].lower()
			password = hash_password(request.form['password'])
			alphabet = string.ascii_letters + string.digits
			#Create and send the email
			token = ''.join(secrets.choice(alphabet) for i in range(8))
			confirm_url = url_for('auth.confirm_email', token=token, _external=True)
			html = render_template('activate.html', confirm_url=confirm_url)
			subject = "Please confirm your email"
			send_email(email, subject, html)

			#Add the user to the DB
			con = db_connect()
			cur = con.cursor()
			cur.execute('INSERT INTO users (fname, lname, username, email, password, verify) VALUES (?, ?, ?, ?, ?, ?)', [fname, lname, uid, email, password, token])
			cur.execute('INSERT INTO matches (user1, user2) VALUES (1, (SELECT id FROM users WHERE users.username = ? ))', [uid] )
			con.commit()
			con.close()
			flash('Verification Email Sent!', 'success')
			return redirect(url_for('auth.login'))
	# IRRESPECTIVE RENDER DATA OUT
	try:
		return render_template('register.html')
	except TemplateNotFound:
		abort(404)

@auth.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
	if request.method == 'POST':
		error = 0
		email = request.form['email'].lower()
		password = request.form['password']
		con = db_connect()
		con.row_factory = dict_factory
		cur = con.cursor()
		cur.execute("""
		SELECT
		u.fname, u.lname, u.email, u.id, u.username, u.gender, u.password, u.bio, u.birthdate, u.sexuality, u.verify,
		l.latCord, l.lngCord, l.city,
		COUNT(p.profile) AS profileset
		FROM
			users AS u
		LEFT JOIN location AS l ON u.id = l.userid
		LEFT JOIN photos AS p ON u.id = p.userId
		WHERE (u.username=? or u.email=?)
		GROUP BY u.id""", [email, email])

		result = cur.fetchone()
		if result:
			if result['verify']:
				flash('Account not verified!', 'danger')
				error = 1
			if not verify_password(result['password'], password):
				flash('Email or Password is wrong!', 'danger')
				error = 1
			if error == 0:
				# SET SESSION DATA
				session['logged_in'] = True
				if result['username'] == 'system':
					session['is_admin'] = True
				session['username'] = result['username']
				session['fname'] = result['fname']
				session['lname'] = result['lname']
				session['email'] = result['email']
				session['id'] = result['id']
				session['sysnotif'] = getsystemmessages(result['id'])
				session['sysmsgcnt'] = getmessagecount(result['id'], True)
				session['msgcnt'] = getmessagecount(result['id'])

				if (result['latCord'] and result['lngCord'] and result['city']):
					session['latCord'] = result['latCord']
					session['lngCord'] = result['lngCord']
					session['city'] = result['city']
				else:
					session['latCord'] = 0
					session['lngCord'] = 0
				flash('Welcome back!', 'success')
				cur.execute("UPDATE users SET lastonline=? WHERE id=?", ["now", session['id']])
				cur.execute("UPDATE users SET passreset=? WHERE id=?", [None, result['id']])
				if result['birthdate']:
					data = result['birthdate'].split("-")
					age = get_age(date(int(data[0]), int(data[1]), int(data[2])))
				con.commit()
				if result['fname'] and result['lname'] and result['username'] and result['email'] and result['gender'] and age and result['sexuality'] and result['bio'] and result['profileset'] > 0:
					cur.execute("UPDATE users SET complete=? WHERE id=?", [1, session['id']])
				else:
					cur.execute("UPDATE users SET complete=? WHERE id=?", [0, session['id']])
				con.commit()
				con.close()
				return redirect(url_for('users.profile'))
		else:
			flash('Username or Email not found.', 'danger')
			con.close()
			return redirect(url_for('auth.login'))
	try:
		return render_template('login.html')
	except TemplateNotFound:
		abort(404)


@auth.route('/logout')
@is_admin_or_logged_in
def logout():
	con = db_connect()
	cur = con.cursor()
	date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
	cur.execute("UPDATE users SET lastonline=? WHERE id=?", [date_time, session['id']])
	con.commit()
	con.close()
	session.clear()
	flash('Logout was successfull', 'success')
	return redirect(url_for('auth.login'))

@auth.route('/confirm/<token>')
@not_logged_in
def confirm_email(token):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute('SELECT * FROM users WHERE verify=?', [token])
	user = cur.fetchone()
	con.close()
	if user:
		email = user['email']
		con = db_connect()
		con.row_factory = dict_factory
		cur = con.cursor()
		cur.execute('UPDATE users SET verify=? WHERE email=?',
					[None, email])
		con.commit()
		con.close()
		flash('You have confirmed your account. Thanks!', 'success')
	else:
		flash('The confirmation link is invalid or has expired.', 'danger')
	return redirect(url_for('auth.login'))

@auth.route('/reset/<token>', methods=['GET', 'POST'])
@not_logged_in
def reset_password(token):
	if request.method == 'POST':

		# ======================== Replace with Validate passwords =================
		length_regex = re.compile(r'.{6,}')
		uppercase_regex = re.compile(r'[A-Z]')
		lowercase_regex = re.compile(r'[a-z]')
		digit_regex = re.compile(r'[0-9]')
		special_regex = re.compile(r'[@#$%^&+=]')
		error = 0
		if not request.form.get('password') or not request.form.get('confirm'):
			flash('Enter all fields and try again!', 'danger')
			return redirect(url_for('auth.reset_password', token=token)) 
		if request.form.get('password') == request.form.get('confirm'):
			if not uppercase_regex.search(request.form.get('password')):
				flash('Password needs at least 1 uppercase letter!', 'danger')
				error = 1
			if not lowercase_regex.search(request.form['password']):
				flash('Password needs at least 1 lowercase letter!', 'danger')
				error = 1
			if not digit_regex.search(request.form['password']):
				flash('Password needs at least 1 number!', 'danger')
				error = 1
			if not special_regex.search(request.form['password']):
				flash('Password needs at least 1 special character!', 'danger')
				error = 1
			if not length_regex.search(request.form['password']):
				flash('Password needs to be at least 6 characters long!', 'danger')
				error = 1
			if error == 1:
				return redirect(url_for('auth.reset_password', token=token))
			else:
				con = db_connect()
				con.row_factory = dict_factory
				cur = con.cursor()
				cur.execute('SELECT * FROM users WHERE passreset=?', [token])
				user = cur.fetchone()
				con.close()
				if user:
					email = user['email']
					con = db_connect()
					con.row_factory = dict_factory
					cur = con.cursor()
					password = hash_password(request.form.get('password'))
					cur.execute('UPDATE users SET passreset=?, password=? WHERE email=?',
								[None, password, email])
					con.commit()
					con.close()
					flash('You have reset your password. Thanks!', 'success')
				else:
					flash('The confirmation link is invalid or has expired.', 'danger')
				return redirect(url_for('auth.login'))
		else:
			flash('Passwords do not match', 'danger')
			return redirect(url_for('auth.reset_password', token=token))
	try:
		return render_template('newpass.html')
	except TemplateNotFound:
		abort(404)

@auth.route('/forget', methods=['GET', 'POST'])
@not_logged_in
def forget():
	if request.method == 'POST':
		email = request.form['email'].lower()
		alphabet = string.ascii_letters + string.digits
		token = ''.join(secrets.choice(alphabet) for i in range(8))
		reset_url = url_for('auth.reset_password', token=token, _external=True)
		html = render_template('reset.html', reset_url=reset_url)
		subject = "Reset password"
		send_email(email, subject, html)
		con = db_connect()
		cur = con.cursor()
		cur.execute("UPDATE users SET passreset=? WHERE email=?", [token, email])
		con.commit()
		con.close()
		flash("Reset email has been sent!", "success")
		return redirect(url_for('auth.login'))
	try:
		return render_template('forget.html')
	except TemplateNotFound:
		abort(404)
