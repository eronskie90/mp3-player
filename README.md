# MP3 Player

A desktop MP3 player with spotify like ui built with Python, Tkinter, Pygame, and Pillow.

## Features

- Play and pause music
- Resume playback
- Stop music
- Next track
- Add songs to the playlist
- Volume control
- Progress tracking
- Album cover display
- Playlist management
- Automatic music and album folder handling

## Technologies Used

- Python
- Tkinter
- Pygame
- Pillow

## Project Structure

````text
└── mp3-player/
    ├── album.py
    ├── config.py
    ├── imaging.py
    ├── library.py
    ├── main.py
    ├── player.py
    ├── README.md
    ├── requirements.txt
    ├── utils.py
    │
    ├── ui/
    │   ├── app.py
    │   ├── icons.py
    │   ├── now_playing.py
    │   ├── player_bar.py
    │   ├── playlist_panel.py
    │   ├── styles.py
    │   ├── track_list.py
    │   ├── widgets.py
    │   └── __init__.py
    │
    ├── music/
    │   └── .gitkeep
    └── album/
        └── .gitkeep


## Installation

1. Clone this repository.

2. Install the required packages:

```bash
pip install -r requirements.txt
````

3. Add your own music files to the `music` folder.

4. Add your own album cover images to the `album` folder.

5. Run the application:

```bash
python main.py
```

## Notes

The repository does not include sample MP3, MP4, or album artwork files. Users can add their own media files to the `music` and `album` folders.

## Purpose

This project was created as a Python desktop application project to practice GUI development, audio playback, playlist management, file handling, and the use of third-party Python libraries.
