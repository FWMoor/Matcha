from flask import Flask, render_template, url_for
from forms import RegistrationForm
app = Flask(__name__)

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


@app.route('/register')
def register():
	form = RegistrationForm()
	return render_template('register.html', title='Register', form=form)


@app.route('/about')
def about():
	return render_template('about.html', title='About')


if __name__ == '__main__':
	app.run()
