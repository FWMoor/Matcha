from flask import Blueprint, render_template, session
from matcha.decorators import not_logged_in, is_logged_in
from flask_socketio import emit
from .. import socketio
from datetime import datetime

msg = Blueprint('msg', __name__,
				 template_folder='./templates')

# Messaging
@msg.route('/')
@is_logged_in
def sessions():
	return render_template('chat.html')

@socketio.on('Connect event')
def Connect_Event(json, methods=['GET', 'POST']):
	print('USER CONNECTED')

@socketio.on('SendChat event')
def SendChat_Event(json, methods=['POST', 'GET']):
	# Preform html cleanup specialchars here
	now = datetime. now()
	current_time = now.strftime("%m/%d/%Y, %H:%M:%S")
	template = "<div> \
					<h4>" + session['username'] + "</h4> \
					<h5>" + current_time + " </h5> \
					<img src="" + session['pfp'] + "" alt = \"Profile Picture here!\" ></img> \
					<p>" + json['message'] + "</p> \
				</div>"

	socketio.emit('ServerReply', template)
