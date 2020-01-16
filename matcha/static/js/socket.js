var socket = io.connect('http://' + document.domain + ':' + location.port);

function SelectRoom(_roomid, username)
{
	socket.emit('getHistory', {'room': _roomid, 'username': username});
	
	$('#Chatfrm').css('display', 'inline-block')
	$('div.messages').empty();
}

socket.on('load', (data) => {
	let message = ''
	data.message.forEach((item) => {
		if (item.senderId === data.id)
			name = data.sender
		else 
			name = data.reciever
		message += `<div class="message content-section">
			<h5>@${name}</h5>
			<p>${item.message}</p>
			<span class="time-right">${item.time}</span>
			</div>`
	})
	$('div.messages').append(message)
	$('div.messages').scrollTop($('div.messages')[0].scrollHeight);
})

socket.on('update', (data) => {
	message = data.message
	$('div.messages').append(message)
	$('div.messages').scrollTop($('div.messages')[0].scrollHeight);
});
