from flask import Flask, render_template, url_for, request, flash, redirect, session
import re

from config.db import db_connect, dict_factory
from utils.password import hash_password, verify_password
from utils.decorators import is_logged_in, is_admin, not_logged_in

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dd35c1f1152a18e60a79dcafafed4b6c'


@app.route('/')
@not_logged_in
def home():
	return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
	if request.method == 'POST':
		error = 0
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		uidLen = len(request.form['username'])

		con = db_connect()
		cur = con.cursor()

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
			uid = request.form['username']
			email = request.form['email']
			cur.execute("SELECT * FROM users WHERE username=? OR email=?", (uid, email))
			rows = cur.fetchall()
			if rows == 0:
				password = hash_password(request.form['password'])
				cur.execute("INSERT INTO users VALUES (null, ?, ?, ?)",
							[(uid), (email), (password)])
				con.commit()
				con.close()

				flash(f'Account for {uid} created!', 'success')
				return redirect(url_for('login'))
			else:
				flash('User already exists!', 'danger')
	return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
	if request.method == 'POST':
		error = 0
		email = request.form['email']
		password = request.form['password']
		con = db_connect()
		con.row_factory = dict_factory
		cur = con.cursor()
		cur.execute(
			"""SELECT * FROM users WHERE email=? OR username=?""", [email, email])
		result = cur.fetchone()
		con.close()

		if result:
			if not verify_password(result['password'], password):
				flash('Email or Password is wrong!', 'danger')
				error = 1
			if error == 0:
				session['logged_in'] = True
				session['username'] = result['username'].lower()
				flash('Welcome back!', 'success')
				return redirect(url_for('profile'))
		else:
			flash('User does not exist!', 'danger')
	return render_template('login.html')


@app.route('/feed')
@is_logged_in
def feed():
	return render_template('feed.html')


@app.route('/profile', defaults={'username': None})
@app.route('/profile/<username>')
@is_logged_in
def profile(username):
	return render_template('profile.html', username=username)


@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('Logout was successfull', 'success')
	return redirect(url_for('login'))


if __name__ == '__main__':
	app.run(debug=True)
