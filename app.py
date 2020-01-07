from flask import Flask, render_template, url_for, request
import re
app = Flask(__name__)

app.config['SECRET_KEY'] = 'dd35c1f1152a18e60a79dcafafed4b6c'

post = [
	{
		'user': 'John Smith',
		'age': 24
	},
	{
		'user': 'John Smit',
		'age': 25
	}
]

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html', posts=post)

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/register', methods = ['GET', 'POST'])
def register():
	errors = []
	if request.method == 'POST':
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		uidLen = len(request.form['username'])
		if uidLen < 6 or uidLen > 20:
			errors.append('Username should be between 6 and 20 characters')
		if request.form['password'] != request.form['confirm']:
			errors.append('Passwords don\'t match!')
		if not re.search(regex, request.form['email']):
			errors.append('Enter a valid email')
		if len(errors) == 0:
			return render_template('about.html', title='It worked')
	return render_template('register.html', title='Register', errors=errors)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	errors = []
	if request.method == 'POST':
		if len(errors) == 0:
			return render_template('about.html', title='It worked')
	return render_template('login.html', title='Login')

if __name__ == '__main__':
	app.run(debug=True)
