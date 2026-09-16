import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
from PIL import Image, ImageTk



BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

MUSIC_FOLDER = os.path.join(BASE_FOLDER, "music")
ALBUM_FOLDER = os.path.join(BASE_FOLDER, "album")

os.makedirs(MUSIC_FOLDER, exist_ok=True)
os.makedirs(ALBUM_FOLDER, exist_ok=True)



pygame.mixer.init()


playlist = []
album_covers = []

current_song = 0
is_paused = False
song_length = 0
is_seeking = False

current_position = 0


window = tk.Tk()

window.title("My MP3 Player")
window.geometry("900x600")
window.resizable(False, False)
window.configure(bg="#101827")



def load_album_covers():

    global album_covers

    album_covers = []

    files = []

    for file in os.listdir(ALBUM_FOLDER):

        if file.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):

            files.append(file)

    files.sort()

    for file in files:

        path = os.path.join(
            ALBUM_FOLDER,
            file
        )

        try:

            image = Image.open(path)

            image = image.resize(
                (220, 220),
                Image.Resampling.LANCZOS
            )

            photo = ImageTk.PhotoImage(image)

            album_covers.append(photo)

        except Exception as error:

            print(
                f"Could not load album cover {file}: {error}"
            )


def show_album_cover(index):

    if index < len(album_covers):

        album_label.config(
            image=album_covers[index],
            text=""
        )

        album_label.image = album_covers[index]

    else:

        album_label.config(
            image="",
            text="MUSIC"
        )

        album_label.image = None



def load_playlist():

    global playlist

    playlist = []

    for file in os.listdir(MUSIC_FOLDER):

        if file.lower().endswith(
            (".mp3", ".wav", ".ogg")
        ):

            playlist.append(file)

    playlist.sort()

    playlist_box.delete(
        0,
        tk.END
    )

    for song in playlist:

        playlist_box.insert(
            tk.END,
            song
        )

    if not playlist:

        song_title.config(
            text="No songs"
        )

        artist_label.config(
            text="Add a song to begin"
        )

        album_label.config(
            image="",
            text="MUSIC"
        )

        album_label.image = None

    else:

        song_title.config(
            text="Select a song"
        )

        artist_label.config(
            text="Ready to play"
        )



def add_song():

    files = filedialog.askopenfilenames(

        title="Add Songs",

        filetypes=[
            (
                "Audio Files",
                "*.mp3 *.wav *.ogg"
            ),

            (
                "MP3 Files",
                "*.mp3"
            ),

            (
                "WAV Files",
                "*.wav"
            ),

            (
                "OGG Files",
                "*.ogg"
            )
        ]
    )

    for file in files:

        filename = os.path.basename(file)

        destination = os.path.join(
            MUSIC_FOLDER,
            filename
        )

        if not os.path.exists(destination):

            try:

                with open(
                    file,
                    "rb"
                ) as source:

                    with open(
                        destination,
                        "wb"
                    ) as target:

                        target.write(
                            source.read()
                        )

            except Exception as error:

                messagebox.showerror(
                    "Error",
                    f"Could not add {filename}\n\n{error}"
                )

    load_playlist()



def play_song():

    global current_song
    global is_paused
    global song_length
    global current_position

    if not playlist:

        messagebox.showinfo(
            "Playlist Empty",
            "Please add a song first."
        )

        return

    if current_song >= len(playlist):

        current_song = 0

    song_path = os.path.join(
        MUSIC_FOLDER,
        playlist[current_song]
    )

    try:

        pygame.mixer.music.load(
            song_path
        )

        pygame.mixer.music.play()

        sound = pygame.mixer.Sound(
            song_path
        )

        song_length = sound.get_length()

        current_position = 0

        is_paused = False


        song_title.config(
            text=os.path.splitext(
                playlist[current_song]
            )[0]
        )

        artist_label.config(
            text="Now Playing"
        )


        show_album_cover(
            current_song
        )


        playlist_box.selection_clear(
            0,
            tk.END
        )

        playlist_box.selection_set(
            current_song
        )

        playlist_box.activate(
            current_song
        )

        playlist_box.see(
            current_song
        )


        pause_button.config(
            text="Pause"
        )

        progress_slider.config(
            from_=0,
            to=max(song_length, 1)
        )

        progress_slider.set(0)

        current_time.config(
            text="00:00"
        )

        total_time.config(
            text=format_time(song_length)
        )

    except pygame.error as error:

        messagebox.showerror(
            "Playback Error",
            str(error)
        )


def pause_song():

    global is_paused

    if pygame.mixer.music.get_busy():

        pygame.mixer.music.pause()

        is_paused = True

        pause_button.config(
            text="Resume"
        )

        artist_label.config(
            text="Paused"
        )



def resume_song():

    global is_paused

    if is_paused:

        pygame.mixer.music.unpause()

        is_paused = False

        pause_button.config(
            text="Pause"
        )

        artist_label.config(
            text="Now Playing"
        )



def pause_resume():

    if is_paused:

        resume_song()

    else:

        pause_song()



def stop_song():

    pygame.mixer.music.stop()

    pause_button.config(
        text="Pause"
    )

    if playlist:

        artist_label.config(
            text="Stopped"
        )



def next_song():

    global current_song

    if not playlist:

        return

    current_song += 1

    if current_song >= len(playlist):

        current_song = 0

    play_song()



def previous_song():

    global current_song

    if not playlist:

        return

    current_song -= 1

    if current_song < 0:

        current_song = len(playlist) - 1

    play_song()



def remove_song():

    global current_song

    selection = playlist_box.curselection()

    if not selection:

        messagebox.showinfo(
            "Remove Song",
            "Select a song first."
        )

        return

    index = selection[0]

    song = playlist[index]

    result = messagebox.askyesno(
        "Remove Song",
        f"Remove '{song}' from your playlist?"
    )

    if not result:

        return

    if index == current_song:

        pygame.mixer.music.stop()

    file_path = os.path.join(
        MUSIC_FOLDER,
        song
    )

    try:

        os.remove(file_path)

    except OSError:

        pass

    if index < current_song:

        current_song -= 1

    if current_song < 0:

        current_song = 0

    load_playlist()



def select_song(event):

    global current_song

    selection = playlist_box.curselection()

    if selection:

        current_song = selection[0]

        play_song()



def set_volume(value):

    volume = float(value) / 100

    pygame.mixer.music.set_volume(
        volume
    )



def format_time(seconds):

    seconds = int(seconds)

    minutes = seconds // 60

    seconds = seconds % 60

    return f"{minutes:02d}:{seconds:02d}"



def update_progress():

    global is_seeking

    if (
        not is_seeking
        and pygame.mixer.music.get_busy()
    ):

        position = (
            pygame.mixer.music.get_pos()
            / 1000
        )

        if position >= 0:

            progress_slider.set(
                position
            )

            current_time.config(
                text=format_time(position)
            )


    if (
        playlist
        and not is_paused
        and song_length > 0
        and not pygame.mixer.music.get_busy()
    ):

        next_song()

    window.after(
        500,
        update_progress
    )



def start_seek(event):

    global is_seeking

    is_seeking = True


def end_seek(event):

    global is_seeking

    position = progress_slider.get()

    pygame.mixer.music.play(
        start=position
    )

    current_time.config(
        text=format_time(position)
    )

    is_seeking = False


def on_close():

    pygame.mixer.music.stop()

    pygame.mixer.quit()

    window.destroy()



top_frame = tk.Frame(
    window,
    bg="#101827"
)

top_frame.pack(
    fill="x",
    padx=30,
    pady=20
)


logo = tk.Label(
    top_frame,
    text="MY MP3 PLAYER",
    font=("Arial", 20, "bold"),
    bg="#101827",
    fg="white"
)

logo.pack(
    side="left"
)


add_button = tk.Button(
    top_frame,
    text="Add Song",
    font=("Arial", 10, "bold"),
    bg="#2563EB",
    fg="white",
    activebackground="#1D4ED8",
    activeforeground="white",
    relief="flat",
    padx=15,
    pady=8,
    command=add_song
)

add_button.pack(
    side="right"
)


main_frame = tk.Frame(
    window,
    bg="#101827"
)

main_frame.pack(
    fill="both",
    expand=True,
    padx=30
)


player_frame = tk.Frame(
    main_frame,
    bg="#172235",
    width=500,
    height=430
)

player_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 15)
)

player_frame.pack_propagate(False)



album_frame = tk.Frame(
    player_frame,
    bg="#263A5A",
    width=220,
    height=220
)

album_frame.pack(
    pady=25
)

album_frame.pack_propagate(False)



album_label = tk.Label(
    album_frame,
    text="MUSIC",
    font=("Arial", 24, "bold"),
    bg="#263A5A",
    fg="#93C5FD"
)

album_label.pack(
    fill="both",
    expand=True
)

song_title = tk.Label(
    player_frame,
    text="No songs",
    font=("Arial", 20, "bold"),
    bg="#172235",
    fg="white"
)

song_title.pack(
    pady=(0, 5)
)

artist_label = tk.Label(
    player_frame,
    text="Add a song to begin",
    font=("Arial", 11),
    bg="#172235",
    fg="#94A3B8"
)

artist_label.pack()


progress_frame = tk.Frame(
    player_frame,
    bg="#172235"
)

progress_frame.pack(
    fill="x",
    padx=35,
    pady=15
)

current_time = tk.Label(
    progress_frame,
    text="00:00",
    font=("Arial", 9),
    bg="#172235",
    fg="#94A3B8"
)

current_time.pack(
    side="left"
)

progress_slider = tk.Scale(
    progress_frame,
    from_=0,
    to=100,
    orient="horizontal",
    showvalue=False,
    resolution=0.1,
    bg="#172235",
    fg="white",
    troughcolor="#334155",
    highlightthickness=0,
    bd=0,
    command=lambda value: None
)

progress_slider.pack(
    side="left",
    fill="x",
    expand=True,
    padx=10
)


progress_slider.bind(
    "<ButtonPress-1>",
    start_seek
)

progress_slider.bind(
    "<ButtonRelease-1>",
    end_seek
)



total_time = tk.Label(
    progress_frame,
    text="00:00",
    font=("Arial", 9),
    bg="#172235",
    fg="#94A3B8"
)

total_time.pack(
    side="right"
)



controls = tk.Frame(
    player_frame,
    bg="#172235"
)

controls.pack(
    pady=5
)

previous_button = tk.Button(
    controls,
    text="Previous",
    font=("Arial", 10),
    bg="#263A5A",
    fg="white",
    activebackground="#334E73",
    activeforeground="white",
    relief="flat",
    width=9,
    command=previous_song
)

previous_button.grid(
    row=0,
    column=0,
    padx=5
)


play_button = tk.Button(
    controls,
    text="Play",
    font=("Arial", 11, "bold"),
    bg="#2563EB",
    fg="white",
    activebackground="#1D4ED8",
    activeforeground="white",
    relief="flat",
    width=9,
    command=play_song
)

play_button.grid(
    row=0,
    column=1,
    padx=5
)


pause_button = tk.Button(
    controls,
    text="Pause",
    font=("Arial", 10),
    bg="#263A5A",
    fg="white",
    activebackground="#334E73",
    activeforeground="white",
    relief="flat",
    width=9,
    command=pause_resume
)

pause_button.grid(
    row=0,
    column=2,
    padx=5
)

next_button = tk.Button(
    controls,
    text="Next",
    font=("Arial", 10),
    bg="#263A5A",
    fg="white",
    activebackground="#334E73",
    activeforeground="white",
    relief="flat",
    width=9,
    command=next_song
)

next_button.grid(
    row=0,
    column=3,
    padx=5
)


stop_button = tk.Button(
    controls,
    text="Stop",
    font=("Arial", 10),
    bg="#7F1D1D",
    fg="white",
    activebackground="#991B1B",
    activeforeground="white",
    relief="flat",
    width=9,
    command=stop_song
)

stop_button.grid(
    row=1,
    column=1,
    columnspan=2,
    pady=10
)


volume_frame = tk.Frame(
    player_frame,
    bg="#172235"
)

volume_frame.pack(
    fill="x",
    padx=70,
    pady=5
)


volume_label = tk.Label(
    volume_frame,
    text="Volume",
    font=("Arial", 9),
    bg="#172235",
    fg="#94A3B8"
)

volume_label.pack(
    side="left"
)


volume_slider = tk.Scale(
    volume_frame,
    from_=0,
    to=100,
    orient="horizontal",
    showvalue=False,
    bg="#172235",
    fg="white",
    troughcolor="#334155",
    highlightthickness=0,
    bd=0,
    command=set_volume
)

volume_slider.set(70)

volume_slider.pack(
    side="left",
    fill="x",
    expand=True,
    padx=10
)


playlist_frame = tk.Frame(
    main_frame,
    bg="#172235",
    width=300,
    height=430
)

playlist_frame.pack(
    side="right",
    fill="y"
)

playlist_frame.pack_propagate(False)


playlist_title = tk.Label(
    playlist_frame,
    text="PLAYLIST",
    font=("Arial", 14, "bold"),
    bg="#172235",
    fg="white"
)

playlist_title.pack(
    anchor="w",
    padx=20,
    pady=20
)

playlist_box = tk.Listbox(
    playlist_frame,
    font=("Arial", 10),
    bg="#111827",
    fg="#E2E8F0",
    selectbackground="#2563EB",
    selectforeground="white",
    activestyle="none",
    relief="flat",
    bd=0,
    highlightthickness=0
)

playlist_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 15)
)

playlist_box.bind(
    "<<ListboxSelect>>",
    select_song
)


remove_button = tk.Button(
    playlist_frame,
    text="Remove Selected",
    font=("Arial", 10),
    bg="#334155",
    fg="white",
    activebackground="#475569",
    activeforeground="white",
    relief="flat",
    command=remove_song
)

remove_button.pack(
    fill="x",
    padx=15,
    pady=(0, 15)
)



pygame.mixer.music.set_volume(0.7)

load_album_covers()

load_playlist()

window.protocol(
    "WM_DELETE_WINDOW",
    on_close
)

update_progress()



window.mainloop()