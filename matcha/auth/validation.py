from flask import flash
from matcha.db import db_connect, dict_factory
import re

def validateLogin(form):
	pass

# Return message and type and error
def validateRegistration(form):
	# Check if form completed
	if not form['fname'] or not form['lname'] or not form['username'] or not form['email'] or not form['password'] or not form['confirm']:
		flash('Fill in all fields and try again!', 'danger')
		return False
	# Now Do The Validations
	if (not ( validateName(form['fname']) and validateName(form['lname']) and validateUsername(form['username']) and validateEmail(form['email']) and validatePasswords(form['password'], form['confirm']) )):
		return False
	else:
		uid = form['username'].lower()
		email = form['email'].lower()
		return usernameavailable(uid, email)

# If not verified another user may take that spot.
def usernameavailable(uid, email):
	con = db_connect()
	cur = con.cursor()
	cur.execute('SELECT * FROM users WHERE (username=? OR email=?) AND verify=NULL', [uid, email])
	rows = cur.fetchall()
	con.close()
	
	if rows:
		flash('Username or Email is already taken!', 'danger')
		return False
	return True

def validateUsername(username):
	if len(username) < 6 or len(username) > 20:
		flash('Username should be between 6 and 20 characters!', 'danger')
		return False
	return True

# Still Need to validate a user's name and lastname
def validateName(name):
	if len(name) < 1 or len(name) > 50:
		flash('Name or lastname should be between 2 and 50 characters!', 'danger')
		return False
	return True


def validateEmail(email):
	emailregex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
	if not re.search(emailregex, email):
		flash('Enter a valid email!', 'danger')
		return False
	return True

def validatePasswords(password, confirmpassword):
	if password != confirmpassword:
		return ('Passwords do not match!', 'danger', 1)
	if validatePassword(password):
		return True
	return False

def validatePassword(password):
	error = 0
	length_regex = re.compile(r'.{6,}')
	uppercase_regex = re.compile(r'[A-Z]')
	lowercase_regex = re.compile(r'[a-z]')
	digit_regex = re.compile(r'[0-9]')
	special_regex = re.compile(r'[@#$%^&+=]')
	if not uppercase_regex.search(password):
		flash('Password needs at least 1 uppercase letter!', 'danger')
		error = 1
	if not lowercase_regex.search(password):
		flash('Password needs at least 1 lowercase letter!', 'danger')
		error = 1
	if not digit_regex.search(password):
		flash('Password needs at least 1 number!', 'danger')
		error = 1
	if not special_regex.search(password):
		flash('Password needs at least 1 special character!', 'danger')
		error = 1
	if not length_regex.search(password):
		flash('Password needs to be at least 6 characters long!', 'danger')
		error = 1
	return (error == 0)
