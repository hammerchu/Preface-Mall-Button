# import vlc

# instance = vlc.Instance('--no-audio', '--fullscreen')
# player = instance.media_player_new()
# player.audio_get_volume()
# media = instance.media_new('/Users/hammerchu/Desktop/DEV/Preface/Mall/footages/3206300-hd_1920_1080_25fps.mp4')
# print(media.get_mrl())
# player.set_media(media)
# player.play()

import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
import vlc
import sys
import os

mov_files_list = os.listdir("/Users/hammerchu/Desktop/DEV/Preface/Mall/footages")

Instance = vlc.Instance('--fullscreen')
player = Instance.media_player_new()

vlcApp = QtWidgets.QApplication([])
vlcWidget = QtWidgets.QFrame()

for mov_file in mov_files_list:
    video_path = os.path.join("/Users/hammerchu/Desktop/DEV/Preface/Mall/footages", mov_file)
    Media = Instance.media_new(video_path)
    player.set_media(Media)
    player.set_nsobject(vlcWidget.winId())  # Set window handle before playing
    vlcWidget.setWindowState(QtCore.Qt.WindowFullScreen)
    vlcWidget.show()
    player.play()
    
    # Wait for video to finish before playing next one
    while player.get_state() != vlc.State.Ended:
        vlcApp.processEvents()
        # QtCore.QThread.msleep(100)  # Add small delay to prevent high CPU usage
        
    player.stop()  # Ensure video is fully stopped before next one

# player.set_media(Media)
# vlcWidget.setWindowState(QtCore.Qt.WindowFullScreen)

# # vlcWidget.resize(700,700)
# vlcWidget.show()

# player.set_nsobject(vlcWidget.winId()) 
    
# player.play()

# vlcApp.exec_()