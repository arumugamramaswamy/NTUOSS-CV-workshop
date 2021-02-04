# NTUOSS TGIFHacks CV Workshop
## Goal
Implement the vision pipeline for a line following Robot.

## Setup - Computer Vision with OpenCV

### Step 1 - Clone the git repo

```sh
git clone https://github.com/arumugam666/NTUOSS-CV-workshop.git
```
### Step 2 - Setup the development environment
Windows:
```sh
cd NTUOSS-CV-workshop; python -m venv workshop-env; .\workshop-env\Scripts\activate; python -m pip install -r requirements.txt
```

Mac/ Linux:
```sh
cd NTUOSS-CV-workshop; python3 -m venv workshop-env; source workshop-env/bin/activate; python3 -m pip install -r requirements.txt
```
## Loading, Displaying and Writing images

An image can be loaded using the below code snippet
```python
import cv2
img = cv2.imread("./Images/cat.jpg")
```

The image can be diplayed using the `cv2.imshow` function
```python
cv2.imshow("cat", img)
cv2.waitKey(0)
```

The image can be written using the `cv2.imwrite` function
```python
cv2.imwrite("./Images/cat-copy.jpg", img)
```
## Working with the webcam

The webcam can be accessed using the following code snippet:
```python
import cv2

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("webcam", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
```
## Colorspaces - RGB and HSV
![asdf](Images/RGB_HSV.jpeg)

RGB uses 3 variables ranging from 0-255 - one each for Red, Green, and Blue.

HSV on the other hand uses 1 variable for Hue ranging from 0-179 and 2 variables ranging from 0-255 for Saturation and Value.

Because we will be building a blue line following robot, we need to be able to detect only the blue coloured pixels in an image.

In an ideal world, we can just check if the colour of a pixel is 0,0,255 (RGB). As we do not live in an ideal world, we need to get our hands dirty and set a threshold that defines the blue colour.

This is easier to do in the HSV colour space (Imagine cutting a slice out of a cake) as compared to doing so in the RGB colour space.

### Converting from RGB to HSV

```python
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
```

### Thresholding using HSV values

We first manually define the lower and upper tresholds to define "Blue". (Please feel free to tune these parameters)

We then find all the pixels which are in this range and generate a mask from them.

This mask can then be applied to the original image to obtain only the blue portions of the image.
```python
# Normal masking algorithm
blue_lower = np.array([89,154,0], np.uint8)
blue_upper = np.array([140,255,255], np.uint8)

# creating mask
blue_mask = cv2.inRange(hsv_img, blue_lower, blue_upper)
blue_mask = blue_mask.astype('bool')

# apply mask
masked_img = img * np.dstack((blue_mask, blue_mask, blue_mask)
```

## Preprocessing

Before we can extract any information from the image about the line to follow, we must first preprocess the image.

We will do so by converting the masked image to a grayscale image and then apply a fixed gray level threshold.

The results of this thresholding can then be used in contour detection.

```python
# convert to gray
imgray = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)

# threshold
ret, thresh = cv2.threshold(imgray, 50, 255, 0)
```

## Contour detection

Now, we can detect the contours in the thresholded image. Contours are regions that have same/similar intensities in an image.

```python
# detect contours
contours,heir = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# find contour with max area
c = max(contours, key = cv2.contourArea)
```
## Choose which direction to rotate to stay centered on the line

We have to find the top left and bottom left points in the largest contour so that we can choose which direction to turn.

```python
upper1 = 10000
upper2 = 10000
upind = [-1, -1]
center = np.array([0, 0])

# find top two points
for ind, coords in enumerate(box):
    center += coords
    if coords[1] <= upper1:
        upper2 = upper1
        upper1 = coords[1]
        upind[1] = upind[0]
        upind[0] = ind
    elif coords[1] <= upper2:
        upper2 = coords[1]
        upind[1] = ind

# find top left point
if box[upind[0]][0] < box[upind[1]][0]:
    up_left = upind[0]
else:
    up_left = upind[1]

# infer bottom two points
bottomind = [x for x in range(4) if x not in upind]

# find bottom left point
if box[bottomind[0]][0] < box[bottomind[1]][0]:
    bottom_left = bottomind[0]
else:
    bottom_left = bottomind[1]
```