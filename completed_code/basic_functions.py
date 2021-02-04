import cv2

# Reading an image
img = cv2.imread("./Images/cat.jpg")

# Displaying an image
cv2.imshow("cat", img)
cv2.waitKey(0)

# Writing an image
cv2.imwrite("./Images/cat-copy.jpg", img)
