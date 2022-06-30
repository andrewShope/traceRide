from calendar import c
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template as flask_render_template, \
				jsonify, flash, render_template_string
from werkzeug.utils import secure_filename
import utils
import bcrypt

# UPLOAD_FOLDER = "/home/andrew/erniesRide/erniesRide/static/images"

app = Flask(__name__)
if os.environ.get("FLASK_ENV") == "development":
	app.config.from_object('erniesRide_settings.BaseConfig')
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
	cur = db.execute('select riderName from riders order by riderName asc')
	riders = cur.fetchall()
	centerPledges = utils.centerSums(get_db())
	riderPledges = utils.riderSums(get_db())
	siteInfo = utils.getSiteInfo(db)
	cur = db.execute('select contents from articles where title="main_article"')
	results = cur.fetchall()
	mainArticleContents = results[0]["contents"]
	cur = db.execute('select * from rider_bios')
	riderBios = cur.fetchall()
	return render_template('index.html', pledgeSum=pledgeSum, riders=riders, 
							centerPledges=centerPledges, riderPledges=riderPledges, 
							siteInfo=siteInfo, mainArticleContents=mainArticleContents, riderBios=riderBios)

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
			cur = db.execute('update site_info set contents = ? where title="banner_image"',
							(request.form["bannerImage"], ))
			db.commit()

			return redirect(url_for('editSiteInfo'))
	else:
		return redirect(url_for('login'))

@app.route('/admin/edit-article/<articleTitle>', methods=["POST", "GET"])
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

			return render_template('front_page_article.html', articleContents=articleContents)
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

			return "Good"
		else:
			return redirect(url_for('login'))
	else:
		return redirect(url_for('login'))

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
	db = get_db()
	cur = db.execute('select contents from articles where title = "ernies_story"')
	results = cur.fetchall()
	articleContents = results[0]

	return render_template('meet_ernie.html', articleContents=articleContents)

@app.route('/past-rides/<year>', methods=["GET"])
def pastRides(year):
	db = get_db()
	cur = db.execute('select * from past_rides where title = ?', (year, ))
	results = cur.fetchall()
	results = results[0]
	results = render_template_string(results["contents"])

	return render_template('past_rides_dynamic.html', articleInfo=results)

@app.route('/about-elizabeths-new-life-center')
def aboutENLC():
	return render_template('enlc.html')

@app.route('/about-community-pregnancy-center')
def aboutCPC():
	return render_template('cpc.html')

@app.route('/about-flc-auglaize-county')
def aboutFLC():
	return render_template('flc.html')

@app.route('/admin/update-site-title', methods=["POST"])
def changeSiteTitle():
	if request.method == "POST":
		if 'username' in session:
			db = get_db()
			cur = db.execute('select * from site_info where title = "websiteTitle"')
			results = cur.fetchall()
			if len(results) > 0:
				cur = db.execute('update site_info set contents = ? where title = "websiteTitle"', (request.form['websiteTitle'], ))
				db.commit()
			else:
				cur = db.execute('insert into site_info (title, contents) values ("websiteTitle", ?)', (request.form['websiteTitle'], ))
				db.commit()
			return redirect(url_for('editSiteInfo'))
		else:
			return redirect(url_for('login'))
	else:
		pass

@app.route('/admin/add-new-ride/<articleID>', methods=["GET", "POST"])
def addNewRideArticle(articleID):
	if request.method == "POST":
		if 'username' in session:
			#ADD A COMPLETELY NEW ARTICLE
			if articleID == "new":
				db = get_db()
				#Get data from the request
				articleTitle = request.form['articleTitle']
				articleContents = request.form['articleContents']
				cur = db.execute('insert into past_rides (title, contents) values (?, ?)', (articleTitle, articleContents))
				db.commit()
			else:
				# IF WE ARE HERE WE ARE EDITING AN EXISTING ARTICLE
				if 'delete' in request.form.keys():
					db = get_db()
					articleDatabaseID = request.form['articleDatabaseID']
					cur = db.execute('delete from past_rides where id= ?', (articleDatabaseID, ))
					db.commit()

					return redirect(url_for('addNewRideArticle', articleID="new"))
				else:
					articleTitle = request.form['articleTitle']
					articleContents = request.form['articleContents']
					articleDatabaseID = request.form['articleDatabaseID']

					db = get_db()
					cur = db.execute('update past_rides set title = ?, contents = ? where id = ?', 
									 (articleTitle, articleContents, articleDatabaseID))
					db.commit()

			return redirect(url_for('addNewRideArticle', articleID=articleID))

		else:
			return redirect(url_for('login'))
	if request.method == "GET":
		if 'username' in session:
			if articleID == "new":
				articleInformation = {"id": "new", "title":"", "contents":""}
				return render_template('add-new-ride.html', articleInformation=articleInformation)
			else:
				#Valid Article ID
				db = get_db()
				cur = db.execute('select * from past_rides where id = ?', (articleID, ))
				results = cur.fetchall()
				results = results[0]

				return render_template('add-new-ride.html', articleInformation=results)
			# Need to add a catch for an invalid ID later that will redirect somewhere
		else:
			return redirect(url_for('login'))

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

@app.route('/admin/manage-rider-bios', methods=["GET"])
def manageRiderBios():
	if 'username' in session:
		db = get_db()
		cur = db.execute('select * from rider_bios')
		riderBios = cur.fetchall()
		return render_template('edit_rider_bios.html', riderBios=riderBios)
	else:
		return redirect(url_for('login'))

@app.route('/admin/putNewRiderBio', methods=["POST"])
def putNewRiderBio():
	if 'username' in session:
		# Verify the uploaded information is correct
		if 'riderPictureFile' not in request.files:
			return redirect(url_for('manageRiderBios'))
		riderName = request.form['riderNameInput']
		riderBio = request.form['riderBioInput']
		file = request.files['riderPictureFile']
		fileName = secure_filename(file.filename)
		if riderName == "" or riderBio == "" or fileName == "":
			return redirect(url_for('manageRiderBios'))
			print("We had a problem")

		# Save all necessary info in the database
		db = get_db()
		cur = db.execute('insert into rider_bios (name, bio, picture) values (?, ?, ?)', (riderName, riderBio, fileName))
		db.commit()

		# Upload the file to the server
		if file and utils.allowedFile(fileName):
				file.save(os.path.join(UPLOAD_FOLDER, fileName))
				utils.saveThumbnail(fileName, UPLOAD_FOLDER, THUMBNAIL_FOLDER)
				return redirect(url_for('manageRiderBios'))
	else:
		return redirect(url_for('login'))

@app.route('/admin/updateRiderBio', methods=["POST"])
def updateRiderBio():
	if 'username' in session:
		# If the delete checkbox is checked, delete that rider.
		if 'deleteRider' in request.form and 'riderID' in request.form:
			db = get_db()
			cur = db.execute('delete from rider_bios where id = (?)',(request.form['riderID']))
			db.commit()
			return redirect(url_for('manageRiderBios'))

		# Since it's not a deletion, it must be an edit
		riderName = request.form['riderName']
		riderBio = request.form['riderBio']
		riderID = request.form['riderID']
		fileName = request.form['originalFilename']
		# Check if a new filel was uploaded
		if 'riderPictureUpload' in request.files:
			if request.files['riderPictureUpload']:
				print("In Here.")
				print(request.files)
				file = request.files['riderPictureUpload']
				fileName = secure_filename(file.filename)
				file.save(os.path.join(UPLOAD_FOLDER, fileName))
				utils.saveThumbnail(fileName, UPLOAD_FOLDER, THUMBNAIL_FOLDER)

		db = get_db()
		cur = db.execute('update rider_bios SET name = (?), bio = (?), picture = (?) WHERE id = (?)', (riderName, riderBio, fileName, riderID))
		db.commit()

		return redirect(url_for('manageRiderBios'))

	else:
		return redirect(url_for('login'))