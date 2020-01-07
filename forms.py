from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
# import re

class RegistrationForm(FlaskForm):
	username = StringField('Username')
	email = StringField('Email')
	password = PasswordField('Password')
	confirm = PasswordField('Confirm')
	submit = SubmitField('Sign Up')

	def length(username):
		if len(username.data) > 20 and len(username.data) < 2:
			raise ValidationError('Username must be between 2 and 20 characters long!')
	
	def email(email):
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		if not (re.search(regex, email)):
			raise ValidationError('Email is not a valid email address')
	
	def match(password, confirm):
		if (password != confirm):
			raise ValidationError('Passwords don\'t match')

class LoginForm(FlaskForm):
	email = StringField('Email')
	password = PasswordField('Password')
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

	def email(email):
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		if not (re.search(regex, email)):
			raise ValidationError('Email is not a valid email address')

