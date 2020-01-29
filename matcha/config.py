import secrets

class Config:
	SECRET_KEY = secrets.token_urlsafe(16)
	UPLOAD_FOLDER = './photos'
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = ''
	MAIL_PASSWORD = ''
