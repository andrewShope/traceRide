def sumPledges(db):
	"""Will take the entries from the database that are in the form
	of a tuple and sum together the pledge amounts
	"""
	cur = db.execute('select email, pledge from entries order by id desc')
	entries = cur.fetchall()
	dbTuple = entries
	total = 0
	for entry in dbTuple:
		pledge = entry[1]
		print(pledge)
		try:
			float(pledge)
			total += pledge
		except:
			pass
	total = "{0:.2f}".format(total)
	return total

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
