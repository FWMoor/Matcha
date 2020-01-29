var socket = io.connect('http://' + document.domain + ':' + location.port);
location.hash = '';

// Update every 5 sec
window.setInterval(() =>
{
	var url_raw = window.location.href

	if (url_raw.indexOf("login") > -1)
		return
	if (url_raw.indexOf("register") > -1)
		return
	socket.emit('update_msgcnt',
		cb = (data) => {
			if (data > 0)
				$('#msgcnt').text(data);
				$('div.messages').empty();
				if (url_raw.indexOf('#') > -1)
				{
					var room = url_raw.split('#').pop()
					if (room)
					{
						socket.emit('getHistory', {
							'room': room,
							'username': $('div.MessageRoom').text()
						});
						$('#Chatfrm').css('display', 'inline-block')
					}
				}
		}
	)

}, 5000);


function SelectRoom(_roomid, username)
{
	$('div.messages').empty();
	socket.emit('getHistory', {'room': _roomid, 'username': username});	
	$('div.MessageRoom').text(username)
	$('#Chatfrm').css('display', 'inline-block')
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
	}
	else
	{
		createnotification(data.rawmsg, data.sender)
	}
});


// Notifications
function setpermission()
{
	if (!("Notification" in window)) {
		alert("This browser does not support desktop notification");
	}
	else if (Notification.permission === "granted") {
		  var notification = new Notification("Notifications are enabled!");
	}
	else if (Notification.permission !== "denied") {
		Notification.requestPermission().then((permission) =>{
			if (permission === "granted") {
				var notification = new Notification("Notifications are enabled!")
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


//Location
function getlocation()
{
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
		(position) => {
			var lat = position.coords.latitude
			var lng =  position.coords.longitude
			$('#latCord').val(lat)
			$('#lngCord').val(lng)
			$.ajax({
				dataType: "json",
				url:'http://nominatim.openstreetmap.org/reverse?format=json&lat='+ lat +'&lon=' + lng,
				success : function(data) {
					if (data['error'])
					{
						$('#city').val('Unknown')
					}
					else
					{
						$('#city').val(data['address']['city'])
					}
				}
			})
		},
		(error) => {
			console.log("Couldn't use GPS")
			ajaxreq()
		});
	} else {
		ajaxreq()
	}
}

function ajaxreq()
{
	$.ajax({
		dataType: "json",
		url: "https://ipapi.co/json/",
		success: function(data){
			$('#latCord').val(data['longitude'])
			$('#lngCord').val(data['latitude'])
			$('#city').val(data['city'])
		}
	})
}

