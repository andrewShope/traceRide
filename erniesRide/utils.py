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

def centerSums(db):
	centerDict = {}
	centers = ["Elizabeth's New Life Center", "Community Pregnancy Center"]
	for center in centers:
		cur = db.execute("select pledge from entries where donationCenter=(?)", [center])
		pledges = cur.fetchall()
		centerDict[center] = sumPledges(pledges)

	return centerDict

def validateEmail(emailAddress):
	return True

def validateCurrency(num):
	num = float(num)
	if num > 0:
		return True
	else:
		return False

def validateFields(city, state, firstName, lastName, emailAddress, pledgeAmount):
	flag = True
	if not validateEmail(emailAddress):
		flag = False
	if not validateCurrency(pledgeAmount):
		flag = False

	return flag
