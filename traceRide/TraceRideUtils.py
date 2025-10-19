import os

thumbPath = "/erniesRide/static/thumbnails/"
imagePath = "/erniesRide/static/images/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def getRiders(db):
	"""Returns a list containing the name of each
	rider in the db
	"""
	cur = db.execute('select riderName from riders')
	return cur.fetchall()

def sumTotal(db):
	cur = db.execute('select pledge from entries order by id desc')
	entries = cur.fetchall()
	return sumPledges(entries)

def sumPledges(rows):
	"""Will take the entries from the database that are in the form
	of a tuple and sum together the pledge amounts
	"""
	dbTuple = rows
	total = 0
	for entry in dbTuple:
		pledge = entry[0]
		try:
			float(pledge)
			total += pledge
		except:
			pass
	total = "{0:.2f}".format(total)
	return total

def riderSums(db):
	"""Returns a dictionary where the key is the rider's
	name and the value is the sum of the pledges
	attributed to that rider
	"""
	riderDict = {}
	riders = getRiders(db)
	for rider in riders:
		cur = db.execute("select pledge from entries where riderName=(?)", [rider[0]])
		pledges = cur.fetchall()
		riderDict[rider[0]] = sumPledges(pledges)

	return riderDict

def validateEmail(emailAddress):
	return True

def validateCurrency(num):
	num = float(num)
	if num > 0:
		return True
	else:
		return False

def validateFields(city, state, firstName, lastName, emailAddress, pledgeAmount, riderName, db):
	flag = True
	if not validateEmail(emailAddress):
		flag = False
	if not validateCurrency(pledgeAmount):
		flag = False
	if not validateRider(riderName, db):
		flag = False

	return flag

def validateCenter(centerName):
	centers = ["Elizabeth's New Life Center", "Community Pregnancy Center", "Family Life Center of Auglaize County", "Hope Rising Pregnancy Center"]
	if centerName in centers:
		return True
	else:
		return False

def validateRider(riderName, db):
	riders = getRiders(db)
	namesList = [rider[0] for rider in riders]
	if riderName in namesList:
		return True
	else:
		return False

def rowToSiteInfoDict(rows):
	'''
	Takes a sqlite row object and creates a 
	dictionary where the key is the first index
	of each row and the value is the respective
	second index
	'''
	d = {}
	for row in rows:
		d[row["title"]] = row["contents"]
	return d

def getSiteInfo(db):
	'''
	Returns the site_info table as a dictionary
	'''
	cur = db.execute('select * from site_info')
	siteInfo = cur.fetchall()
	siteInfo = rowToSiteInfoDict(siteInfo)
	# cur = db.execute('select title from articles')
	# siteInfo["articles"] = cur.fetchall()
	
	return siteInfo

def allowedFile(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def saveThumbnail(filename, imagePath, thumbnailFolderPath):
	im = Image.open(os.path.join(imagePath, filename))
	largestSide = max(im.width, im.height)
	factor = largestSide/600
	im_resized = im.resize((int(im.width//factor), int(im.height//factor)))
	im_resized.save(os.path.join(thumbnailFolderPath, filename))

	return True


