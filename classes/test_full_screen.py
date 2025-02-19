import cv2
import tkinter as tk
from PIL import Image, ImageTk
import pygame
import numpy
import vlc

def play_video_fullscreen(path):
    """
    Function note: Play video using VLC with hardware decoding
    Args:
        path (str): Path to video file
    """
    instance = vlc.Instance('--no-xlib --aout=alsa')
    player = instance.media_player_new()
    media = instance.media_new(path)
    player.set_media(media)
    player.set_fullscreen(True)
    player.play()
    
    while player.is_playing():
        continue

def play_video_tk(video_path):
    """
    Play a video in fullscreen loop using OpenCV and Tkinter
    
    Args:
        video_path (str): Path to the video file to play
    """
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    
    # Create Tkinter window
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    
    # Create canvas for video display
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Bind Escape key to exit
    root.bind('<Escape>', lambda e: root.quit())
    
    def update_frame():
        """Update video frame on canvas"""
        ret, frame = cap.read()
        
        if ret:
            # Convert frame to format for Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Display frame
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.image = imgtk
            
            # Schedule next frame update
            root.after(30, update_frame)
        else:
            # Reset video to beginning when it ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            root.after(30, update_frame)
    
    # Start video playback
    update_frame()
    root.mainloop()
    
    # Clean up
    cap.release()


def play_video_pygame(video_path):
    """
    Play a video in fullscreen loop using OpenCV and Pygame
    
    Args:
        video_path (str): Path to the video file to play
    """
    # Initialize pygame
    pygame.init()
    
    # Get display info
    display_info = pygame.display.Info()
    screen_width = display_info.current_w
    screen_height = display_info.current_h
    
    # Create fullscreen display
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    
    # Get video dimensions
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Read video frame
        ret, frame = cap.read()
        
        if ret:
            # Convert frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Scale frame to fit screen while maintaining aspect ratio
            scale = min(screen_width/video_width, screen_height/video_height)
            new_width = int(video_width * scale)
            new_height = int(video_height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to pygame surface
            frame = numpy.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            
            # Center frame on screen
            x_offset = (screen_width - new_width) // 2
            y_offset = (screen_height - new_height) // 2
            
            # Clear screen and draw frame
            screen.fill((0,0,0))
            screen.blit(frame, (x_offset, y_offset))
            pygame.display.flip()
            
        else:
            # Reset video to beginning when it ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
    # Clean up
    cap.release()
    pygame.quit()


if __name__ == "__main__":
    # Replace with your video path
    video_path = "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/A_8.mp4"
    # play_video_tk(video_path)
    play_video_pygame(video_path)
    # play_video_fullscreen(video_path)
    # play_video_fullscreen_vlc(video_path)

