from PIL import Image
import os

imagePath = "static/images/"
thumbPath = "static/thumbnails/"

fileList = os.listdir(imagePath)
maxsize = 600
thumbList = os.listdir(thumbPath)

for file in fileList:
	# Make sure it's a file and not a directory
	if len(file.split(".")) > 1:
		print("Resizing " + file)
		im = Image.open(os.getcwd() + "/" + imagePath + file)
		largestSide = max(im.width, im.height)
		factor = largestSide/600
		im_resized = im.resize((int(im.width//factor), int(im.height//factor)))
		im_resized.save(os.getcwd() + "/" + thumbPath+file)