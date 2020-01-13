// Connect socket
var socket = io.connect('http://' + document.domain + ':' + location.port);
var id = undefined

function SelectRoom(_id)
{
	socket.emit('join', {'room': _id});
	$('div.messages').empty();
	$('.RoomId').text(_id);
	id = _id;
}

// Get update from server
socket.on('update', (message) => {
	$('div.messages').append(message + "<br/>");
});

// If send a chat
$('.Chatfrm').on('submit', (e) => {
	e.preventDefault()
		let message = $('input.message').val();
		// clear message box
		socket.emit('send', {'message': message, 'room': id});
		$('input.message').val('').focus();
});

