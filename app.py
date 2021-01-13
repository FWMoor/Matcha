from matcha import create_app, socketio

app = create_app()

if __name__ == '__main__':
	# serve(app, host='0.0.0.0', port=8080, threads=4) #Prod Server
	# app.run() #Dev Server
	print("app started at : http://localhost:8080")
	socketio.run(app, host="localhost", port=8080)
