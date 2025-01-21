# Preface-Mall-Button

Example code of controling video playback with python

How to run the example

create a virtual env

```
python3 -m venv mallEnv
```

Activate the env

```
source ./mallEnv/bin/activate
```

install dependency

```
pip install -r requirements.txt
```

Run the playback.py

```
 python ./classes/playback.py -f play_this_folder
```

The playback.py is a class that will playback all the video in the appointed folder, and when press 'q', it will change the playback list and start playing another video once the current one is finished
