import cv2

im = cv2.imread(cv2.samples.findFile("lena.jpg"))
cv2.namedWindow("foo", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("foo", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("foo", im)
cv2.waitKey()
cv2.destroyWindow("foo")