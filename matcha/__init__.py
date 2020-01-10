from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_socketio import SocketIO
import re

socketio = SocketIO()

from matcha.decorators import not_logged_in, is_logged_in
from matcha.auth.routes import auth
from matcha.main.routes import main
from matcha.users.routes import users
from matcha.errors.handlers import errors
from matcha.db import setup_tables
from matcha.chat.routes import chat

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'dd35c1f1152a18e60a79dcafafed4b6c'
	setup_tables()

	app.register_blueprint(main)
	app.register_blueprint(errors)
	app.register_blueprint(auth, url_prefix="/auth")
	app.register_blueprint(users, url_prefix="/user")
	app.register_blueprint(chat, url_prefix="/chat")
	socketio.init_app(app)
	return app
