from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from matcha.decorators import not_logged_in, is_logged_in
from matcha.db import db_connect, dict_factory

main = Blueprint('main', __name__,
				 template_folder='./templates', static_folder='static')

@main.route('/')
@not_logged_in
def home():
	try:
		return render_template('home.html')
	except TemplateNotFound:
		abort(404)

@main.route('/feed')
@is_logged_in
def feed():
	try:
		con = db_connect()
		con.row_factory = dict_factory
		cur = con.cursor()
		cur.execute("SELECT * FROM users")
		rows = cur.fetchall()
		cur.close()
		return render_template('feed.html', users = rows)
	except TemplateNotFound:
		abort(404)
