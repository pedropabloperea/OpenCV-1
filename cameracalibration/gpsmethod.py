import cv2;
import numpy as np;
import sys;
import pickle;
from _pygameview_twocameras import *;
from _camerasources import *;
from multiprocessing import Process,Array,Lock,Event;
from optparse import OptionParser;
from math import sqrt;
from _positioning import *; 

from linearalgebratools.matrix44 import *
from linearalgebratools.vector3 import *

# Command line options parser
def parse_options():
	parser = OptionParser();
	parser.add_option("--onecamera", action="store_true", dest="onecamera", help="Use only one camera");
	parser.add_option("--firstsource", type="int", default=0, dest="firstsource", help="First source of video");
	parser.add_option("--firstcalibration", type="string", dest="firstcalibration", help="Calibration data file for the first source of video. If ommited, new calibration will be performed. If not ommited but the file doesn't exist, new calibration will be performed and the data will be saved into the specified file");
	parser.add_option("--secondsource", type="int", default=1, dest="secondsource", help="Second source of video. Incompatible with --onecamera");
	parser.add_option("--secondcalibration", type="string", dest="secondcalibration", help="Calibration data file for the second source of video. If ommited, new calibration will be performed. If not ommited but the file doesn't exist, new calibration will be performed and the data will be saved into the specified file. Incompatible with --onecamera. For one camera, the second calibration data is the same as for the first camera (obviously)");
	parser.add_option("--resolution", type="int", nargs=2, default=(640,480), dest="resolution", help="Cameras resolution");
	parser.add_option("--pattern", type="int", nargs=2, default=(6,3), dest="patternsize", help="Pattern size (inner corners)");
	parser.add_option("--squaresize", type="float", default=1.0, dest="squaresize", help="Square size");
	return parser.parse_args();


def getCorners(img,patternSize):
	corners = None;
	imggs = cv2.cvtColor(img, cv2.cv.CV_RGB2GRAY);
	patternWasFound, corners = cv2.findChessboardCorners(imggs, patternSize, corners, cv2.CALIB_CB_FAST_CHECK);
	
	if patternWasFound:
		criteria = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 );
		cv2.cornerSubPix(imggs, corners, (5, 5), (-1, -1), criteria);
	return patternWasFound,corners;


def distance(v1,v2):
	s = 0.0;
	for i in range(len(v1)):
		s+= pow((v1[i]-v2[i]),2);
	return sqrt(s);

def v2s(vector):
	s = '[';
	for i,v in enumerate(vector):
		if (i>0):
			s+=' ';
		s+= '%5.3f'%v;
	s += ']';
	return s;


if __name__ == "__main__":
	(options, args) = parse_options();
	print "Options: ",options;
	# Create virtual pattern to calibrate
	squareSize = options.squaresize;
	patternSize = options.patternsize;
	patternPoints = np.zeros( (np.prod(patternSize), 3), np.float32 )
	patternPoints[:,:2] = np.indices(patternSize).T.reshape(-1, 2)
	patternPoints *= squareSize
	
	# Creating first camera
	cam1 = CameraSource(options.firstsource, options.resolution);
	# Calibration of the first camera
	if options.firstcalibration:
		cam1.setCalibrationFile(options.firstcalibration, patternPoints,patternSize);
	else:
		cam1.calibrate(patternPoints,patternSize, 10);
		
	# Second camera
	if options.onecamera:
		cam2 = VirtualCameraSource(cam1);
		# Calibration of the virtual camera is just getting the calibration data from the first one
		cam2.calibrate(patternPoints,patternSize, 10);
	else:
		cam2 = CameraSource(options.secondsource, options.resolution);
		if options.secondcalibration:
			cam2.setCalibrationFile(options.secondcalibration, patternPoints,patternSize);
		else:
			cam2.calibrate(patternPoints,patternSize, 10);
	
	rms1, cameraMatrix1, distCoefs1, rvecs1, tvecs1 = cam1.getCalibrationData();
	rms2, cameraMatrix2, distCoefs2, rvecs2, tvecs2 = cam2.getCalibrationData();
			
	# Pygame process
	p = None;
	
	# Arrays for passing data to the process, the lock and the stop event
	R1arr = Array('d',[0.0]*3);
	T1arr = Array('d',[0.0]*3);
	R2arr = Array('d',[0.0]*3);
	T2arr = Array('d',[0.0]*3);
	lock = Lock();
	stopped = Event();
	
	solved1,R1,T1 = None,None,None;
	solved2,R2,T2 = None,None,None;
	
	points = [];
	distances = [];
	while True:
		key = cv2.waitKey(10);
		key = -1 if key == -1 else key & 255;
		if (key == KEY_ESC or key == KEY_Q):
			stopped.set();
			print "Quiting...";
			break;
			
			
		img1 = cam1.read();
		img2 = cam2.read();
		w,h = options.resolution;
		
		patternWasFound1,corners1 = getCorners(img1, patternSize);
		patternWasFound2,corners2 = getCorners(img2, patternSize);
		
		cv2.drawChessboardCorners(img1, patternSize, corners1, patternWasFound1);
		cv2.drawChessboardCorners(img2, patternSize, corners2, patternWasFound2);
		
		# Draw the cameras centers
		cv2.circle(img1,(int(cameraMatrix1[0][2]),int(cameraMatrix1[1][2])),10,(255,255,0),2);
		cv2.circle(img2,(int(cameraMatrix2[0][2]),int(cameraMatrix2[1][2])),10,(255,255,0),2);
		
		# Show images
		cv2.imshow("First source",img1);
		cv2.imshow("Second source",img2);

		
		
		if patternWasFound1 and patternWasFound2:			
			result1 = cv2.solvePnP(patternPoints, corners1, cameraMatrix1, distCoefs1);
			result2 = cv2.solvePnP(patternPoints, corners2, cameraMatrix2, distCoefs2);
			
			 
			# Workaround because in 2.4.0 solvePnP returns 3 values
			if (len(result1) == 2):
				R1,T1 = result1;
				solved1 = True;
				R2,T2 = result2;
				solved2 = True;
			else:
				solved1,R1,T1 = result1;
				solved2,R2,T2 = result2;
				
				
			if key == KEY_SPACE:
				print "Capturing this point";
				points.append(T1);
				distances.append(np.sqrt(T1[0]**2+T1[1]**2+T1[2]**2));
				
				print points;
				print distances;
				
				if len(points) == 4:
					print "solving position:";
					print getPosition(points[0],points[1],points[2],points[3],distances[0],distances[1],distances[2],distances[3]);
					
#				
#			 Send data to the process
#			lock.acquire();
#			R1arr[:] = R1;
#			T1arr[:] = T1;
#			R2arr[:] = R2;
#			T2arr[:] = T2;
#			lock.release();
#			
#			rot1 = Matrix44.rotation_about_axis(R1,-);
#			print rot1;
#			tvec1 = rot1.rotate(Vector3(T1)*-1);
#			rot2 = Matrix44.rotation_about_axis(R2,-np.sqrt(R2[0]**2+R2[1]**2+R2[2]**2));
#			tvec2 = rot2.rotate(Vector3(T2)*-1);
			
#			print tvec1;
#			print tvec2;
#			print "Dtvec: ",distance(tvec1,tvec2);
#			
#			
#			
#			print ;
#			print "Distance: ",distance(T1,T2);
#			print "T1: "+v2s(T1);
#			print "T2: "+v2s(T2);
			
			# Check if process is started
			if False:
				p = Process(target=pygameProcess, args=(R1arr,T1arr,R2arr,T2arr,lock,stopped));
				p.start();
		
