import cv2

cap = cv2.VideoCapture('./footages/A_8.mp4')
cv2.namedWindow("video", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    cv2.imshow("video", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyWindow("video")