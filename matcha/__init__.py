from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_socketio import SocketIO
from flask_mail import Mail
from matcha.config import Config
import re

socketio = SocketIO()
mail = Mail()

from matcha.decorators import not_logged_in, is_logged_in, is_admin, is_admin_or_logged_in
from matcha.auth.routes import auth
from matcha.main.routes import main
from matcha.users.routes import users
from matcha.errors.handlers import errors
from matcha.db import setup_tables
from matcha.chat.routes import chat
import sys


def create_app():
	app = Flask(__name__)
	sys.dont_write_bytecode = True	
	app.config.from_object(Config)

	socketio.init_app(app)
	mail.init_app(app)

	setup_tables()

	app.register_blueprint(main)
	app.register_blueprint(errors)
	app.register_blueprint(auth, url_prefix="/auth")
	app.register_blueprint(users, url_prefix="/user")
	app.register_blueprint(chat, url_prefix="/chat")

	return app
