from moviepy.editor import *
from moviepy.editor import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.transitions import crossfadein, crossfadeout
from pynput import keyboard
import argparse
import os
import subprocess

class Playback:
    '''Control video playback'''

    def __init__(self, folder_path="./", fps=25, loop=True, is_full_screen=False):
        # self.is_pause = False # not used
        # self.max_pause_time = 10 # not used
        self.folder_path = folder_path
        self.fps = fps
        self.loop = loop
        self.clips = []
        self.listener = None
        self.next = None
        self.is_full_screen = is_full_screen

    def on_press(self, key):
        # if key == keyboard.Key.space:   
            # self.is_pause = not self.is_pause # not used
            # print(f"is_pause: {self.is_pause}") # not used
        if key == keyboard.Key.backspace:
            self.loop = False
            self.stop()
        if key == keyboard.KeyCode.from_char('q'):
            self.next = True # raise the flag to play the next video

    def on_release(self, key):
        print(f"Key released: {key}")

    def start(self):
        '''Start playback all videos in the given folder'''
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        video_files = [f for f in os.listdir(self.folder_path) if f.endswith('.mp4')] # extract all the mp4 files and puot them inot a list
        print("video_files", video_files)
        # Create a list to store all clips in the appoint folder
        for video in video_files:
            video_path = f"{self.folder_path}/{video}"
            clip = VideoFileClip(video_path)#.subclip(0, 3)
            # Add fade in and fade out
            # clip = clip.fadein(0.5).fadeout(0.5)
            # self.clips.append(clip.crossfadein(1))
            self.clips.append(video_path)


        count = 0
        while self.loop:

            # # Concatenate all clips with crossfade transitions
            # final_clip = concatenate_videoclips(self.clips, method="compose")
            # # Play the final clip
            # final_clip.preview(fps=self.fps) # play the video
            for video_path in self.clips:
                # Build ffmpeg command with fade transitions
                print(f"Playing video: {video_path}")
                if os.path.exists(video_path):
                    # Get duration of video
                    # Get duration using ffmpeg
                    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
                    duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
                    
                    # Add fade in/out filters
                    fade_cmd = f'ffmpeg -i "{video_path}" -vf "fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5}:d=0.5" -y temp_fade.mp4'
                    subprocess.run(fade_cmd, shell=True)
                    
                    # Play the video with fades
                    play_cmd = f'ffplay temp_fade.mp4' 
                    subprocess.run(play_cmd, shell=True)
                    
                    # # Clean up temp file
                    # if os.path.exists("temp_fade.mp4"):
                    #     os.remove("temp_fade.mp4")
            

            if self.next:
                '''when user press q, set the clips to the next video (C.mp4 in this case)'''
                video_path = f"/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/A.mp4"
                # clip = VideoFileClip(video_path)#.subclip(0, 3)
                # self.clips = [clip.fadein(0.5).fadeout(0.5)]
                self.clips = [video_path]
                # Play video with fade transitions
                if os.path.exists(video_path):
                    # Get duration of video
                    clip = VideoFileClip(video_path)
                    duration = clip.duration
                    clip.close()
                    
                    # Add fade in/out filters
                    fade_cmd = f'ffmpeg -i "{video_path}" -vf "fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5}:d=0.5" -y temp_fade.mp4'
                    subprocess.run(fade_cmd, shell=True)
                    
                    # Play the video with fades
                    play_cmd = f'ffplay -autoexit temp_fade.mp4'
                    subprocess.run(play_cmd, shell=True)
                    
                    # # Clean up temp file
                    # if os.path.exists("temp_fade.mp4"):
                    #     os.remove("temp_fade.mp4")
                self.next = False # reset the flag
            
            count += 1

        # final_clip.close()
        # for clip in self.clips:
        #     clip.close()

        print("done")
        if os.path.exists("temp_fade.mp4"):
            os.remove("temp_fade.mp4")


    def stop(self):
        '''Stop playback'''
        self.listener.stop()

if __name__ == "__main__":

    folder_path = "/Users/hammerchu/Desktop/DEV/Preface/Mall/play_this_folder"
    playback = Playback(folder_path)
    playback.start()


