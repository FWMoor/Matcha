import sys

sys.dont_write_bytecode = True
from matcha import create_app, socketio
app = create_app(debug=True)

if __name__ == '__main__':
	socketio.run(app)
