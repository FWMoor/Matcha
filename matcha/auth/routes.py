from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
import re
from jinja2 import TemplateNotFound
from datetime import datetime, date

from matcha.auth.utils import hash_password, verify_password
from matcha.decorators import not_logged_in, is_logged_in
from matcha.db import db_connect, dict_factory

from matcha.auth.email import send_email

import string
import secrets

auth = Blueprint('auth', __name__,
				 template_folder='./templates', static_folder='static')

def get_age(birthDate):
	today = date.today()
	age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
	return age

@auth.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
	if request.method == 'POST':
		error = 0
		con = db_connect()
		cur = con.cursor()
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		uidLen = len(request.form['username'])
		length_regex = re.compile(r'.{6,}')
		uppercase_regex = re.compile(r'[A-Z]')
		lowercase_regex = re.compile(r'[a-z]')
		digit_regex = re.compile(r'[0-9]')
		special_regex = re.compile(r'[@#$%^&+=]')
		if not request.form['fname'] or not request.form['lname'] or not request.form['username'] or not request.form['email'] or not request.form['password'] or not request.form['confirm']:
			flash('Fill in all fields and try again!', 'danger')
		if uidLen < 6 or uidLen > 20:
			flash('Username should be between 6 and 20 characters!', 'danger')
			error = 1
		if request.form['password'] != request.form['confirm']:
			flash('Passwords do not match!', 'danger')
			error = 1
		if not re.search(regex, request.form['email']):
			flash('Enter a valid email!', 'danger')
			error = 1
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
		if error == 0:
			uid = request.form['username'].lower()
			email = request.form['email'].lower()
			cur.execute('SELECT * FROM users WHERE (username=? OR email=?) AND verify=?', [uid, email, None])
			rows = cur.fetchall()
			if not rows:
				fname = request.form['fname']
				lname = request.form['lname']
				password = hash_password(request.form['password'])
				alphabet = string.ascii_letters + string.digits
				token = ''.join(secrets.choice(alphabet) for i in range(8))
				confirm_url = url_for(
					'auth.confirm_email', token=token, _external=True)
				html = render_template(
					'activate.html', confirm_url=confirm_url)
				subject = "Please confirm your email"
				send_email(email, subject, html)
				cur.execute('INSERT INTO users (fname, lname, username, email, password, verify) VALUES (?, ?, ?, ?, ?, ?)', [(fname), (lname), (uid), (email), (password), (token)])
				con.execute('INSERT INTO matches (user1, user2) VALUES (1, (SELECT id FROM users WHERE users.username = ?))', [uid])
				con.commit()
				con.close()
				flash('Verification Email Sent!', 'success')
				return redirect(url_for('auth.login'))
			else:
				flash('Username or Email is already taken!', 'danger')
				return redirect(url_for('auth.register'))
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
		cur.execute('SELECT * FROM users WHERE email=? OR username=?', [email, email])
		result = cur.fetchone()
		if result:
			if result['verify']:
				flash('Account not verified!', 'danger')
				error = 1
			if not verify_password(result['password'], password):
				flash('Email or Password is wrong!', 'danger')
				error = 1
			if error == 0:
				session['logged_in'] = True
				if result['username'] == 'system':
					session['is_admin'] = True
				session['username'] = result['username']
				session['fname'] = result['fname']
				session['lname'] = result['lname']
				session['email'] = result['email']
				session['id'] = result['id']
				flash('Welcome back!', 'success')
				cur.execute("UPDATE users SET lastonline=? WHERE id=?", ["now", session['id']])
				cur.execute("UPDATE users SET passreset=? WHERE id=?", [None, result['id']])
				if result['birthdate']:
					data = result['birthdate'].split("-")
					age = get_age(date(int(data[0]), int(data[1]), int(data[2])))
					cur.execute("UPDATE users SET age=? WHERE id=?", [age, result['id']])
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
@is_logged_in
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
