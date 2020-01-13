if (navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(
	(position) => {
		var lat = position.coords.latitude
		var lng =  position.coords.longitude
		console.log(lat)
		console.log(lng)
	},
	(error) => {
		console.log(error)
		ajaxreq()
	});

} else {
	ajaxreq()
}

function ajaxreq()
{
	$.ajax({
		dataType: "json",
		url: "https://ipapi.co/json/",
		success: function(data){
			console.log(data['latitude'])
			console.log(data['longitude'])
		}
	})
}

function deg2rad(deg) {
	return deg * (Math.PI/180)
}

function Distance(lat1,lon1,lat2,lon2) {
	var R = 6371; // Radius of the earth in km
	var dLat = deg2rad(lat2-lat1);
	var dLon = deg2rad(lon2-lon1); 
	var a = 
		Math.sin(dLat/2) * Math.sin(dLat/2) +
		Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
		Math.sin(dLon/2) * Math.sin(dLon/2); 
	var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
	var d = R * c;
	return d;
}