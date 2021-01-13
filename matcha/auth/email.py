from flask_mail import Message
from matcha import mail
import os

def send_email(to, subject, template):
	msg = Message(
		subject,
		recipients=[to],
		html=template,
		sender= os.environ.get('MAIL_USERNAME')
	)
	mail.send(msg)
