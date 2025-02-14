from classes.cv2_playback import CV2Player
from classes.yolo import Eyes


if __name__ == "__main__":
    yolo = Eyes()

    video_paths = [
        # "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/A.mp4",
        # "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/B.mp4",
        "/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/C_8.mp4"
    ]

    player = CV2Player(video_paths) 
    player.play_playlist()



