import pytesseract
import numpy as np
import cv2 as cv

img = cv.imread('/Users/joshua/Desktop/NEN archives/1983_04 April/20200623_0029.jpg')

gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
# gray, img_bin = cv.threshold(gray, 50, 100, cv.THRESH_BINARY | cv.THRESH_OTSU)
# gray = cv.bitwise_not(img_bin)

kernel = np.ones((2, 1), np.uint8)

img = cv.erode(gray, kernel, iterations=1)

img = cv.dilate(img, kernel, iterations=1)

out_below = pytesseract.image_to_string(img)
cv.imshow('', img)
print(out_below)
cv.waitKey(0)
