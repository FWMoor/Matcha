from flask import Blueprint, render_template, session, flash, redirect, url_for, abort
from matcha.decorators import not_logged_in, is_logged_in
from .. import socketio
from flask_socketio import join_room, leave_room, emit
from matcha.db import db_connect, dict_factory
from datetime import datetime
import json

chat = Blueprint('chat', __name__,
				 template_folder='./templates')

# Messaging
@chat.route('/')
@is_logged_in
def sessions():
	try:
		return render_template('chat.html', Matches=getMatches(), title="Chat")
	except:
		abort(500)

def escape(s, quote=True):
	s = s.replace("&", "&amp;") # Must be done first!
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	if quote:
		s = s.replace('"', "&quot;")
		s = s.replace('\'', "&#x27;")
	return s

def getMatches():
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	if session.get('id') is not None:
		id = session['id']
		cur.execute("""SELECT users.username, matches.id, users.id as userid FROM matches LEFT OUTER JOIN users on (matches.user1 = users.id) Where matches.user2 = ?
		UNION
		SELECT users.username, matches.id, users.id as userid FROM matches LEFT OUTER JOIN users on (matches.user2 = users.id) Where matches.user1 = ?""", [id,id])
		result = cur.fetchall()
		con.close()
	else:
		return None
	return result

def getMessages(room):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM messages WHERE matchId=?", [room])
	result = cur.fetchall()
	con.close()
	return result

def getReciever(room, id):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("""SELECT users.username, matches.id, users.id as userid FROM matches LEFT OUTER JOIN users on (matches.user1 = users.id) Where matches.id = ? AND matches.user2 = ?
		UNION
		SELECT users.username, matches.id, users.id as userid FROM matches LEFT OUTER JOIN users on (matches.user2 = users.id) Where matches.id = ? AND matches.user1 = ?""", [room, id, room, id])
	result = cur.fetchone()
	con.close()
	return result

def getusernamebyid(id):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT * FROM users WHERE id = ? ", [id])
	result = cur.fetchone()
	con.close()
	return result

def getroombyuserids(id1, id2):
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("SELECT id FROM matches WHERE user1 = ? AND user2 = ?", [id1, id2])
	result = cur.fetchone()
	con.close()
	return result

def insertMessage(arr):
	con = db_connect()
	cur = con.cursor()
	cur.execute("INSERT INTO messages (matchId, senderId, receiveId, message, time) VALUES (?,?,?,?,?)", arr)
	con.commit()
	con.close()

def setseen(id, room):
	con = db_connect()
	cur = con.cursor()
	cur.execute(
	"""	UPDATE messages SET seen = 1
		WHERE matchId = ? 
		AND receiveId = ?""",
		[room, id])
	con.commit()
	con.close()

def setCords(lng, lat, id):
	con = db_connect()
	cur = con.cursor()
	cur.execute(
	"""	UPDATE users SET lngCord = ?, latCord = ?
		WHERE id = ?""",
		[lng, lat, id])
	con.commit()
	con.close()

@socketio.on('getHistory')
def getHistory(data):
	session['room'] = str(data['room'])
	#set messages as seen
	setseen(session['id'], data['room'])
	#construct messages
	reciever = getReciever(session['room'], session['id'])['username']
	messages = getMessages(data['room'])
	strmessages = ''
	for message in messages:
		if (message['senderId'] == session['id']):
			css = "send"
			user = session['username']
		else:
			css = "recieve"
			user = reciever
		if (message['seen'] == 1):
			status = 'seen'
		else:
			status = 'unseen'
		strmessages += """
		<div class="message content-section {}">
			<h5>@{}</h5>
			<p>{}</p>
			<span class="time-right {} ">{}</span>
		</div>
		<br>""".format(css,user, message['message'], status ,message['time'])
	emit('load', strmessages)

@socketio.on('connect')
def connect_all():
	if (not session.get('room')):
		session['room'] = None
	Matches=getMatches()
	if Matches is not None:
		for match in Matches:
			join_room(str(match['id']))

@socketio.on('send')
def message(data):
	if (session.get('room')):
		date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
		receiveId = getReciever(session['room'], session['id'])['userid']
		msg = escape(data['message'])
		if not msg.isspace():
			insertMessage([session['room'], session['id'], receiveId, msg, date_time])
			message = """
			<div class="message content-section">
				<h5>@{}</h5>
				<p>{}</p>
				<span class="time-right">{}</span>
			</div>
			<br>""".format(session['username'], msg,date_time)
			JSON = {"message": message, "rawmsg": msg, "roomname": session['room'], "sender": session['username']}
			emit('update',JSON,room=session['room'], json=True)

def sysmsg(data):
	date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
	username = getusernamebyid(data['id'])
	msg = escape(data['message'])
	room = getroombyuserids(1, data['id'])['id']
	# print(room)
	if not msg.isspace():
		insertMessage([room, 1, data['id'], msg, date_time])
		message = """
		<div class="message content-section">
			<h5>@{}</h5>
			<p>{}</p>
			<span class="time-right">{}</span>
		</div>
		<br>""".format(session['username'], msg,date_time)
		JSON = {"message": message, "rawmsg": msg, "roomname": str(room), "sender": "System"}
		emit('update',JSON,room=str(room), json=True, namespace = '/')

@socketio.on('location')
def location(data):
	print(session['username'] + " location data:")
	print(data)
	setCords(data['lng'], data['lat'], session['id'])