import cv2
import numpy as np;
 

# Setup SimpleBlobDetector parameters.
def createSimpleBlobDetectorParams():
	params = cv2.SimpleBlobDetector_Params()

	params.filterByColor = False
	params.blobColor = 255;

	# Change thresholds
	params.minThreshold = 100;
	params.maxThreshold = 256;
	 
	# Filter by Area.
	params.filterByArea = True
	params.minArea = 9
	 
	# Filter by Circularity
	params.filterByCircularity = True
	params.minCircularity = 0.5
	 
	# Filter by Convexity
	params.filterByConvexity = False
	params.minConvexity = 0.5
	 
	# Filter by Inertia
	params.filterByInertia = False
	params.minInertiaRatio = 0.5
	
	return params



def exploreAroundKeypointAndComputeMean(keypoint, img):
	mean = np.multiply(img[0,0], 0.0)
	#print mean
	radius = int(keypoint.size)
	#print radius
	keyptx = int(keypoint.pt[0]+1)
	#print keyptx
	keypty = int(keypoint.pt[1]+1)
	#print keypty
	n = 0
	for x in xrange(keyptx - radius, keyptx + radius):
		for y in xrange(keypty - radius, keypty + radius):
			mean = np.add(mean, img[y, x])
			#print img[y, x]
			img[y,x] = [0,255,0]
			n = n + 1
	#print n
	return np.divide(mean, n)
	
def distance(mean, color):
	return np.linalg.norm(mean-color)

def processKeypoints(keypoints, img, refPt):
	distances = [];
	for keypoint in keypoints:
		mean = exploreAroundKeypointAndComputeMean(keypoint, img);
		distances.append([distance(mean, [255,0,0]), distance(mean, [0,0,255])])
	if (len(distances) >= 2) :
		prob_1st_red = distances[0][0] / (distances[0][0] + distances[1][0]) - distances[0][1] / (distances[0][1] + distances[1][1])
		diameter = computeDiameter(keypoints[0].pt, keypoints[1].pt, refPt)
		if (prob_1st_red > 0):
			print toString(keypoints[0].pt, refPt, "R") + ", " + toString(keypoints[1].pt, refPt, "B") + " D {:d}".format(int(round(diameter)))
		else :
			print toString(keypoints[1].pt, refPt, "R") + ", " + toString(keypoints[0].pt, refPt, "B") + " D {:d}".format(int(round(diameter)))
		return [keypoints[0].pt[0]+refPt[0], keypoints[0].pt[1]+refPt[1]]
	else :
		print "No match"
		return False
		

def processImage(img, refPt):
	
	img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY )

	#simple threshold
	ret,img_thresh = cv2.threshold(img_gray,140,255,cv2.THRESH_BINARY)
	img_thresh_2 = cv2.dilate(img_thresh, np.ones((3, 3)))

	# Set up the detector with default parameters.
	params = createSimpleBlobDetectorParams()
	
	ver = (cv2.__version__).split('.')
	if int(ver[0]) < 3 :
		detector = cv2.SimpleBlobDetector(params)
	else : 
		detector = cv2.SimpleBlobDetector_create(params)
 
	# Detect blobs.
	keypoints = detector.detect(img_thresh_2)
	
	return processKeypoints(keypoints, img, refPt)
	
def toString(pt, refPt, color):
		unwrappedPt = unwrap(pt, refPt)
		return color + "({:d},{:d})".format(int(round(unwrappedPt[0]+1)), int(round(unwrappedPt[1]+1)))
	
def unwrap(pt, refPt):
	M = [[4.21412876e-01,1.63141220e-01,-1.43069743e+02],[2.20151807e-02,9.69559655e-01,-7.60938354e+01],[1.17752302e-05,1.46472177e-03,1.00000000e+00]]
	x = pt[0] + refPt[0]
	y = pt[1] + refPt[1]
	x2 = (M[0][0]* x + M[0][1] * y + M[0][2]) / (M[2][0]* x + M[2][1] * y + M[2][2])
	y2 = (M[1][0]* x + M[1][1] * y + M[1][2]) / (M[2][0]* x + M[2][1] * y + M[2][2])
	return [x2, y2]

def computeDiameter(pt1, pt2, refPt):
	return np.linalg.norm(np.subtract(unwrap(pt1, refPt), unwrap(pt2, refPt)))
		
		
# Load background, reference frame without the robot
background = cv2.imread('ss_large_000000.png')
background_gray = cv2.cvtColor( background, cv2.COLOR_RGB2GRAY )
ret,background_gray_t = cv2.threshold(background_gray,100,255,cv2.THRESH_BINARY)
excluded_area = cv2.dilate(background_gray_t, np.ones((6, 6)))


# Iterate on collection
explorationZone=[100,100]
pt = False
for i in range(1, 354):
	filename = "ss_large_%06d.png" % i
	print "Processing %s ..." % filename
	img = cv2.imread(filename)
	if (not pt):
		pt = processImage(img, [0,0])
	else :
		xmin = max(0, int(round(pt[0]))-explorationZone[0])
		ymin = max(0, int(round(pt[1]))-explorationZone[1])
		xmax = min(1295, int(round(pt[0]))+explorationZone[0])
		ymax = min(971, int(round(pt[1]))+explorationZone[1])
		print "{:d},{:d},{:d},{:d}".format(xmin,ymin,xmax,ymax)
		filename = "min_%06d.png" % i
		cv2.imwrite(filename, img[ymin:ymax, xmin:xmax])
		pt = processImage(img[ymin:ymax, xmin:xmax], [xmin, ymin])

