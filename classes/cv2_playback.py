import sys
import cv2
import os
import time
import threading
class CV2Player:
    """
    A video player class that uses OpenCV to play videos seamlessly
    """
    def __init__(self, video_paths=[], fps=25):
        """
        Initialize the video player
        
        Args:
            fps (int): Target frames per second for video playback (default: 30)
        """
        self.playlist = [(path, False) for path in video_paths]
        self.current_video = None
        self.current_index = 0
        self.is_playing = False
        self.fps = fps
        self.frame_delay = int(1000/fps)
        self.is_fullscreen = False
        self.window_name = 'Video Player'
        self.message = None
        self.message_timestamp = 0
        self.message_duration = 2  # Duration in seconds to show the message

    def play_playlist(self):
        """Start playing videos from the playlist
        Videos added with play_immediately=True will interrupt current playback
        """
        # if not self.playlist:
        #     print("Playlist is empty")
        #     return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.is_playing = True

        count = 0
        while self.is_playing:
            count += 1
            print(f"running - {count}")
            if not self.playlist:
                # break
                continue
                
            video_path, play_immediately = self.playlist[0]
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"Error opening video: {video_path}")
                self.playlist.pop(0)
                continue

            
            while cap.isOpened() and self.is_playing:
                print(f"playing video")
                s = time.time()
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Add message overlay if within duration
                if self.message and time.time() - self.message_timestamp < self.message_duration:
                    height, width = frame.shape[:2]
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (10, height-60), (width-10, height-10), (0, 0, 0), -1)
                    cv2.putText(overlay, self.message, (30, height-30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
                    
                cv2.imshow(self.window_name, frame)
                
                key = cv2.waitKey(self.frame_delay) & 0xFF
                if key == 27:
                    self.is_playing = False
                    break
                elif key == ord('f'):
                    self.toggle_fullscreen()
                elif key == ord('i'):
                    self.add_video('./footages/D_8.mp4', play_immediately=True)
                    self.show_message("Added video (play immediately)") #for dev
                elif key == ord('o'):
                    self.add_video('./footages/D_8.mp4', play_immediately=False)
                    self.show_message("Added video (play after current)") #for dev
                
                # Check if next video needs immediate playback
                if len(self.playlist) > 1 and self.playlist[1][1]:
                    break

                diff = time.time() - s
                print(f"VIDEO PLAYER | sleep: {max(0, self.frame_delay/1000 - diff):.2f}s (target: {self.frame_delay/1000:.2f}s) | fps: {1/diff:.2f}")
                time.sleep(max(0, self.frame_delay/1000 - diff))

            cap.release()
            
            # Handle playlist management
            if len(self.playlist) > 1:
                self.playlist.pop(0)
            else:
                self.playlist[0] = (video_path, False)
                continue
            

        cv2.destroyAllWindows()

    def add_video(self, video_path, play_immediately=False):
        """
        Add a video to the playlist
        
        Args:
            video_path (str): path to the video to add
            play_immediately (bool): whether to play the video immediately or wait until current video finishes
        """
        self.playlist.append((video_path, play_immediately))

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

    def test_play_playlist(self):
        time.sleep(5) # optional, just for testing
        print("Adding video")
        self.add_video('./footages/D_8.mp4', play_immediately=True)

if __name__ == '__main__':
    
    video_paths = [
        "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/A_8.mp4" # put CLIP A here
    ]

    player = CV2Player(video_paths) # this has to run in main thread and will be blocking

    # this thread will add a video to the playlist in 5 seconds
    thread = threading.Thread(target=player.test_play_playlist)
    thread.start()

    # this thread will play the playlist(which could be empty) immediately
    player.play_playlist()

    
