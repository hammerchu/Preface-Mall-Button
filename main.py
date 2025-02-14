from classes.cv2_playback import CV2Player
from classes.yolo import Eyes


if __name__ == "__main__":
    yolo = Eyes()

    video_paths = [
        # "./footages/A.mp4",
        # "./footages/B.mp4",
        "./footages/C_8.mp4"
    ]

    player = CV2Player(video_paths) 
    player.play_playlist()



