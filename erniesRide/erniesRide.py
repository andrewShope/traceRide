import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
				jsonify, flash
import utils
import bcrypt


app = Flask(__name__)
app.config.from_object('erniesRide_settings.BaseConfig')
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
	pledgeSum = utils.sumTotal(get_db())
	db = get_db()
	cur = db.execute('select riderName from riders order by riderName asc')
	riders = cur.fetchall()
	centerPledges = utils.centerSums(get_db())
	riderPledges = utils.riderSums(get_db())
	return render_template('index.html', pledgeSum=pledgeSum, riders=riders, 
							centerPledges=centerPledges, riderPledges=riderPledges)

@app.route('/pledge', methods=["POST"])
def pledge():
	email = request.form['emailAddress']
	pledge = request.form['pledgeAmount']
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	city = request.form['city']
	state = request.form['state']
	riderName = request.form['riderName']
	donationCenter = request.form['donationCenter']
	if utils.validateFields(firstName, lastName, city, state, email, pledge, riderName, donationCenter, get_db()):
		db = get_db()
		db.execute('insert into entries (email, pledge, firstName, lastName, city, state, riderName, donationCenter) values (?, ?, ?, ?, ? ,?, ?, ?)',
			[email, pledge, firstName, lastName, city, state, riderName, donationCenter])
		db.commit()
		pledgeSum = utils.sumTotal(get_db())
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
		cur = db.execute('select id, email, pledge, firstName, lastName, city, state, riderName, donationCenter from entries order by id asc')
		entries = cur.fetchall()

		return render_template('admin_panel.html', entries=entries)
	else:
		return redirect(url_for('login'))

@app.route('/admin/manage-riders', methods=["POST", "GET"])
def manageRiders():
	if request.method == "POST":
		pass
	if 'username' in session:
		db = get_db()
		cur = db.execute('select id, riderName from riders order by id asc')
		riders = cur.fetchall()

		return render_template('manage_riders.html', riders=riders)
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

@app.route('/add-rider', methods=["POST", "GET"])
def addRider():
	if request.method == "POST":
		if 'username' in session:
			db = get_db()
			newRiderName = request.form['riderName']
			cur = db.execute('insert into riders (riderName) values (?)', [newRiderName])
			db.commit()

@app.route('/delete-riders', methods=["POST", "GET"])
def deleteRider():
	if request.method == "POST":
		if 'username' in session:
			db = get_db()
			for entry in request.form.getlist("ids[]"):
				cur = db.execute('delete from riders where id = ?', (entry, ))
			db.commit()
			return jsonify(result="success")
	if request.method == "GET":
		return redirect(url_for('manageRiders'))

		
@app.route('/meeternie')
def meetErnie():
	return render_template('meet_ernie.html')

@app.route('/past-rides')
def pastRides():
	return render_template('past_rides.html')

@app.route('/past-rides/2017')
def ride2017():
	return render_template('ride_2017.html')
	
@app.route('/past-rides/2014')
def ride2014():
	return render_template('ride_2014.html')

@app.route('/about-elizabeths-new-life-center')
def aboutENLC():
	return render_template('enlc.html')

@app.route('/about-community-pregnancy-center')
def aboutCPC():
	return render_template('cpc.html')
