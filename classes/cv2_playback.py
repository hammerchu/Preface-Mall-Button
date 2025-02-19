import sys
import cv2
import os
import time
import threading

from pie_chart import PieChart

class CV2Player:
    """
    A video player class that uses OpenCV to play videos seamlessly
    """
    def __init__(self, video_paths=[], votes_file="", fps=25, verbose=False):
        """
        Initialize the video player
        
        Args:
            fps (int): Target frames per second for video playback (default: 30)
        """
        self.playlist = [(path, False) for path in video_paths] # (path, play_immediately, hold_time)
        self.current_video = None
        self.current_index = 0
        self.is_playing = False
        self.fps = fps
        self.frame_delay = int(1000/fps)
        self.screen_scale = 1
        self.is_fullscreen = False
        self.window_name = 'Video Player'
        self.res_width = 1920
        self.res_height = 1080
        self.message = None
        self.message_timestamp = 0
        self.message_duration = 2  # Duration in seconds to show the message
        
        self.is_video_reach_end = False
        self.is_video_reach_end_threshold = 0.3 # if the video is near end, set the flag to True - make sure this is larger than the sleep time of jump_to_state_action() in controller
        self.verbose = verbose

        self.current_clip_frame_count = None
        self.total_clip_frame_count = None

        self.pie_chart = PieChart()
        self.votes_file = votes_file
        if not self.votes_file:
            raise ValueError("Error: votes_file is required")
        self.pie_is_baking = False


    def play_playlist(self):
        """Start playing videos from the playlist
        Videos added with play_immediately=True will interrupt current playback
        """
        # if not self.playlist:
        #     print("Playlist is empty")
        #     return

        # cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # self.toggle_fullscreen()
        self.is_playing = True

        count = 0
        pie_chart_duration = 50
        pie_chart_hold_time = 3
        while self.is_playing:
            count += 1
            print(f"running - {count}")
            if self.playlist:
                video_path, _ = self.playlist[-1] # play the last video in the playlist

                if video_path == "pie_chart_render":
                    '''Special case for pie chart render'''
                    print(f"***** playing {video_path} *****")
                    # data = [('Apples', 50), ('Bananas', 30), ('Cherries', 20)]
                    # colors = ['darkred', 'yellow', 'pink']

                    data, colors = self.generate_statistic_video_params()
                    
                    # frame_count = 0
                    self.current_clip_frame_count = 0
                    self.total_clip_frame_count = pie_chart_duration + pie_chart_hold_time*self.fps
                    while self.current_clip_frame_count < self.total_clip_frame_count:
                        if self.current_clip_frame_count < pie_chart_duration:
                            frame = self.pie_chart.render_single_frame(data, colors, duration=pie_chart_duration, title="polling result", frame_index=self.current_clip_frame_count, player=False)
                        else:
                            print(f"holding the pie chart for {self.current_clip_frame_count - pie_chart_duration}/{pie_chart_hold_time*self.fps} seconds")
                            frame = self.pie_chart.render_single_frame(data, colors, duration=pie_chart_duration, title="polling result", frame_index=pie_chart_duration, player=False)
                        # Scale the frame
                        # frame = cv2.resize(frame, None, fx=self.screen_scale, fy=self.screen_scale)
                        cv2.imshow(self.window_name, frame)
                        key = cv2.waitKey(self.frame_delay) & 0xFF
                        if key == 27:
                            self.is_playing = False
                            break
                        elif key == ord('f'):
                            self.toggle_fullscreen()
                        # frame_count += 1

                        # Unified end detection using total duration
                        frames_remaining = self.total_clip_frame_count - self.current_clip_frame_count
                        time_remaining = frames_remaining / self.fps
                        self.is_video_reach_end = time_remaining <= self.is_video_reach_end_threshold
                        print(f"-----> time_remaining: {time_remaining} | threshold: {self.is_video_reach_end_threshold} | is_video_reach_end: {self.is_video_reach_end}")

                        self.current_clip_frame_count += 1

                        # Check if next video needs immediate playback - TODO: we might not need this based on our design
                        if len(self.playlist) > 1 and self.playlist[1][1]:
                            break

                    print("Pie chart render finished")

                else:
                    '''Normal case for video playback'''
                    print(f"***** playing {video_path} *****")
                    cap = cv2.VideoCapture(video_path) # open the video
                    
                    if not cap.isOpened():
                        print(f"Error opening video: {video_path}")
                        self.playlist.pop(0)
                        continue

                    self.current_clip_frame_count = 0
                    self.total_clip_frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    while cap.isOpened() and self.is_playing:
                        self.current_clip_frame_count += 1
                        if count % 30 == 0:
                            print(f"playing video")
                        s = time.time()


                        ret, frame = cap.read()
                        
                        if not ret:
                            break
                        
                        # Unified end detection using total duration
                        frames_remaining = self.total_clip_frame_count - self.current_clip_frame_count
                        time_remaining = frames_remaining / self.fps
                        self.is_video_reach_end = time_remaining <= self.is_video_reach_end_threshold
                        
                        # Add message overlay if within duration
                        # if self.message and time.time() - self.message_timestamp < self.message_duration:
                        if self.message:
                            height, width = frame.shape[:2]
                            overlay = frame.copy()
                            cv2.rectangle(overlay, (10, height-60), (width-10, height-10), (0, 0, 0), -1)
                            cv2.putText(overlay, self.message, (30, height-30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                            frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
                            
                        # Scale the frame
                        # frame = cv2.resize(frame, None, fx=self.screen_scale, fy=self.screen_scale)
                        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        cv2.imshow(self.window_name, frame)
                        
                        key = cv2.waitKey(self.frame_delay) & 0xFF
                        if key == 27:
                            self.is_playing = False
                            break
                        elif key == ord('f'):
                            self.toggle_fullscreen()

                        # Check if next video needs immediate playback
                        if len(self.playlist) > 1 and self.playlist[1][1]:
                            break

                        # sleep to match the frame rate
                        diff = time.time() - s
                        if self.verbose:
                            print(f"VIDEO PLAYER | sleep: {max(0, self.frame_delay/1000 - diff):.2f}s (target: {self.frame_delay/1000:.2f}s) | fps: {1/diff:.2f}")
                        # time.sleep(max(0, self.frame_delay/1000 - diff))

                cap.release()
                
                # Handle playlist management
                # Handle playlist management after video finishes playing
                if len(self.playlist) > 1:
                    # If there are more videos in playlist, remove the current one
                    # and continue to next video
                    self.playlist.pop(0)
                    print(f"{len(self.playlist)} | videos left in playlist")
                else:
                    # If this is the only video in playlist, keep it but set
                    # play_immediately flag to False so it loops continuously
                    self.playlist[0] = (video_path, False)
                    print(f"{len(self.playlist)} | videos left in playlist | repeat the last video")
                    continue
            
            else:
                # if the playlist is empty, wait for 1 second before checking again
                print("Playlist is empty, waiting for 1 second")
                time.sleep(1)

        cv2.destroyAllWindows()

    def add_video(self, video_path, play_immediately=False):
        """
        Add a video to the playlist
        
        Args:
            video_path (str): path to the video to add
            play_immediately (bool): whether to play the video immediately or wait until current video finishes
            hold_time (int): number of seconds to hold the last frame
        """
        self.playlist.append((video_path, play_immediately))
        # self.playlist = [(video_path, play_immediately)]

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    def show_message(self, text):
        """
        Display a message on the video player
        
        Args:
            text (str): Message to display
        """
        self.message = text
        self.message_timestamp = time.time()


    def generate_statistic_video_params(self):
        """
        prepare the data for the pie chart
        return the data, colors
        """
        print("Start generating statistic video...")
        s = time.time()
        with open(self.votes_file, 'r') as f:
            votes = [line.strip() for line in f.readlines()]

        counts = {'Q': 0, 'W': 0, 'E': 0}
        for vote in votes:
            if vote in counts:
                counts[vote] += 1

        total = sum(counts.values())
        data = []
        if total > 0:
            data = [
                ('Too hot', counts['Q']),
                ('Just right', counts['W']),
                ('Too cold', counts['E'])
            ]
        # Generate pie chart
        colors = ['#FF0000', '#808080', '#0000FF']
        return data, colors

if __name__ == '__main__':
    
    video_paths = [
        "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/A_8.mp4" # put CLIP A here
    ]

    player = CV2Player() # this has to run in main thread and will be blocking

    # this thread will add a video to the playlist in 5 seconds
    thread = threading.Thread(target=player.test_play_playlist)
    thread.start()

    # this thread will play the playlist(which could be empty) immediately
    player.play_playlist()

    
