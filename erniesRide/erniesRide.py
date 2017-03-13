import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
				jsonify, flash
import utils
import bcrypt


app = Flask(__name__)
app.config.from_object('default_settings.BaseConfig')
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'pledges.db'),
	))

def connect_db():
	"""Connects to the specific database"""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row 
	return rv

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	"""Initializes the database"""
	init_db()
	print("Initialized the database.")

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of a request"""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def index():
	pledgeSum = utils.sumPledges(get_db())
	return render_template('index.html', pledgeSum=pledgeSum)

@app.route('/pledge', methods=["POST"])
def pledge():
	email = request.form['emailAddress']
	pledge = request.form['pledgeAmount']
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	city = request.form['city']
	state = request.form['state']
	if utils.validateFields(firstName, lastName, city, state, email, pledge):
		db = get_db()
		db.execute('insert into entries (email, pledge, firstName, lastName, city, state) values (?, ?, ?, ?, ? ,?)',
			[email, pledge, firstName, lastName, city, state])
		db.commit()
		pledgeSum = utils.sumPledges(get_db())
		return jsonify(result='success', total=pledgeSum, pledgeAmount=pledge)
	else:
		return jsonify(result='failure')

@app.route('/view')
def show_entries():
	db = get_db()
	cur = db.execute('select email, pledge from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

@app.route('/admin/', methods=["POST", "GET"])
def login():
	if request.method == "POST":
		app.logger.debug(request.form.keys())
		if 'username' in request.form.keys() and 'inputPassword' in request.form.keys():
			if bcrypt.checkpw(request.form['inputPassword'].encode(), app.config['ADMIN_PASSWORD'].encode()) and request.form['username'] == app.config['ADMIN_USERNAME']:
				session['username'] = request.form['username']
				return redirect(url_for('admin'))
	if 'username' in session:
		return redirect(url_for('admin'))

	return render_template("sign_in.html")

@app.route('/admin/dashboard', methods=["POST", "GET"])
def admin():
	if request.method == "POST":
		pass
	if 'username' in session:
		db = get_db()
		cur = db.execute('select id, email, pledge, firstName, lastName, city, state from entries order by id asc')
		entries = cur.fetchall()

		return render_template('admin_panel.html', entries=entries)
	else:
		return redirect(url_for('login'))

@app.route('/delete', methods=["POST", "GET"])
def deleteRows():
	if request.method == "POST":
		if 'username' in session:
			db = get_db()
			for entry in request.form.getlist("ids[]"):
				cur = db.execute('delete from entries where id = ?', (entry, ))
			db.commit()
			return jsonify(result="success")
	return jsonify(result="failure")
	if request.method == "GET":
		return redirect(url_for('admin'))
		
@app.route('/meeternie')
def meetErnie():
	return render_template('meet_ernie.html')
