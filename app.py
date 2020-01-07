from flask import Flask, render_template, url_for, request, flash, redirect, g
import sqlite3
import re
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dd35c1f1152a18e60a79dcafafed4b6c'

import os
import sqlite3

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'site.db')

def db_connect(db_path=DEFAULT_PATH):
	con = sqlite3.connect(db_path)
	return con

con = db_connect()
cur = con.cursor()
users_sql = """
CREATE TABLE users (
	id integer PRIMARY KEY,
	username text NOT NULL,
	email text NOT NULL,
	password text NOT NULL
)"""
cur.execute(users_sql)

post = [
	{
		'user': 'John Smith',
		'age': 24
	},
	{
		'user': 'John Smit',
		'age': 25
	}
]

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html', posts=post)

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/register', methods = ['GET', 'POST'])
def register():
	if request.method == 'POST':
		error = 0
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
			uid = request.form['username']
			flash(f'Account for {uid} created!', 'success')
			return redirect(url_for('home'))
	return render_template('register.html', title='Register')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		error = 0
		if error == 0:
			flash('Welcome back!', 'success')
			return redirect(url_for('home'))
	return render_template('login.html', title='Login')

if __name__ == '__main__':
	app.run(debug=True)
