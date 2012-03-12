import cv2;
import sys;
import numpy as np;

# Joins various images into one
# Argument: list of lists of images (rows of columns)
def joinImages (images):
	w = images[0][0].shape[1];
	h = images[0][0].shape[0];
	img = np.zeros((len(images)*h, len(images[0])*w,3), np.uint8);
	for i in range(len(images)):
		for j in range(len(images[0])):
			if (images[i][j] != None):
				if(len(images[i][j].shape) == 3):
					img[i*h:(i+1)*h,j*w:(j+1)*w] = images[i][j];
				else:
					for k in range(3):
						img[i*h:(i+1)*h,j*w:(j+1)*w,k] = images[i][j];
					
	return img;

# Labels various images
#
def labelImages(images, labels, toggleLabels):
	if (toggleLabels):
		for i in range(len(images)):
			cv2.putText(images[i],labels[i],(int(images[i].shape[1]*0.1),int(images[i].shape[0]*0.9)),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),5);
			cv2.putText(images[i],labels[i],(int(images[i].shape[1]*0.1),int(images[i].shape[0]*0.9)),cv2.FONT_HERSHEY_SIMPLEX,0.7,1,1);
	return images;

if __name__ == "__main__":
	print "Press T to toggle frame names.";
	print "Usage: ";
	print "    split.py filename               for filename"
	print "    slpit.py N                      for camera /dev/videoN"
	toggleLabels = False;
	video = False;
	filename = '../img/stop.jpg';
	cam = False;
	
	img = None;
	if (len(sys.argv)>1):
		if (len(sys.argv[1])  == 1):
			video = True;
			
			cam = cv2.VideoCapture(int(sys.argv[1]));
			cam.set(3, 320);
			cam.set(4, 240);
		else:
			filename = sys.argv[1];
	if (not video):
		img = cv2.imread(filename);	
	original = None;
	cv2.namedWindow('testwindow');
	
	while True:		
		if (video):
			f,img = cam.read();
		while (img.shape[1] > 320 or img.shape[0] > 350):
			img = cv2.pyrDown(img);
	
		imgB, imgG, imgR = cv2.split(img);
		imgHSV = cv2.cvtColor(img, cv2.cv.CV_RGB2HSV);
		imgH, imgS, imgV = cv2.split(imgHSV);
		[original] = labelImages([img.copy()],['original'], toggleLabels);
		
		hrgb = np.zeros(img.shape);
		hhsv = np.zeros(img.shape);
		bins = np.arange(256).reshape(256,1);
		color = [ (255,0,0),(0,255,0),(0,0,255) ];		

		for item,col in zip([imgR,imgG,imgB],color):
			hist_item = cv2.calcHist([item],[0],None,[256],[0,255])
			cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
			hist=np.int32(np.around(hist_item))
			pts = np.column_stack((bins,hist))
			cv2.polylines(hrgb,[pts],False,col)
			
		for item,col in zip([imgH,imgS,imgV],color):
			hist_item = cv2.calcHist([item],[0],None,[256],[0,255])
			cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
			hist=np.int32(np.around(hist_item))
			pts = np.column_stack((bins,hist))
			cv2.polylines(hhsv,[pts],False,col)
			
		
		imgB,imgG, imgR = labelImages([imgB,imgG,imgR], ['blue','green','red'], toggleLabels);
		imgH, imgS, imgV = labelImages([imgH,imgS,imgV], ['hue','saturation','value'], toggleLabels);	
		output = joinImages([[imgR, imgG, imgB],[imgH,imgS,imgV],[original,hrgb,hhsv]]);
		
		
		cv2.imshow('testwindow', output);
		
		key = cv2.waitKey(5);
		if(key != -1):	
			if (key == 116): #T
				toggleLabels = not toggleLabels;
			else:
				print "Key "+str(key)+" pressed. Exiting.";
				break;

			