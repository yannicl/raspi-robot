#
# Compute perspective matrix. This matrix is used to unwrap observed position in the image to physical position in the room.
#
# Step : Identify 4 points in the room
# Step : Find the coordinates in the images (pts1)
# Step : Measure physical coordinates in the room (pts2)
#
# Using an offset, the upper-left point will be mapped to (xoffset, yoffset)

import cv2
import numpy as np;
xoffset = 100
yoffset = 100
scale = 1

img = cv2.imread('ss_large_ref.png')
rows,cols,ch = img.shape
pts1 = np.float32([[570.5,199.5],[1084,186.5],[561,439],[1211.5,419.5]])
pts2 = np.float32([[0+xoffset,0+yoffset],[167.64+xoffset,0+yoffset],[0+xoffset,119.38+yoffset],[167.64+xoffset,119.38+yoffset]])
pts2 = pts2 * scale
M = cv2.getPerspectiveTransform(pts1,pts2)
dst = cv2.warpPerspective(img,M,(cols,rows))

print M

cv2.imshow('original',img)
cv2.imshow('wrapped',dst)

cv2.waitKey(0)
cv2.destroyAllWindows()

#
# Compute physical position from image position
#
# Step : Pick an image point
# Step : Use formula involving perspective matrix to compute physical position
#
#

x = 850
y = 297
print "---"
print (M[0][0]* x + M[0][1] * y + M[0][2]) / (M[2][0]* x + M[2][1] * y + M[2][2])
print (M[1][0]* x + M[1][1] * y + M[1][2]) / (M[2][0]* x + M[2][1] * y + M[2][2])

