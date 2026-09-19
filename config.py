import os

# --- Folders -----------------------------------------------------------
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
MUSIC_FOLDER = os.path.join(BASE_FOLDER, "music")
ALBUM_FOLDER = os.path.join(BASE_FOLDER, "album")

# --- Supported file types ---------------------------------------------
AUDIO_EXTENSIONS = (".mp3", ".wav", ".ogg")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# --- Window / behaviour ------------------------------------------------
WINDOW_TITLE = "My MP3 Player"
WINDOW_SIZE = "1100x720"
WINDOW_MIN_SIZE = (900, 600)
PLAYLIST_TITLE = "My Music"
DEFAULT_VOLUME = 70       
PROGRESS_UPDATE_MS = 500     

# --- Album cover sizes ---------------------------------------
COVER_LARGE = 264           
COVER_BAR = 56              
COVER_THUMB = 40           

# Header colour used when the current song has no album cover (R, G, B)
DEFAULT_ACCENT = (80, 56, 160)


class Colors:
    BLACK = "#000000"        
    CARD = "#121212"      
    HOVER = "#2A2A2A"       
    SELECTED = "#333333"     
    DIVIDER = "#2A2A2A"
    PLACEHOLDER = "#282828" 

    TEXT = "#FFFFFF"
    TEXT_MUTED = "#B3B3B3"
    TEXT_SUBTLE = "#727272"

    GREEN = "#1DB954"
    GREEN_HOVER = "#1ED760"

    TRACK = "#4D4D4D"     


def ensure_folders():
    os.makedirs(MUSIC_FOLDER, exist_ok=True)
    os.makedirs(ALBUM_FOLDER, exist_ok=True)