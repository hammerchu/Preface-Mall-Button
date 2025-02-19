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

    def __init__(self, use_eyes=True, working_folder="./", votes_file="data/votes.txt", eye_parms=None):
        """
        Initialize the video controller with required components and state variables

        Args:
            folder_path (str): Path to the folder containing video clips
        """
        self.working_folder = working_folder
        # self.folder_path = folder_path
        # self.eyes = Eyes()  # Initialize camera detection
        if use_eyes:
            self.eyes = Eyes(*eye_parms)
        else:
            self.eyes = None
        self.current_state = "A"  # Starting state

        self.A_video_path = os.path.join(self.working_folder, "footages/A_8.mp4")
        self.B_video_path = os.path.join(self.working_folder, "footages/B_8.mp4")
        self.C_video_path = os.path.join(self.working_folder, "footages/C_8.mp4")
        self.D_video_path = os.path.join(self.working_folder, "footages/D_8.mp4")
        print(f"A_video_path: {self.A_video_path}")
        print(f"B_video_path: {self.B_video_path}")
        print(f"C_video_path: {self.C_video_path}")
        print(f"D_video_path: {self.D_video_path}")

        self.cam_active = False  # Camera detection status
        self.vote_active = False  # Voting system status
        self.running = True  # Main loop control flag
        self.timers = {}  # Store timing information
        self.keyboard_listener = None  # Keyboard input handler
        self.statistics_duration = 10  # Duration to show statistics in seconds
        self.votes_file = os.path.join(self.working_folder, "data/votes.txt")
        self.last_vote_time = 0
        self.vote_cooldown = 1  # 1 second cooldown between votes
        open(self.votes_file, 'a').close()  # Create file if not exists
        self.cam_detection_buffer = []
        self.cam_threshold = 3 # NEW
        self.is_changed_state = False
        self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag

        self.pie_chart = PieChart()
        self.pie_ready = False
        self.statistic_video_path = os.path.join(self.working_folder, "tmp_pie_chart.mp4")
        
        # Initialize the cv2 player
        self.cv2_player = CV2Player([
            self.A_video_path,
        ], votes_file=self.votes_file) 

    def start(self):
        """
        Start the main control loop that manages state transitions and video playback.
        Initializes camera and keyboard listeners before entering the main loop.
        """
        # self.start_camera() # camera listener non-blocking
        self.start_keyboard_listener() # keyboard listener non-blocking

        action_thread = threading.Thread(target=self.jump_to_state_action)
        action_thread.start()

        
        self.cv2_player.screen_scale = 0.5 # scale down the video to 50% of the original size
        self.cv2_player.play_playlist() #  BLOCKING! - play the playlist(which could be empty) immediately 

        self.cleanup()  


    def start_keyboard_listener(self):
        """
        Initialize and start keyboard input listener.
        Handles:
        - ESC key to stop program
        - 'v' key to toggle voting status
        """

        # TODO: add keyboard Q, W, E input to toggle each opinion, we can store the opinions in a text file for now
        # TODO: add sleep time between each opinion to avoid double voting
        def on_press(key):
            # Existing ESC handler
            if key == keyboard.Key.esc:
                self.running = False
                print("pynput:ESC key pressed")

            # Added vote handling (TODO)
            try:
                # Check if pressed key is one of the voting keys (Q, W, E)
                if key.char.upper() in ['Q', 'W', 'E']:
                    current_time = time.time()
                    # Check if enough time has passed since last vote (prevents double voting)
                    if current_time - self.last_vote_time >= self.vote_cooldown:
                        print("--------------------------------")
                        print("--------------------------------")
                        print(f"Valid new vote of {key.char.upper()}")
                        print("--------------------------------")
                        print("--------------------------------")
                        # Append the vote to the votes file
                        with open(self.votes_file, 'a') as f:
                            f.write(f"{key.char.upper()}\n")
                        # Set voting as active and update last vote timestamp
                        self.vote_active = True # set the vote_active flag to True, it will be reset in the jump_to_state_action()
                        self.last_vote_time = current_time # update the last vote timestamp

                '''DEV: Force transition to a state'''
                if key.char == 'a':
                    print("pynput:a key pressed")
                    self.current_state = 'A'
                    self.cv2_player.add_video(self.A_video_path, play_immediately=True)
                if key.char == 'b':
                    print("pynput:b key pressed")
                    self.current_state = 'B'
                    self.cv2_player.add_video(self.B_video_path, play_immediately=True)
                if key.char == 'c':
                    print("pynput:c key pressed")
                    self.current_state = 'C'
                    self.cv2_player.add_video(self.C_video_path, play_immediately=True)
                if key.char == 'd':
                    print("pynput:d key pressed")
                    self.cv2_player.add_video(self.D_video_path, play_immediately=True)
                
                '''Simulate eyes detection'''
                if key.char == 'p':
                    if not self.cam_active:
                        print("pynput:p key pressed - simulate eyes detection ON")
                        self.cam_active = True  
                    else:
                        print("pynput:p key pressed - simulate eyes detection OFF")
                        self.cam_active = False
            except AttributeError:
                pass

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()


    def jump_to_state_action(self):
        """
        Run a loop, and jump to a specific state when the condition is met
        """
        # time.sleep(3)
        count = 0
        while self.running:
            try:
                print(f"STATE: {self.current_state} | CAM ACTIVE: {self.cam_active} | {self.cv2_player.current_clip_frame_count:.0f}/{self.cv2_player.total_clip_frame_count:.0f} REACH END: {self.cv2_player.is_video_reach_end} | LEN OF PLAYLIST: {len(self.cv2_player.playlist)} | IS CHANGED STATE: {self.is_changed_state}")
            except:
                print("Error: cv2_player is not initialized")

            if self.current_state == 'A':
                '''
                Transitions to State B when camera becomes active.
                '''
                if self.cv2_player.is_video_reach_end: # if the video is near end, show a message
                    if self.cam_active:
                        self.cv2_player.message = f"Video is near end | CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"Video is near end | CAMERA INACTIVE"
                else:
                    if self.cam_active:
                        self.cv2_player.message = f"CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"CAMERA INACTIVE"

                if self.cam_active:
                    '''
                    Transitions from State A to State B immediately when camera becomes active.
                    '''
                    print("CAMERA ACTIVE - Transitioning from State A to State B")
                    self.cv2_player.add_video(self.B_video_path, play_immediately=True)
                    self.current_state = 'B'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag
                
                    
            elif self.current_state == 'B':
                '''
                Transitions:
                - To Statistics if vote detected
                - To State C if camera remains active
                - To State A if camera inactive
                '''  
                self.state_counter += 1
                if self.state_counter == 10:
                    self.is_changed_state = False # this allow the transition to happen only once

                if self.cv2_player.is_video_reach_end: # if the video is near end, show a message
                    if self.cam_active:
                        self.cv2_player.message = f"Video is near end | CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"Video is near end | CAMERA INACTIVE"
                else:
                    if self.cam_active:
                        self.cv2_player.message = f"CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"CAMERA INACTIVE"

                if self.vote_active and self.cam_active:
                    '''
                    If vote is detected,
                    Transitions from State B to State Statistics immediately.
                    '''
                    print("VOTE DETECTED - Transitioning from State B to State Statistics")
                   

                    self.cv2_player.add_video('pie_chart_render', play_immediately=True) # jump to statistics state, note that this is a special case, the video is not a file, but a label to trigger the pie chart render
                    self.current_state = 'STATISTICS'
                    self.vote_active = False # reset the vote_active flag to False
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag

                elif self.cam_active and not self.vote_active and self.cv2_player.is_video_reach_end and not self.is_changed_state:
                    '''
                    If NO vote and camera is ACTIVE,
                    Transitions from State B to State C when the video is near end.
                    '''
                    print("CAMERA ACTIVE - Transitioning from State B to State C")
                    
                    self.cv2_player.add_video(self.C_video_path, play_immediately=False)
                    self.current_state = 'C'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag

                elif not self.cam_active and not self.vote_active and self.cv2_player.is_video_reach_end and not self.is_changed_state:
                    '''
                    If NO vote and camera is INACTIVE,
                    Transitions from State B to State A when the video is near end.
                    '''
                    print("CAMERA INACTIVE - Transitioning from State B to State A")
                    self.cv2_player.add_video(self.A_video_path, play_immediately=False)
                    self.current_state = 'A'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag


            elif self.current_state == 'C':
                """
                State C handler: Plays clip C.
                Transitions:
                - To State A if camera inactive
                - To Statistics if vote detected (TODO: no vote for this state )
                - To State B otherwise
                """
                self.state_counter += 1
                if self.state_counter == 10:
                    self.is_changed_state = False # this allow the transition to happen only once

                if self.cv2_player.is_video_reach_end: # if the video is near end, show a message
                    if self.cam_active:
                        self.cv2_player.message = f"Video is near end | CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"Video is near end | CAMERA INACTIVE"
                else:
                    if self.cam_active:
                        self.cv2_player.message = f"CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"CAMERA INACTIVE"

                if not self.cam_active and self.cv2_player.is_video_reach_end and not self.is_changed_state:
                    '''
                    If camera is INACTIVE,
                    Transitions from State B to State A when the video is near end.
                    '''
                    print("CAMERA INACTIVE - Transitioning from State C to State A")
                    self.cv2_player.add_video(self.A_video_path, play_immediately=False)
                    self.current_state = 'A'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag
                elif self.cam_active and self.cv2_player.is_video_reach_end and not self.is_changed_state:
                    '''
                    If camera is ACTIVE,
                    Transitions from State C to State B when the video is near end.
                    '''
                    print("CAMERA ACTIVE - Transitioning from State C to State B")
                    self.cv2_player.add_video(self.B_video_path, play_immediately=False)
                    self.current_state = 'B'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag


            elif self.current_state == 'STATISTICS':
                """
                State Statistics handler: Plays custom clip Statistics.
                Transitions:
                - To State A if camera inactive
                - To State C if vote detected (TODO: no vote for this state )
                - To State B otherwise
                """
                self.state_counter += 1
                if self.state_counter == 5:
                    self.is_changed_state = False # this allow the transition to happen only once

                if self.cv2_player.is_video_reach_end: # if the video is near end, show a message
                    if self.cam_active:
                        self.cv2_player.message = f"Video is near end | CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"Video is near end | CAMERA INACTIVE"
                else:
                    if self.cam_active:
                        self.cv2_player.message = f"CAMERA ACTIVE"
                    else:
                        self.cv2_player.message = f"CAMERA INACTIVE"

                if not self.cam_active and self.cv2_player.is_video_reach_end and not self.is_changed_state:
                    '''
                    If camera is INACTIVE,
                    Transitions from State S to State A when the video is near end.
                    '''
                    print("CAMERA INACTIVE - Transitioning from State S to State A")
                    self.cv2_player.add_video(self.A_video_path, play_immediately=False)
                    self.current_state = 'A'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag

                elif self.cam_active and self.cv2_player.is_video_reach_end and not self.is_changed_state:
                    '''
                    If camera is ACTIVE,
                    Transitions from State S to State B when the video is near end.
                    '''
                    print("CAMERA ACTIVE - Transitioning from State S to State B")
                    self.cv2_player.add_video(self.B_video_path, play_immediately=False)
                    self.current_state = 'B'
                    self.is_changed_state = True
                    self.state_counter = 0 # set the state counter to 0, its for delay reset of the is_changed_state flag

            
            time.sleep(0.1)


    def update_sensors(self):
        print("Updating sensors")
        """Update the status of camera detection and voting system"""
        # self.cam_active = self.check_camera_condition()
        self.vote_active = self.check_vote_condition()

    def check_camera_condition(self):

        # Get current detection status - True if objects detected in current frame, False if no detection or no result
        current_detection = bool(len(self.eyes.result_list)) if self.eyes.yolo_result else False
        # Add current detection status to buffer for tracking detection history
        self.cam_detection_buffer.append(current_detection)

        # Maintain buffer of last 5 checks
        # Keep buffer size at 5 by removing oldest detection
        if len(self.cam_detection_buffer) > 5:
            self.cam_detection_buffer.pop(0)
        # Return True if objects detected in current frame, False otherwise
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
        self.eyes.running = False
        self.keyboard_listener.stop()
        if os.path.exists(self.statistic_video_path):
            os.remove(self.statistic_video_path)


if __name__ == "__main__":
    # Get the current directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get the Mall directory
    mall_dir = os.path.dirname(current_dir)
    
    #Eyes
    eyes_fps = 3
    eyes_scale = 1
    eyes_buffer_size = 15
    eyes_result_threshold = 13
    eye_parms = (eyes_fps, eyes_scale, eyes_buffer_size, eyes_result_threshold)

    print('WORKING DIRECTORY:', mall_dir)
    controller = VideoController(use_eyes=False, working_folder=mall_dir, votes_file="data/votes.txt", eye_parms=eye_parms)
    controller.start()