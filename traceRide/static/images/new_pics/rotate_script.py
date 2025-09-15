import exifread
import os
from PIL import Image
import logging
import traceback

orientationConversion = {
	"Horizontal (normal)": 0,
	"Rotated 90 CCW": 270,
	"Rotated 90 CW": 90,
	"Rotated 180": 180,
	"None": 0
}

def validFile(fileName):
	if len(fileName.split(".")) > 1:
		if fileName.split(".")[1].lower() == "jpg":
			return True
		if fileName.split(".")[1].lower() == "jpeg":
			return True
	return False

for fileName in os.listdir():
	if validFile(fileName):
		file = open(fileName, 'rb')
		exifDict = exifread.process_file(file)
		orientation = str(exifDict.get("Image Orientation"))
		rotationAmount = orientationConversion.get(orientation)
		print(fileName)
		im = Image.open(fileName)
		try:
			print(type(rotationAmount))
			im.rotate(rotationAmount)
			im.save("converted/"+fileName)
		except Exception as e:
			logging.error(traceback.format_exc())
		break
	else:
		print("Rejected: " + fileName)
	