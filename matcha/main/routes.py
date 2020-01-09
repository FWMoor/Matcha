from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from matcha.decorators import not_logged_in, is_logged_in

main = Blueprint('main', __name__,
                 template_folder='./templates', static_folder='static')


@main.route('/')
@not_logged_in
def home():
    return render_template('home.html')


@main.route('/feed')
@is_logged_in
def feed():
    return render_template('feed.html')
