import cv2
import time
import platform
import threading
from ultralytics import YOLO


class Eyes:
    def __init__(self, fps=3, scale=1, buffer_size=5, result_threshold=3) -> None:
        print(f"Eyes initialized with fps: {fps}, scale: {scale}, buffer_size: {buffer_size}, result_threshold: {result_threshold}")
        self.yolo_fps = 1 # how many frames per second to run the yolo detection
        self.yolo_model = YOLO("yolo11n.pt") # decide what model to use, n is the lightweight model
        self.scale = 1
        self.running = True
        self.frame = None
        self.read_thread = threading.Thread(target=self.read_frame)
        self.read_thread.start()
        self.yolo_thread = threading.Thread(target=self.yolo_detect)
        self.yolo_thread.start()

        self.yolo_result = None # the result of the yolo detection
        self.yolo_result_list = [] # yolo detection results container
        
        self.buffer_list = [] # container to hold a few secs of results
        self.buffer_size = buffer_size #size of the buffer
        self.result_threshold = result_threshold #threshold to consider a person detected
        self.buffered_result = None # the result after considering the buffer (bool)

    def read_frame(self):
        '''
        Read a frame from the camera and write it to the video writer
        '''
        # Open the video capture device (camera)
        if platform.system() == 'Darwin':
            cap_ = cv2.VideoCapture(0)
        elif platform.system() == 'Linux':
            cap_ = cv2.VideoCapture(-1)
        
        # Check if the camera is opened correctly
        if not cap_.isOpened():
            print("Failed to open camera")
            return

        start_time = time.time()
        while self.running:
            # print("reading frame")
            # Read a frame from the camera
            ret_, self.frame = cap_.read()
            s = time.time()
            
            # Check if the frame was successfully read
            if not ret_:
                print("Failed to capture frame", 0)
                break
            
            # Resize frame based on scale factor
            if self.scale != 1 and self.frame is not None:
                old_shape = self.frame.shape
                self.frame = cv2.resize(self.frame, None, fx=self.scale, fy=self.scale)
                print(f"Resized frame from {old_shape[1]}x{old_shape[0]} to {self.frame.shape[1]}x{self.frame.shape[0]}")

            duration = time.time() - start_time
            diff = time.time() - s
            time.sleep(max(0, 1/self.yolo_fps*1.5 - diff))
 
            
        # Release the video capture device and close the window
        print("Read frame done")
        cap_.release()
        cv2.destroyAllWindows()

    def yolo_detect(self):
        '''
        Detect objects in the frame using YOLOv8
        Also updates various key variables for obs detection
        '''
        while self.running:
            if self.frame is not None:
                s = time.time()
                self.result_list = []
                self.yolo_result = self.yolo_model.predict(source=self.frame, save=False, device='cpu')
                for i, r in enumerate(self.yolo_result):
                    self.result_list.append(
                        {
                            "boxes_xyxy": r.boxes.xyxy.tolist(),
                            "boxes_conf": r.boxes.conf.tolist(),
                            "boxes_cls": r.boxes.cls.tolist()
                        }
                    )

                diff = time.time() - s
                print("-"*100)
                print(f"===== BUFFERED RESULT: {self.update_buffered_result()} =====")
                print(f"YOLO | sleep: {max(0, 1/self.yolo_fps - diff):.2f}s (target: {1/self.yolo_fps:.2f}s) | fps: {1/diff:.2f}")
                print("-"*100)
                time.sleep(max(0, 1/self.yolo_fps - diff))

        print("YOLO detection done")

    def update_buffered_result(self):
        '''
        Update the buffered result based on the YOLO results based on the buffer size and the result threshold
        
        Returns:
            bool: True if person detected, False otherwise
        '''
            
        for result in self.result_list: # digest the result list
            if 0 in result["boxes_cls"]:  # Check if person (class 0) is in detected classes
                self.buffer_list.append(True)
            else:
                self.buffer_list.append(False)
            
        if len(self.buffer_list) >= self.buffer_size: # remove the oldest result
            self.buffer_list = self.buffer_list[1:]

        if sum(self.buffer_list) >= self.result_threshold: # if the number of True in the buffer is greater than the threshold
            self.buffered_result = True
        else:
            self.buffered_result = False

        return self.buffered_result

      

if __name__ == "__main__":
    yolo = Eyes()
