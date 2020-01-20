from flask import Blueprint, render_template, url_for, request, flash, redirect, session, abort
from jinja2 import TemplateNotFound
from datetime import date 

import secrets
import os

from matcha.auth.utils import hash_password
from matcha.decorators import is_logged_in
from matcha.db import db_connect, dict_factory

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

users = Blueprint('users', __name__,
				  template_folder='./templates', static_folder='../static')

def get_age(birthDate):
	today = date.today()
	age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
	return age

def update_fame_rating(id):
	con = db_connect()
	cur = con.cursor()
	cur.execute("SELECT * FROM likes WHERE user2=?", [id])
	like = cur.fetchall()
	likes = len(like)
	cur.execute("SELECT * FROM matches WHERE user2=?", [id])
	match = cur.fetchall()
	matches = len(match)
	cur.execute("SELECT * FROM users WHERE NOT id=?", [id])
	tot = cur.fetchall()
	total = len(tot)
	if (total > 0):
		fame = (likes + matches) / total * 5
	else:
		fame = 0
	cur.execute("UPDATE users SET fame=? WHERE id=?", [round(fame, 1), id])
	con.commit()
	con.close()
	return likes + matches

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

@users.route('/profile', defaults={'username': None}, methods=['GET', 'POST'])
@users.route('/profile/<username>', methods=['GET', 'POST'])
@is_logged_in
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
		cur.execute("SELECT * FROM photos WHERE userId=?", [result['id']])
		pics = cur.fetchall()
		cur.execute("SELECT * FROM photos WHERE userId=? AND profile=1", [result['id']])
		profile = cur.fetchone()
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
		image = profile['path'] if profile != None else 'default.jpeg'
		image_file = url_for('static', filename='photos/' + image)
		try:
			if result['password']:
				del result['password']
			update_fame_rating(result['id'])
			if result['birthdate']:
				data = result['birthdate'].split("-")
				age = get_age(date(int(data[0]), int(data[1]), int(data[2])))
			else:
				age = 0
			return render_template('profile.html', user=result, username=username, profile=image_file, pics=pics, amount=len(pics), blocked=blocked, liked=liked, matched=matched, age=age)
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
		notif = 1 if request.form.get('notifications') else 0
		cur.execute("SELECT * FROM users WHERE (username=? OR email=?) AND NOT id=?", [request.form.get('username'), request.form.get('email'), session['id']])
		results = cur.fetchall()
		if results:
			flash('Username or email already in use!', 'danger')
			return redirect(url_for('users.edit'))
		else:
			cur.execute("UPDATE users SET fname=?, lname=?, username=?, email=?, gender=?, sexuality=?, birthdate=?, bio=?, notifications=? WHERE id=?", [request.form.get('fname'), request.form.get('lname'), request.form.get('username'), request.form.get('email'), request.form.get('gender'), request.form.get('sexuality'), request.form.get('birthdate'), request.form.get('bio'), notif, session['id']])
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
	cur = con.cursor()
	cur.execute("SELECT * FROM photos WHERE userId=? AND id=?", [session['id'], photoId])
	result = cur.fetchone()
	if result:
		os.remove('matcha/static/photos/' + result[2])
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
	cur = con.cursor()
	cur.execute("SELECT * FROM photos WHERE userId=? AND id=?", [session['id'], photoId])
	result = cur.fetchone()
	if result:
		cur.execute("UPDATE photos SET profile=? WHERE userId=? AND profile=?", [0, session['id'], 1])
		con.commit()
		cur.execute("UPDATE photos SET profile=? WHERE id=? AND userId=?", [1, photoId, session['id']])
		con.commit()
	else:
		flash('Couldn\'t update profile picture!', 'danger')
	con.close()
	return redirect(url_for('users.profile'))

@users.route('/profile/block/<userId>')
@is_logged_in
def block_user(userId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM blocked WHERE userId=? AND blockedId=?", [session['id'], userId])
	result = cur.fetchone()
	if result:
		cur.execute("DELETE FROM blocked WHERE userId=? AND blockedId=?", [session['id'], userId])
		flash('User has been unblocked!', 'success')
	else:
		cur.execute("INSERT INTO blocked (userId, blockedId) VALUES (?, ?)", [session['id'], userId])
		cur.execute("DELETE FROM likes WHERE user1=? AND user2=?", [session['id'], userId])
		flash('User has been blocked!', 'success')
	con.commit()
	con.close()
	return redirect(url_for('users.profile', username=user[3]))

@users.route('/profile/like/<userId>')
@is_logged_in
def like_user(userId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM likes WHERE user1=? AND user2=?", [session['id'], userId])
	result = cur.fetchone()
	if result:
		cur.execute("DELETE FROM likes WHERE user1=? AND user2=?", [session['id'], userId])
		flash('User has been unliked!', 'success')
	else:
		cur.execute("INSERT INTO likes (user1, user2) VALUES (?, ?)", [session['id'], userId])
		cur.execute("DELETE FROM blocked WHERE userId=? AND blockedId=?", [session['id'], userId])
		con.commit()
		cur.execute("SELECT * FROM likes WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", [session['id'], userId, userId, session['id']])
		matched = cur.fetchall()
		if len(matched) == 2:
			cur.execute("INSERT INTO matches (user1, user2) VALUES (?, ?)", [session['id'], userId])
			cur.execute("DELETE FROM likes WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", [session['id'], userId, userId, session['id']])
			flash('You made a match!', 'success')
		else:
			flash('User has been liked!', 'success')
	con.commit()
	con.close()
	update_fame_rating(userId)
	return redirect(url_for('users.profile', username=user[3]))

@users.route('/profile/match/<userId>')
@is_logged_in
def match_user(userId):
	con = db_connect()
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id=?", [userId])
	user = cur.fetchone()
	cur.execute("SELECT * FROM matches WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", [session['id'], userId, userId, session['id']])
	result = cur.fetchone()
	if result:
		cur.execute("DELETE FROM matches WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", [session['id'], userId, userId, session['id']])
		con.commit()
		flash('You unmatched from user!', 'success')
	else:
		flash('Match not found!', 'success')
	con.close()
	update_fame_rating(userId)
	return redirect(url_for('users.profile', username=user[3]))
