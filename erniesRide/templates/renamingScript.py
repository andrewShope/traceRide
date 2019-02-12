def main():
	newFile = open('newFile.html', 'w')
	with open('ride_2017.html') as f:
		for line in f:
			if "static/images" in line:
				startIndex = line.find('"') + 1
				endIndex = line.find('"', startIndex)
				print(type(startIndex))
				print(type(endIndex))
				fileLocation = line[startIndex:endIndex]
				fileName = fileLocation.split("/")[2]
				newLine = line[:startIndex] + makeNewString(fileName) + line[endIndex:] + "\n"
				newFile.write(newLine)
			else:
				newFile.write(line)


def makeNewString(fileName):
	return "{{{{url_for('static', filename='images/{0}')}}}}".format(fileName)

if __name__ == "__main__":
	main()