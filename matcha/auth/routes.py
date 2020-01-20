from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
import re
from jinja2 import TemplateNotFound
from datetime import datetime

from matcha.auth.utils import hash_password, verify_password
from matcha.decorators import not_logged_in, is_logged_in
from matcha.db import db_connect, dict_factory

from matcha.auth.email import send_email

import string
import secrets

auth = Blueprint('auth', __name__,
				 template_folder='./templates', static_folder='static')

@auth.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
	if request.method == 'POST':
		error = 0
		con = db_connect()
		cur = con.cursor()
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		uidLen = len(request.form['username'])
		if uidLen < 6 or uidLen > 20:
			flash('Username should be between 6 and 20 characters!', 'danger')
			error = 1
		if request.form['password'] != request.form['confirm']:
			flash('Passwords do not match!', 'danger')
			error = 1
		if not re.search(regex, request.form['email']):
			flash('Enter a valid email!', 'danger')
			error = 1
		if error == 0:
			uid = request.form['username'].lower()
			email = request.form['email'].lower()
			cur.execute('SELECT * FROM users WHERE username=? OR email=?', [uid, email])
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
				con.execute('INSERT INTO matches (user1, user2) VALUES (0, (SELECT id FROM users WHERE users.username = ?))', [uid])
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
				session['username'] = result['username']
				session['fname'] = result['fname']
				session['lname'] = result['lname']
				session['email'] = result['email']
				session['id'] = result['id']
				flash('Welcome back!', 'success')
				cur.execute("UPDATE users SET lastonline=? WHERE id=?", ["now", session['id']])
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
