import secrets
import os

class Config:
	""" Please Run these exports prior to starting the application.
		Ensure to always have your email and password setup Correctly.
		If your email doesn't work (with gmail) please allow access to less secure applications

		configuration that needs changes:

		MAIL_USERNAME
		MAIL_PASSWORD
		SECRET_KEY (Optional but preffered for security)
	"""

	
	MAIL_USERNAME="projectmatcha60@gmail.com"
	MAIL_PASSWORD=""
	SECRET_KEY="secrets.token_urlsafe(16)"
	UPLOAD_FOLDER="./photos"
	MAIL_SERVER="smtp.gmail.com"
	MAIL_PORT=465
	MAIL_USE_SSL=True
	SESSION_COOKIE_SAMESITE="Lax"
	
	# SECRET_KEY = os.environ.get('SECRET_KEY')
	# UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
	# MAIL_SERVER = os.environ.get('MAIL_SERVER')
	# MAIL_PORT = os.environ.get('MAIL_PORT')
	# MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
	# MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	# MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	# SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE')
