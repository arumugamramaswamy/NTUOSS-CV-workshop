import cv2
import numpy as np

BLUE_LOWER = np.array([89, 154, 0], np.uint8)
BLUE_UPPER = np.array([140, 255, 255], np.uint8)
DIRECTION_THRESHOLD = 10


def mask_image(hsv_img, img):

    # creating mask
    blue_mask = cv2.inRange(hsv_img, BLUE_LOWER, BLUE_UPPER)
    blue_mask = blue_mask.astype("bool")

    # apply mask
    masked_img = img * np.dstack((blue_mask, blue_mask, blue_mask))

    return masked_img


def apply_threshold(img):
    # convert to gray
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # DIRECTION_THRESHOLD
    ret, thresh = cv2.threshold(imgray, 50, 255, 0)

    return thresh


def process_contours(contours, img):
    # find contour with max area
    c = max(contours, key=cv2.contourArea)

    # Green color in BGR
    color = (0, 255, 0)

    # Line thickness of 9 px
    thickness = 2

    # find bounding rectangle
    rect = cv2.minAreaRect(c)

    box = cv2.boxPoints(rect)
    box = np.int0(box)
    if len(box) > 0:
        ret_img = cv2.drawContours(img, [box], 0, color, thickness)

        return ret_img, box


def find_direction(box):
    # initialise upper1 and upper2 and upind and center
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

    # output yaw command
    thickness = 2
    if (
        DIRECTION_THRESHOLD
        > box[up_left][0] - box[bottom_left][0]
        > -DIRECTION_THRESHOLD
    ):
        print("Just right!")
    elif box[up_left][0] - box[bottom_left][0] > 0:
        print("rotate other way")
    else:
        print("rotate one way")


def pipeline(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    masked_img = mask_image(hsv_img, img)
    thresh = apply_threshold(masked_img)
    contours, heir = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.imshow("thresh", thresh)
    cv2.imshow("masked_img", masked_img)
    if len(contours) > 0:
        contour_img, box = process_contours(contours, img)
        cv2.imshow("contour_img", contour_img)
        find_direction(box)
    pass


if __name__ == "__main__":

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        pipeline(frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
