from calendar import c
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template as flask_render_template, \
				jsonify, flash, render_template_string
from werkzeug.utils import secure_filename
import TraceRideUtils as utils
import bcrypt

app = Flask(__name__)
if os.environ.get("FLASK_ENV") == "development":
	app.config.from_object('traceRide_settings.BaseConfig')
else:
	app.config.from_object('default_settings.BaseConfig')

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'pledges.db'),
	))
UPLOAD_FOLDER = os.path.join(app.root_path, "static/images")
THUMBNAIL_FOLDER = os.path.join(app.root_path, "static/thumbnails")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def render_template(source, **context):
	siteInfo = utils.getSiteInfo(get_db())
	context["siteInfo"] = siteInfo
	print(app.root_path)

	return flask_render_template(source, **context)

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
	cur = db.execute('select contents from articles where title="main-article"')
	results = cur.fetchall()
	mainArticleContents = results[0]["contents"]
	siteInfo = utils.getSiteInfo(db)
	cur = db.execute('select riderName from riders order by id asc')
	riders = cur.fetchall()
	riderPledges = utils.riderSums(get_db())

	return render_template('index.html', pledgeSum=pledgeSum, 
						   mainArticleContents=mainArticleContents,
						   siteInfo=siteInfo,
						   riders=riders,
						   riderPledges=riderPledges)

@app.route('/pledge', methods=["POST"])
def pledge():
	email = request.form['emailAddress']
	pledge = request.form['pledgeAmount']
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	city = request.form['city']
	state = request.form['state']
	riderName = request.form['riderName']
	print(request.form)
	if utils.validateFields(city, state, firstName, lastName, email, pledge, riderName, get_db()):
		db = get_db()
		db.execute('insert into entries (email, pledge, firstName, lastName, city, state, riderName) values (?, ?, ?, ?, ? ,?, ?)',
			[email, pledge, firstName, lastName, city, state, riderName])
		db.commit()

		db = get_db()
		db.execute('insert into email_queue (email_address, first_name, last_name, pledged_rider, pledged_amount, email_sent) values (?, ?, ?, ?, ? ,?)',
			[email, firstName, lastName, riderName, pledge, 0])
		db.commit()

		pledgeSum = utils.sumTotal(get_db())
		return jsonify(result='success', total=pledgeSum, pledgeAmount=pledge)
	else:
		return jsonify(result='failure')

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
		cur = db.execute('select id, email, pledge, riderName, firstName, lastName, city, state from entries order by id asc')
		entries = cur.fetchall()

		return render_template('admin_panel.html', entries=entries)
	else:
		return redirect(url_for('login'))

@app.route('/admin/edit-site-information', methods=["GET", "POST"])
def editSiteInfo():
	if 'username' in session:
		if request.method == "GET":
			return render_template('page_editor.html')
		if request.method == "POST":
			db = get_db()
			cur = db.execute('update site_info set contents = ? where title="websiteTitle"', 
							(request.form["websiteTitle"], ))
			db.commit()
			cur = db.execute('update site_info set contents = ? where title="isSponsorActive"', 
							(request.form["sponsorStatus"], ))
			db.commit()
			cur = db.execute('update site_info set contents = ? where title="activeSponsorMessage"', 
							(request.form["activeSponsorMessage"], ))
			db.commit()
			cur = db.execute('update site_info set contents = ? where title="inactiveSponsorMessage"', 
							(request.form["inactiveSponsorMessage"], ))
			db.commit()

			return redirect(url_for('editSiteInfo'))
	else:
		return redirect(url_for('login'))

@app.route('/admin/edit-article/<articleTitle>', methods=["GET", "POST"])
def editArticle(articleTitle):
	if 'username' in session:
		if request.method=="POST":
			articleTitle = request.form["articleTitle"]
			articleContents = request.form["articleContents"]
			db = get_db()
			cur = db.execute('update articles set contents = ? where title = ?',
							(articleContents, articleTitle ))
			db.commit()

			return redirect(url_for('editArticle', articleTitle=articleTitle))
		else:
			db = get_db()
			cur = db.execute('select * from articles where title=?', (articleTitle, ))
			results = cur.fetchall()
			articleContents = results[0]

			return render_template('article_editor.html', articleContents=articleContents)


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

@app.route('/admin/images', methods=["GET", "POST"])
def imageFolder():
	if 'username' in session:
		if request.method == "GET":
			fileList = os.listdir(THUMBNAIL_FOLDER)
			fileList.sort()
			return render_template('image_folder.html', fileList=fileList)
		if request.method == "POST":
			if 'file' not in request.files:
				return redirect(url_for('imageFolder'))
			file = request.files['file']
			if file.filename == '' or file is None:
				return(redirect(url_for('imageFolder')))
			if file and utils.allowedFile(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(UPLOAD_FOLDER, filename))
				utils.saveThumbnail(filename, UPLOAD_FOLDER, THUMBNAIL_FOLDER)
				return redirect(url_for('imageFolder'))
	else:
		return redirect(url_for('login'))

@app.route('/admin/auto-email', methods=["GET", "POST"])
def autoEmailView():
	if 'username' in session:
		if request.method == "GET":
			db = get_db()
			cur = db.execute('select * from site_info where title = ?;', ("autoEmailMessage",))
			emailMessage = cur.fetchall()
			return render_template('edit_auto_email.html', emailMessage=emailMessage)
		elif request.method == "POST":
			db = get_db()
			emailContents = request.form["emailMessage"]
			cur = db.execute("update site_info set contents = ? where title = ?;", (emailContents, "autoEmailMessage"))
			db.commit()
			return redirect(url_for("autoEmailView"))
	else:
		return redirect(url_for('login'))