from flask import url_for, flash, redirect, session
from functools import wraps

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('auth.login'))
	return wrap

def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'is_admin' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('auth.login'))
	return wrap

def not_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return redirect(url_for('main.feed'))
		else:
			return f(*args, **kwargs)
	return wrap
