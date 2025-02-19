import cv2
import tkinter as tk
from PIL import Image, ImageTk

def play_video(video_path):
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

if __name__ == "__main__":
    # Replace with your video path
    video_path = "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/A_8.mp4"
    play_video(video_path)
