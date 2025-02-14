import cv2
import time
import platform
import threading
from ultralytics import YOLO


class Eyes:
    def __init__(self) -> None:
        self.yolo_result = None # the result of the yolo detection
        self.yolo_fps = 3 # how many frames per second to run the yolo detection
        self.yolo_model = YOLO("yolo11n.pt") # decide what model to use, n is the lightweight model

        self.done = False
        self.max_run_time = 100000
        self.frame = None
        self.read_thread = threading.Thread(target=self.read_frame)
        self.read_thread.start()
        self.yolo_thread = threading.Thread(target=self.yolo_detect)
        self.yolo_thread.start()

    def read_frame(self):
        '''
        Read a frame from the camera and write it to the video writer
        '''
        # Open the video capture device (camera)
        if platform.system() == 'Darwin':
            cap_ = cv2.VideoCapture(0)
        elif platform.system() == 'Linux':
            cap_ = cv2.VideoCapture(-1)
        # cap_ = cv2.VideoCapture(cam_id)
        # cap_.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # type: ignore
        # cap_.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # cap_.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # cap_.set(cv2.CAP_PROP_FPS, 30)
        
        # Check if the camera is opened correctly
        if not cap_.isOpened():
            print("Failed to open camera")
            return

        start_time = time.time()
        while not self.done:
            # print("reading frame")
            # Read a frame from the camera
            ret_, self.frame = cap_.read()
            s = time.time()
            
            # Check if the frame was successfully read
            if not ret_:
                print("Failed to capture frame", 0)
                break

            duration = time.time() - start_time
            diff = time.time() - s
            time.sleep(max(0, 1/self.yolo_fps*1.5 - diff))
            # print("="*100)
            # print(f"sleep: {max(0, 1/self.yolo_fps*1.5 - diff):.2f}s | fps: {1/diff:.2f}")
            # print("="*100)
            if duration > self.max_run_time*60: # stop the program when it reach max run time
                self.done = True
                break
            
        # Release the video capture device and close the window
        print("Read frame done")
        cap_.release()
        cv2.destroyAllWindows()

    def yolo_detect(self):
        '''
        Detect objects in the frame using YOLOv8
        Also updates various key variables for obs detection
        '''
        while not self.done:
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
                print(f"YOLO | sleep: {max(0, 1/self.yolo_fps - diff):.2f}s (target: {1/self.yolo_fps:.2f}s) | fps: {1/diff:.2f}")
                print("-"*100)
                time.sleep(max(0, 1/self.yolo_fps - diff))

        print("YOLO detection done")

if __name__ == "__main__":
    yolo = Eyes()
