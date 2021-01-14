from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
from jinja2 import TemplateNotFound
from datetime import date 

import secrets
import os

#For sys notifications
from matcha.chat.routes import sysmsg

from matcha.utils.general import get_age
from matcha.auth.utils import hash_password
from matcha.decorators import is_logged_in, is_admin_or_logged_in
from matcha.db import db_connect, dict_factory

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

users = Blueprint('users', __name__,
				  template_folder='./templates', static_folder='../static')

def update_fame_rating(id):
	total = getprofileviews(id)
	con = db_connect()
	cur = con.cursor()
	cur.execute("SELECT * FROM likes WHERE user2=?", [id])
	like = cur.fetchall()
	likes = len(like)
	cur.execute("SELECT * FROM matches WHERE (user2=? OR user1=?) AND NOT (user1=1 OR user2=1)", [id, id])
	match = cur.fetchall()
	matches = len(match)
	if (total > 0):
		fame = (likes + matches) / total * 5
	else:
		fame = 0
	cur.execute("UPDATE users SET fame=? WHERE id=?", [round(fame, 1), id])
	con.commit()
	con.close()
	return round(fame, 1)

def get_id_from_username(username):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE username=?", [username])
	user = cur.fetchone()
	con.close()
	return user['username']

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	if (f_ext in ALLOWED_EXTENSIONS):
		picture_fn = str(session['id']) + "." + random_hex + f_ext
		picture_path = os.path.join('matcha/static/photos', picture_fn)
		form_picture.save(picture_path)
		return picture_fn
	else:
		flash('Unsupported extention type!', 'danger')
		return 'Empty'

def getprofileviews(id):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT viewee as count FROM views WHERE viewer=? AND NOT viewer=1", [id])
	result = cur.fetchall()
	con.close()
	return len(result)

def addprofileviews(id):
	views = getprofileviews(id) + 1
	con = db_connect()
	cur = con.cursor()
	cur.execute(
	"""UPDATE users SET totalviews = ?
		WHERE id = ?""",
		[views, id])
	con.commit()
	con.close()

@users.route('/profile', defaults={'username': None}, methods=['GET', 'POST'])
@users.route('/profile/<username>', methods=['GET', 'POST'])
@is_admin_or_logged_in
def profile(username):
	if username == None:
		username = session['username']
	username = username.lower()
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE username=?", [username])
	result = cur.fetchone()
	if result:
		if username != session['username']:
			cur.execute("SELECT * FROM blocked WHERE userId=? AND blockedId=?", [result['id'], session['id']])
			isblocked = cur.fetchone()
			if isblocked:
				abort(404)
			else:
				cur.execute("SELECT * FROM views WHERE viewee=? AND viewer=?", [result['id'], session['id']])
				view = cur.fetchone()
				if not view:
					cur.execute("INSERT INTO views (viewer, viewee) VALUES(?, ?)", [result['id'], session['id']]) #might not be right lol
					con.commit()
		if request.method == 'POST':
			cur.execute("SELECT * FROM photos WHERE userId=?", [result['id']])
			tot = cur.fetchall()
			if len(tot) < 5:
				picture_file = save_picture(request.files['picture'])
				if picture_file != 'Empty':
					cur.execute("SELECT * FROM photos WHERE userId=?", [result['id']])
					pics = cur.fetchall()
					if not pics:
						cur.execute("INSERT INTO photos (userId, path, profile) VALUES (?, ?, 1)", [session['id'], picture_file])
					else:
						cur.execute("INSERT INTO photos (userId, path) VALUES (?, ?)", [session['id'], picture_file])
					con.commit()
		cur.execute("SELECT * FROM photos WHERE userId=? ORDER BY profile DESC", [result['id']])
		pics = cur.fetchall()
		# Fix this please 
		profile = pics[0] if pics != [] else None
		cur.execute("SELECT * FROM tags WHERE id IN (SELECT tagId FROM usertags WHERE userId=?)", [result['id']])
		tags = cur.fetchall()
		cur.execute("""
		SELECT
		u.fname, u.lname, u.email, u.id, u.username, u.gender, u.password, u.bio, u.birthdate, u.sexuality, u.verify,
		COUNT(p.profile) AS profileset
		FROM
			users AS u
		LEFT JOIN photos AS p ON u.id = p.userId
		WHERE u.id=?
		GROUP BY u.id
		""", [session['id']])
		complete = cur.fetchone()
		if complete['fname'] and complete['lname'] and complete['username'] and complete['email'] and complete['gender'] and complete['birthdate'] and complete['sexuality'] and complete['bio'] and complete['profileset'] > 0:
			cur.execute("UPDATE users SET complete=? WHERE id=?", [1, complete['id']])
		else:
			cur.execute("UPDATE users SET complete=? WHERE id=?", [0, complete['id']])
		con.commit()
		blocked = 0
		liked = 0
		matched = 0
		if (username != session['username']):
			cur.execute("SELECT * FROM blocked WHERE userId=? AND blockedId=?", [session['id'], result['id']])
			block = cur.fetchone()
			blocked = 1 if block != None else 0
			cur.execute("SELECT * FROM matches WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", [session['id'], result['id'], result['id'], session['id']])
			match = cur.fetchone()
			if match:
				matched = 1
			else:
				cur.execute("SELECT * FROM likes WHERE user1=? AND user2=?", [session['id'], result['id']])
				like = cur.fetchone()
				liked = 1 if like != None else 0
		con.close()
		#update profile views
		# referrer = request.referrer
		if (username != session['username']):
			data = {'id': result['id'], "message":session['username'] + " viewed your profile"}
			sysmsg(data)
			addprofileviews(result['id'])
		image = profile['path'] if profile != None else 'default.jpeg'
		image_file = url_for('static', filename='photos/' + image)
		try:
			if result['password']:
				del result['password']
			if result['birthdate']:
				data = result['birthdate'].split("-")
				age = get_age(date(int(data[0]), int(data[1]), int(data[2])))
			else:
				age = 0
			return render_template('profile.html', user=result, fame=update_fame_rating(result['id']), profile=image_file, pics=pics, amount=len(pics), blocked=blocked, liked=liked, matched=matched, age=age, tags=tags)
		except TemplateNotFound:
			abort(404)
	else:
		abort(404)

@users.route('/profile/edit', methods=['GET', 'POST'])
@is_logged_in
def edit():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	if request.method == 'POST':
		cur.execute("SELECT * FROM users WHERE (username=? OR email=?) AND NOT id=?", [request.form.get('username'), request.form.get('email'), session['id']])
		results = cur.fetchall()
		if results:
			flash('Username or email already in use!', 'danger')
			return redirect(url_for('users.edit'))
		else:
			if request.form.get('birthdate'):
				data = request.form.get('birthdate').split("-")
				age = get_age(date(int(data[0]), int(data[1]), int(data[2])))
				if (not age or age < 18):
					flash('You are not allowed to use this site if you are under 18!', 'danger')
					return redirect(url_for('users.edit'))
			else: 
				flash('Please Spesify your Date of birth!', 'danger')
				return redirect(url_for('users.edit'))
			#let user update location removed notif cuz it be useless
			if (not request.form.get('gender')):
				flash('Please Spesify your Gender!', 'danger')
				return redirect(url_for('users.edit'))
				
			if (request.form.get('latCord') and request.form.get('lngCord') and request.form.get('city')):
				cur.execute("UPDATE users SET fname=?, lname=?, username=?, email=?, gender=?, sexuality=?, birthdate=?, bio=?, latCord=?, lngCord=?, city=? WHERE id=?", [request.form.get('fname'), request.form.get('lname'), request.form.get('username'), request.form.get('email'), request.form.get('gender'), request.form.get('sexuality'), request.form.get('birthdate'), request.form.get('bio'), request.form.get('latCord'), request.form.get('lngCord'),request.form.get('city'), session['id']])
				session['latCord'] = request.form.get('latCord')
				session['lngCord'] = request.form.get('lngCord')
				session['city'] = request.form.get('city')
			else:
				cur.execute("UPDATE users SET fname=?, lname=?, username=?, email=?, gender=?, sexuality=?, birthdate=?, bio=? WHERE id=?", [request.form.get('fname'), request.form.get('lname'), request.form.get('username'), request.form.get('email'), request.form.get('gender'), request.form.get('sexuality'), request.form.get('birthdate'), request.form.get('bio'), session['id']])
			con.commit()
			con.close()
			session['username'] = request.form.get('username')
			session['fname'] = request.form.get('fname')
			session['lname'] = request.form.get('lname')
			session['email'] = request.form.get('email')
			try:
				flash('Profile was updated!', 'success')
				return redirect(url_for('users.profile', username=request.form.get('username')))
			except TemplateNotFound:
				abort(404)
	else:
		username = session['username'].lower()
		cur.execute("SELECT * FROM users WHERE username=?", [username])
		result = cur.fetchone()
		con.close()
		if result:
			try:
				return render_template('edit.html', user=result)
			except TemplateNotFound:
				abort(404)
		else:
			abort(404)

@users.route('/profile/tags', methods=['GET', 'POST'])
@is_logged_in
def tags():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	if request.method == 'POST':
		cur.execute("SELECT * FROM tags WHERE UPPER(tags) = UPPER(?)", [request.form.get('tag')])
		result = cur.fetchall()
		if result:
			flash('Tag already exists!', 'danger')
		else:
			cur.execute("INSERT INTO tags (tags) VALUES (UPPER(?))", [request.form.get('tag')])
			con.commit()
	cur.execute("SELECT * FROM tags WHERE id IN (SELECT tagId FROM usertags GROUP BY tagId ORDER BY COUNT(tagId) DESC LIMIT 5)")
	popular = cur.fetchall()
	cur.execute("SELECT * FROM tags")
	tags = cur.fetchall()
	cur.execute("SELECT * FROM tags WHERE id IN (SELECT tagId FROM usertags WHERE userId=?)", [session['id']])
	mine = cur.fetchall()
	con.close()
	return render_template('tags.html', popular=popular, tags=tags, mine=mine)

@users.route('/profile/password', methods=['GET', 'POST'])
@is_logged_in
def password():
	if request.method == 'POST':
		password = request.form.get('password')
		confirm = request.form.get('confirm')
		if (password == confirm):
			password = hash_password(password)
			con = db_connect()
			cur = con.cursor()
			cur.execute("UPDATE users SET password=? WHERE id=?", [password, session['id']])
			con.commit()
			con.close()
			try:
				flash('Password was updated!', 'success')
				return redirect(url_for('users.profile', username=request.form.get('username')))
			except TemplateNotFound:
				abort(404)
		else:
			flash('Password don\'t match!', 'danger')
			return redirect(url_for('users.password'))
	else:
		try:
			return render_template('password.html')
		except TemplateNotFound:
			abort(404)

@users.route('/delete/<photoId>')
@is_logged_in
def delete_pic(photoId):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM photos WHERE userId=? AND id=?", [session['id'], photoId])
	result = cur.fetchone()
	if result:
		try:
			os.remove('matcha/static/photos/' + result['path'])
		except FileNotFoundError:
			flash('Picture has been deleted!', 'danger')
		cur.execute("DELETE FROM photos WHERE userId=? AND id=?", [session['id'], photoId])
		con.commit()
	else:
		flash('Couldn\'t delete the picture!', 'danger')
	con.close()
	return redirect(url_for('users.profile'))

@users.route('/set/<photoId>')
@is_logged_in
def set_pic(photoId):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM photos WHERE userId=? AND id=?", [session['id'], photoId])
	result = cur.fetchone()
	if result:
		cur.execute("UPDATE users SET ProfilePictureID=? WHERE id=?", [result['path'], session['id']])
		cur.execute("UPDATE photos SET profile=? WHERE userId=? AND profile=?", [0, session['id'], 1])
		cur.execute("UPDATE photos SET profile=? WHERE userId=? AND id=?", [1, session['id'], photoId])
		con.commit()
	else:
		flash('Couldn\'t update profile picture!', 'danger')
	con.close()
	return redirect(url_for('users.profile'))

@users.route('/profile/block/<userId>')
@is_logged_in
def block_user(userId):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM blocked WHERE userId=? AND blockedId=?", [session['id'], userId])
	result = cur.fetchone()
	if result:
		cur.execute("DELETE FROM blocked WHERE userId=? AND blockedId=?", [session['id'], userId])
		con.commit()
		con.close()
		data = {'id': userId, "message":session['username'] + " unblocked you"}
		sysmsg(data)
		flash('User has been unblocked!', 'success')
	else:
		cur.execute("INSERT INTO blocked (userId, blockedId) VALUES (?, ?)", [session['id'], userId])
		cur.execute("DELETE FROM likes WHERE user1=? AND user2=? AND user1 <> 1", [session['id'], userId])
		# set system msg if blocked
		con.commit()
		con.close()
		data = {'id': userId, "message":session['username'] + " blocked you"}
		sysmsg(data)
		flash('User has been blocked!', 'success')
	return redirect(url_for('users.profile', username=user['username']))

@users.route('/profile/report/<userId>')
@is_logged_in
def report_user(userId):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM reports WHERE userId=? AND reportedId=?", [session['id'], userId])
	result = cur.fetchone()
	if result:
		flash('User has been reported!', 'success')
	else:
		cur.execute("INSERT INTO reports (userId, reportedId) VALUES (?, ?)", [session['id'], userId])
		con.commit()
		con.close()
		flash('User has been reported!', 'success')
	return redirect(url_for('users.profile', username=user['username']))

@users.route('/profile/like/<userId>')
@is_logged_in
def like_user(userId):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM likes WHERE user1=? AND user2=?", [session['id'], userId])
	result = cur.fetchone()
	if (result and userId != 1):
		cur.execute("DELETE FROM likes WHERE user1=? AND user2=? AND user1 <> 1", [session['id'], userId])
		flash('User has been unliked!', 'success')
		# set system message if unliked
		con.commit()
		con.close()
		data = {'id': userId, "message":session['username'] + " unliked you"}
		sysmsg(data)
	else:
		cur.execute("INSERT INTO likes (user1, user2) VALUES (?, ?)", [session['id'], userId])
		cur.execute("DELETE FROM blocked WHERE userId=? AND blockedId=? AND userId <> 1", [session['id'], userId])
		con.commit()
		cur.execute("SELECT * FROM likes WHERE (user1=? AND user2=?) OR (user1=? AND user2=?) AND user1 <> 1", [session['id'], userId, userId, session['id']])
		matched = cur.fetchall()
		if len(matched) == 2:
			cur.execute("INSERT INTO matches (user1, user2) VALUES (?, ?)", [session['id'], userId])
			cur.execute("DELETE FROM likes WHERE (user1=? AND user2=?) OR (user1=? AND user2=?) AND user1 <> 1", [session['id'], userId, userId, session['id']])
			# set system message if matched
			con.commit()
			con.close()
			data = {'id': userId, "message":session['username'] + " matched with you"}
			sysmsg(data)
			flash('You made a match!', 'success')
		else:
			# set system message if matched
			con.commit()
			con.close()
			data = {'id': userId, "message":session['username'] + " liked you"}
			sysmsg(data)
			flash('User has been liked!', 'success')
	update_fame_rating(userId)
	return redirect(url_for('users.profile', username=user['username']))

@users.route('/profile/match/<userId>')
@is_logged_in
def match_user(userId):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM matches WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", [session['id'], userId, userId, session['id']])
	result = cur.fetchone()
	if result:
		cur.execute("DELETE FROM matches WHERE (user1=? AND user2=?) OR (user1=? AND user2=?) AND user1 <> 1", [session['id'], userId, userId, session['id']])
		con.commit()
		con.close()
		data = {'id': userId, "message":session['username'] + " unmatched you"}
		sysmsg(data)
		flash('You unmatched from user!', 'success')
	else:
		flash('Match not found!', 'success')
		con.close()
	update_fame_rating(userId)
	return redirect(url_for('users.profile', username=user['username']))

@users.route('/profile/pick_tag/<tagId>')
@is_logged_in
def pick_tag(tagId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("SELECT * FROM usertags WHERE userId=? AND tagId=?", [session['id'], tagId])
	result = cur.fetchone()
	if result:
		flash('Tag deleted from account!', 'success')
		cur.execute("DELETE FROM usertags WHERE userId=? AND tagId=?", [session['id'], tagId])
	else:
		flash('Tag added to account!', 'success')
		cur.execute("INSERT INTO usertags (userId, tagId) VALUES (?, ?)", [session['id'], tagId])
	con.commit()
	con.close()
	return redirect(url_for('users.tags'))

@users.route('/profile/activity/<type>')
@is_logged_in
def activity(type):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	likes = []
	if type == 'likes':
		cur.execute("SELECT * FROM users WHERE id IN (SELECT user2 FROM likes WHERE user1=?)", [session['id']])
		likes = cur.fetchall()
	elif type == 'matches':
		cur.execute("""SELECT * FROM matches LEFT OUTER JOIN users on (matches.user1 = users.id) Where matches.user2 = ? AND NOT UPPER(users.username) = ?
		UNION
		SELECT * FROM matches LEFT OUTER JOIN users on (matches.user2 = users.id) Where matches.user1 = ? AND NOT UPPER(users.username) = ?""", [session['id'], 'SYSTEM', session['id'], 'SYSTEM'])
		likes = cur.fetchall()
	elif type == 'views':
		cur.execute("SELECT * FROM users WHERE id IN (SELECT viewer FROM views WHERE viewee=?) AND NOT UPPER(username)=?", [session['id'], 'SYSTEM'])
		likes = cur.fetchall()
	elif type == 'likedBy':
		cur.execute("SELECT * FROM users WHERE id IN (SELECT user1 FROM likes WHERE user2=?)", [session['id']])
		likes = cur.fetchall()
	elif type == 'blocked':
		cur.execute("SELECT * FROM users WHERE id IN (SELECT blockedId FROM blocked WHERE userId=?)", [session['id']])
		likes = cur.fetchall()
	con.close()
	return render_template('activity.html', likes=likes, type=type.upper())
