from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from matcha.db import db_connect, dict_factory
from matcha.utils.general import getdist
from matcha.decorators import not_logged_in, is_logged_in, is_admin

from matcha.main.search import get_currentUser, get_SuggestedUsers, get_wantedsexuality, search_users

main = Blueprint('main', __name__,
				template_folder='./templates', static_folder='static')



@main.route('/')
@not_logged_in
def home():
	try:
		return render_template('home.html')
	except TemplateNotFound:
		abort(404)

@main.route('/admin')
@is_admin
def admin():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id IN (SELECT reportedId FROM reports)")
	reporteds = cur.fetchall()
	con.close()
	try:
		return render_template('admin.html', users=reporteds)
	except TemplateNotFound:
		abort(404)

@main.route('/ban/<reportedId>')
@is_admin
def ban_user(reportedId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("DELETE FROM reports WHERE reportedId=?", [reportedId])
	cur.execute("DELETE FROM users WHERE id=?", [reportedId])
	con.commit()
	con.close()
	try:
		flash('User has been banned!', 'success')
		return redirect(url_for('main.admin'))
	except TemplateNotFound:
		abort(404)

@main.route('/remove/<reportedId>')
@is_admin
def remove_report(reportedId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("DELETE FROM reports WHERE reportedId=?", [reportedId])
	con.commit()
	con.close()
	try:
		flash('Report has been removed!', 'success')
		return redirect(url_for('main.admin'))
	except TemplateNotFound:
		abort(404)


@main.route('/feed', methods=['GET', 'POST'])
@is_logged_in
def feed():
	#Get current user
	user = get_currentUser(session['id'])
	if user['complete'] == 1:
		if (request.method == 'POST'):
			# Do The actual Search
			users = search_users(request.form, user['gender'], user['sexuality'])
		else:
			# Get suggested users
			users = get_SuggestedUsers(user['sexuality'], user['gender'])
	else:
		flash("Please complete your profile to view the feed!", "danger")
		return render_template('feed.html', setup="Profile is not complete",form=request.form)
	
	try:
		return render_template('feed.html', users=users, form=request.form)
	except TemplateNotFound:
		abort(404)
