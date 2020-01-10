import sys

sys.dont_write_bytecode = True
from matcha import create_app, socketio
app = create_app()

if __name__ == '__main__':
	socketio.run(app, debug=True)
