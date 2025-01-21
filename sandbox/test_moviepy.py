from  moviepy.editor import *
from moviepy.editor import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import crossfadein, crossfadeout
import cv2
from pynput import keyboard


is_pause = False
def on_press(key):
    global is_pause
    print(f"Key pressed: {key}")
    if key == keyboard.Key.space:
        print("space")
        is_pause = not is_pause
        print(f"is_pause: {is_pause}")

def on_release(key):
    print(f"Key released: {key}")


if __name__=='__main__':
    # List of video files to play
    # video_files = ['A.mp4', 'B.mp4', 'C.mp4', 'D.mp4']
    # video_files = ['3206300-hd_1920_1080_25fps.mp4', '3580080-hd_1920_1080_24fps.mp4', '4682200-hd_1920_1080_25fps.mp4']
    video_files = ['3206300-hd_1920_1080_25fps.mp4', '3580080-hd_1920_1080_24fps.mp4']
    base_path = "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages"

    # Create a list to store all clips
    clips = []
    for video in video_files:
        video_path = f"{base_path}/{video}"
        clip = VideoFileClip(video_path).subclip(0, 3)
        # Add 1 second fade in and fade out
        # clip = clip.fadein(0.5)#.fadeout(0.5)
        clips.append(clip.crossfadein(1))


    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    count = 0
    max_pause_time = 10
    while count < 6:

        # Concatenate all clips with crossfade transitions
        print("clips", clips)
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Play the final clip
        final_clip.preview(fps=25)
        if is_pause:
            # Pause the video playback when is_pause is True
            while is_pause and max_pause_time > 0:
                cv2.waitKey(1)  # Keep window responsive while paused
                max_pause_time -= 1
            if max_pause_time == 0:
                is_pause = False
                max_pause_time = 10
        
        if count == 2:
            video = '4682200-hd_1920_1080_25fps.mp4'
            video_path = f"{base_path}/{video}"
            new_clip = VideoFileClip(video_path).subclip(0, 3)
            clips.append(new_clip.crossfadein(1))
            print(f"append {video}")
        if count == 3:
            video = '6092618-hd_1920_1080_30fps.mp4'
            video_path = f"{base_path}/{video}"
            new_clip = VideoFileClip(video_path).subclip(0, 3)
            clips.append(new_clip.crossfadein(1))
            print(f"append {video}")
        count += 1

    final_clip.close()
    for clip in clips:
        clip.close()

    print("done")


