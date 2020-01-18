from flask import Blueprint, render_template, session, flash, redirect, url_for, abort
from matcha.decorators import not_logged_in, is_logged_in
from flask_socketio import join_room, leave_room, send, emit
from matcha.db import db_connect, dict_factory
from .. import socketio
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

def insertMessage(arr):
	con = db_connect()
	cur = con.cursor()
	cur.execute("INSERT INTO messages (matchId, senderId, receiveId, message, time) VALUES (?,?,?,?,?)", arr)
	con.commit()
	con.close()


@socketio.on('getHistory')
def getHistory(data):
	session['room'] = str(data['room'])
	JSON = {
			"reciever": getReciever(session['room'], session['id'])['username'],
			"message": getMessages(data['room']),
			"sender": session['username'],
			"id": session['id']
	}
	emit('load', JSON, json=True)

@socketio.on('connect')
def connect_all():
	Matches=getMatches()
	if Matches is not None:
		for match in Matches:
			join_room(str(match['id']))

@socketio.on('send')
def message(data):
	if (session.get('room')):
		date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
		receive = getReciever(session['room'], session['id'])
		receiveId = receive['id']
		receiver = receive['username']

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
			JSON = {"message": message, "room": receiver, "rawmsg": msg, "roomname": session['username']}
			emit('update',JSON, room=session['room'], json=True)
