from moviepy.editor import VideoFileClip
import time
import threading
from pynput import keyboard
import os
from yolo import Eyes
from pie_chart import PieChart
from cv2_playback import CV2Player

class VideoController:
    """
    Main controller class that manages video playback, state transitions, and user interactions.
    Handles camera detection and voting system integration.

    workflow that we are trying to achieve:
    - State A: Plays clip A in a loop until camera detects activity.
        if camera detects activity, transition to State B.
    - State B: Plays clip B for 5-10 seconds.
        if vote is detected(T), transition to State Statistics.
        if vote is(F), camera is inactive(F), transition to State A.
        if vote is(F), camera remains active until the end of the clip(T), transition to State C.
    - State C: Plays clip C for 10s.
        if camera is inactive(F), transition to State A.(TODO: NEW)
        if camera remains active until the end of the clip(T), transition to State B(so people can press).
    - Statistics: Displays voting results as pie chart.
        if camera is inactive(F), transition to State A.
        if camera remains active until the end of the clip(T), transition to State A. (TODO: NEW)

    """
    def __init__(self, folder_path):
        """
        Initialize the video controller with required components and state variables
        
        Args:
            folder_path (str): Path to the folder containing video clips
        """
        self.folder_path = folder_path
        self.eyes = Eyes()  # Initialize camera detection
        self.current_state = "A"  # Starting state
        self.cam_active = False  # Camera detection status
        self.vote_active = False  # Voting system status  
        self.running = True  # Main loop control flag
        self.timers = {}  # Store timing information
        self.keyboard_listener = None  # Keyboard input handler
        self.statistics_duration = 10  # Duration to show statistics in seconds

        CLIP_A = os.path.join(self.folder_path, "A.mp4") # #TODO (NEW)initialize player with CLIP A
        self.cv2_player = CV2Player([CLIP_A]) # TODO (NEW) Initialize the cv2 player

        #TODO: add a text file as database to store the opinions
        

        # State transition map - maps states to their handler functions
        self.transitions = {
            "A": self.handle_state_a,
            "B": self.handle_state_b, 
            "C": self.handle_state_c,
            "STATISTICS": self.handle_state_statistics
        }

    def start(self):
        """
        Start the main control loop that manages state transitions and video playback.
        Initializes camera and keyboard listeners before entering the main loop.
        """
        self.start_camera()
        self.start_keyboard_listener()

        while self.running:
            self.update_sensors()  # Update camera and voting status
            self.transitions[self.current_state]() 
            time.sleep(0.1)  # Prevent CPU overload

        self.cleanup()

    def handle_state_a(self):
        """
        State A handler: Plays clip A in a loop until camera detects activity.
        Transitions to State B when camera becomes active.
        """
        self.play_clip("A.mp4", loop=True)

        if self.cam_active:
            print("Transitioning to State B")
            self.current_state = "B"
            self.stop_current_clip()

    def handle_state_b(self):
        """
        State B handler: Plays clip B for 5-10 seconds.
        Transitions:
        - To State A if camera inactive
        - To Statistics if vote detected
        - To State C if camera remains active for 15 seconds
        """
        self.play_clip("B.mp4", duration=(5, 10))

        if not self.cam_active:
            self.current_state = "A"
            return

        if self.vote_active:
            self.current_state = "STATISTICS"
        else:
            if self.check_condition_duration(15):
                self.current_state = "C"

    def handle_state_c(self):
        """
        State C handler: Plays clip C.
        Transitions:
        - To State A if camera inactive
        - To Statistics if vote detected
        - To State B otherwise
        """
        self.play_clip("C.mp4")

        if not self.cam_active:
            self.current_state = "A"
            return

        if self.vote_active:
            self.current_state = "STATISTICS"
        else:
            self.current_state = "B"

    def handle_state_statistics(self):
        """
        Statistics state handler: Displays voting results as pie chart.
        Transitions:
        - To State A if camera inactive
        - To State C if camera remains active
        """
        self.show_statistics()

        if not self.cam_active:
            self.current_state = "A"
        else:
            self.current_state = "C"

    def play_clip_cv2(self, filename, play_immediately=False, show_message=False):
        """
        TODO: (NEW) Play a video clip using OpenCV
        
        Args:
            filename (str): Name of the video file to play
            play_immediately (bool): Whether to play the clip immediately
        """
        thread = threading.Thread(target=self.cv2_player.add_video, args=(os.path.join(self.folder_path, filename), play_immediately))
        thread.start()

    def play_clip(self, filename, loop=False, duration=None):
        """
        Play a video clip with specified parameters
        
        Args:
            filename (str): Name of the video file to play
            loop (bool): Whether to loop the video
            duration (tuple or int): Duration to play the clip, can be (min, max) or fixed duration
        """
        clip = VideoFileClip(os.path.join(self.folder_path, filename))

        if loop:
            clip = clip.loop()
        if duration:
            clip = clip.subclip(0, duration[1] if isinstance(duration, tuple) else duration)

        clip.preview(fps=24)
        clip.close()

    def show_statistics(self):
        """
        Generate and display a pie chart showing voting statistics.
        Creates a temporary video file for the chart animation.
        """
        #TODO: read the database file and update the data
        data = [('Option A', 35), ('Option B', 40), ('Option C', 25)]
        colors = ['#FF0000', '#00FF00', '#0000FF']
        PieChart(data, colors, 50, "temp_piechart.mp4")
        self.play_clip("temp_piechart.mp4", duration=self.statistics_duration)

    def update_sensors(self):
        """Update the status of camera detection and voting system"""
        self.cam_active = self.check_camera_condition()  
        self.vote_active = self.check_vote_condition()

    def check_camera_condition(self):
        """
        Check if camera detects required conditions
        
        Returns:
            bool: True if detection criteria met, False otherwise
        """
        #TODO: introduce a threshold to allow some false negatives frames (yolo could miss a person in the frame)
        return len(self.eyes.result_list) > 0 if self.eyes.yolo_result else False

    def check_vote_condition(self):
        """
        Check if voting is active
        
        Returns:
            bool: Current voting status
        """
        
        return self.vote_active  # Replace with actual vote detection logic

    def check_condition_duration(self, required_duration):
        """
        Check if a condition persists for specified duration
        
        Args:
            required_duration (int): Duration in seconds to check for
            
        Returns:
            bool: True if condition persists for entire duration
        """
        start_time = time.time()
        while time.time() - start_time < required_duration:
            if not self.cam_active or self.vote_active:
                return False
            time.sleep(0.1)
        return True

    def start_keyboard_listener(self):
        """
        Initialize and start keyboard input listener.
        Handles:
        - ESC key to stop program
        - 'v' key to toggle voting status
        """
        #TODO: add keyboard Q, W, E input to toggle each opinion, we can store the opinions in a text file for now 
        #TODO: add sleep time between each opinion to avoid double voting
        def on_press(key):
            if key == keyboard.Key.esc:
                self.running = False
            elif key == keyboard.KeyCode.from_char('v'):
                self.vote_active = not self.vote_active
            elif key == keyboard.KeyCode.from_char('q'): 
                self.vote_active = not self.vote_active 
            elif key == keyboard.KeyCode.from_char('w'):
                self.vote_active = not self.vote_active
            elif key == keyboard.KeyCode.from_char('e'):
                self.vote_active = not self.vote_active

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def start_camera(self):
        """Start camera detection threads if not already running"""
        if not self.eyes.read_thread.is_alive():
            self.eyes.read_thread.start()
        if not self.eyes.yolo_thread.is_alive():
            self.eyes.yolo_thread.start()

    def stop_current_clip(self):
        """Stop the currently playing video clip"""
        # MoviePy doesn't support interrupting previews, need to manage timing
        pass  # Implement proper clip termination if needed

    def cleanup(self):
        """Clean up resources and temporary files before program exit"""
        self.eyes.done = True
        self.keyboard_listener.stop()
        if os.path.exists("temp_piechart.mp4"):
            os.remove("temp_piechart.mp4")


if __name__ == "__main__":
    controller = VideoController("/path/to/video/folder")
    controller.start()