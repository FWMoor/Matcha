var socket = io.connect('http://' + document.domain + ':' + location.port);
location.hash = '';

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
	if (window.location.href.split('#').pop() == data.roomname)
	{
		$('div.messages').append(message)
		$('div.messages').scrollTop($('div.messages')[0].scrollHeight);
	}
	else
	{
		createnotification(data.rawmsg, data.roomname)
		// alert(data.rawmsg)
	}

});


function setpermission()
{
	if (!("Notification" in window)) {
		alert("This browser does not support desktop notification");
	}
	else if (Notification.permission === "granted") {
		  var notification = new Notification("Notifications allowed!");
	}
	else if (Notification.permission !== "denied") {
		Notification.requestPermission().then((permission) =>{
			if (permission === "granted") {
				var notification = new Notification("Notifications allowed!");
			}
		});
	}
}

function notify(message, title) {
}

function createnotification(message,title)
{
	if (Notification.permission === "granted")
	{
		var instance = new Notification(
			title, {
				body: message
			}
		);
	}
	else
	{
		alert(title + ':' + message)
	}

}