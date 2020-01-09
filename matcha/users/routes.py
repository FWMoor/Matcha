from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
from jinja2 import TemplateNotFound

from matcha.decorators import is_logged_in

users = Blueprint('users', __name__,
                  template_folder='./templates', static_folder='static')


@users.route('/profile', defaults={'username': None})
@users.route('/profile/<username>')
@is_logged_in
def profile(username):
    return render_template('profile.html', username=username)
