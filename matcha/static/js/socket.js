var socket = io.connect('http://' + document.domain + ':' + location.port);
location.hash = '';

function SelectRoom(_roomid, username)
{
	socket.emit('getHistory', {'room': _roomid, 'username': username});	
	$('div.MessageRoom').text(username)
	$('#Chatfrm').css('display', 'inline-block')
	$('div.messages').empty();
}

socket.on('load', (messages) => {
	$('div.messages').append(messages)
	$('div.messages').scrollTop($('div.messages')[0].scrollHeight);
})

socket.on('update', (data) => {
	message = data.message
	if (window.location.href.split('#').pop() === data.roomname)
	{
		
		$('div.messages').append(message)
		$('div.messages').scrollTop($('div.messages')[0].scrollHeight);
		SelectRoom(data.roomname, $('div.MessageRoom').text())
	}
	else
	{
		createnotification(data.rawmsg, data.sender)
	}

});


function setpermission()
{
	if (!("Notification" in window)) {
		alert("This browser does not support desktop notification");
	}
	else if (Notification.permission === "granted") {
		  var notification = new Notification("Welcome to Matcha!");
	}
	else if (Notification.permission !== "denied") {
		Notification.requestPermission().then((permission) =>{
			if (permission === "granted") {
				var notification = new Notification("Welcome to Matcha!")
			};
		});
	}
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