from datetime import date
from math import sin, cos, atan2, sqrt, pi
from flask import session

def get_age(birthDate):
	today = date.today()
	age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
	return age

def deg2radiant(deg):
	return deg * (pi / 180)

def getdist(lat, lng):
	try:
		lat2 = float(session['latCord'])
		lng2 = float(session['lngCord'])
		R = 6371
		dLat = deg2radiant(lat2-lat)
		dLng = deg2radiant(lng2-lng)
		a = sin(dLat/2) * sin(dLat/2) + cos(deg2radiant(lat)) * cos(deg2radiant(lat2)) * sin(dLng/2) * sin(dLng/2)
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		d = R * c
		return round(d,4)
	except:
		return -1