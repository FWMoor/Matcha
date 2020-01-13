from flask import Blueprint, render_template, session, flash, redirect, url_for
from matcha.decorators import not_logged_in, is_logged_in
from flask_socketio import join_room, leave_room, send, emit
from matcha.db import db_connect, dict_factory
from .. import socketio
from datetime import datetime

chat = Blueprint('chat', __name__,
				 template_folder='./templates')

#Data to use for the meantime
Matches = [
	{
		"username": "Steve",
		"name": "Steven",
		"surname": "Robinson",
		"email": "Email@steve.co",
		"matchId": 1
	},
	{
		"username": "Bob",
		"name": "Bobbyson",
		"surname": "Rob",
		"email": "Email@bob.com",
		"matchId": 2
	}
]
messages = ''

# Messaging
@chat.route('/')
@is_logged_in
def sessions():
	return render_template('chat.html', Matches=Matches)


@socketio.on('join')
def joined(data):
	room = str(data['room'])
	join_room(str(room))
	# Get all messages from db of current match and append it here
	con = db_connect()
	con.row_factory = dict_factory
	cur = con.cursor()
	cur.execute("""SELECT * FROM messages WHERE matchId=?""", [data['room']])
	result = cur.fetchall()
	for item in result:
		emit('update', item['message'], room=room)
	con.close()

@socketio.on('send')
def message(data):
	room = str(data['room'])
	# save message 
	con = db_connect()
	cur = con.cursor()
	cur.execute("INSERT INTO messages (matchId, senderId, receiveId, message, time) VALUES (?,?,?,?,?)", 
	[data['room'], 1, 1, data['message'], "Str time"])
	con.commit()
	con.close()
	emit('update', data['message'], room=room)
