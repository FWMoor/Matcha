// Connect socket
var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', () => {
	socket.emit('Connect event', {
		time: Date.now()
	});

	// Handel message sending 
	$('form').on('submit', (e) => {
		e.preventDefault()
		// Set username serverside
		let user_input = $('input.message').val()
		socket.emit('SendChat event', {
			message : user_input
		})
		// clear message box
		$('input.message').val('').focus()
		})
});

// add server rendered message here.
socket.on('ServerReply', (message_template) => {
	$('div.messages').append(message_template);
});
