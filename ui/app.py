import os
import tkinter as tk
from tkinter import filedialog, messagebox
 
import pygame
 
import library
from album import load_album_covers
from config import (
    DEFAULT_ACCENT,
    DEFAULT_VOLUME,
    PROGRESS_UPDATE_MS,
    WINDOW_MIN_SIZE,
    WINDOW_SIZE,
    WINDOW_TITLE,
    Colors,
    ensure_folders,
)
from player import AudioPlayer, PlayerState
from ui.now_playing import NowPlayingPanel
from ui.player_bar import PlayerBar
from ui.playlist_panel import PlaylistPanel
from ui.styles import init_styles
 
 
class MP3PlayerApp:
    def __init__(self):
        ensure_folders()
 
        self.player = AudioPlayer(DEFAULT_VOLUME)
 
        self.songs = []          
        self.covers = []         
        self.current_index = 0
        self.is_seeking = False
 
        self._build_window()
        self._build_layout()
 
        self.covers = load_album_covers()
        self.refresh_playlist()
 
        self.window.bind("<space>", lambda event: self.toggle_play())
        self.window.bind("<Delete>", lambda event: self.remove_song())
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self._update_progress()
 
    def run(self):
        self.window.mainloop()
 
    # --- Building the window -------------------------------------------
    def _build_window(self):
        self.window = tk.Tk()
        self.window.title(WINDOW_TITLE)
        self.window.geometry(WINDOW_SIZE)
        self.window.minsize(*WINDOW_MIN_SIZE)
        self.window.configure(bg=Colors.BLACK)
        init_styles(self.window)
 
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
 
    def _build_layout(self):
        body = tk.Frame(self.window, bg=Colors.BLACK)
        body.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 0))
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
 
        self.now_playing = NowPlayingPanel(body)
        self.now_playing.grid(row=0, column=0, sticky="ns", padx=(0, 8))
 
        self.playlist_panel = PlaylistPanel(
            body,
            on_play_index=self.play_index,
            on_toggle_play=self.toggle_play,
            on_add=self.add_song,
            on_remove=self.remove_song,
        )
        self.playlist_panel.grid(row=0, column=1, sticky="nsew")
 
        self.player_bar = PlayerBar(
            self.window,
            on_toggle_play=self.toggle_play,
            on_stop=self.stop_song,
            on_next=self.next_song,
            on_previous=self.previous_song,
            on_volume_change=self.player.set_volume,
            on_seek_start=self.start_seek,
            on_seek_end=self.end_seek,
        )
        self.player_bar.grid(row=1, column=0, sticky="ew")
 
    # --- Keeping the panels in sync ------------------------------------
    def _cover_for(self, index):
        if index < len(self.covers):
            return self.covers[index]
        return None
 
    def _show_track(self, title, status, cover):
        self.now_playing.show_track(title, status, cover)
        self.player_bar.show_track(title, status, cover)
        self.playlist_panel.set_accent(cover.accent if cover else DEFAULT_ACCENT)
 
    def _set_status(self, status):
        self.now_playing.set_status(status)
        self.player_bar.set_status(status)
 
    def _sync_transport(self):
        state = self.player.state
        playing = state is PlayerState.PLAYING
 
        self.player_bar.set_playing(playing)
        self.playlist_panel.set_playing(playing)
        self.playlist_panel.set_current(
            None if state is PlayerState.STOPPED else self.current_index
        )
 
    # --- Playlist ------------------------------------------------------
    def refresh_playlist(self):
        current_name = self._current_song_name()
 
        self.songs = library.list_songs()
        self.playlist_panel.set_songs(
            [library.song_info(name) for name in self.songs], self.covers
        )
 
        # Keep pointing at the same song even if the list order changed.
        if current_name in self.songs:
            self.current_index = self.songs.index(current_name)
        else:
            self.current_index = min(
                self.current_index, max(len(self.songs) - 1, 0)
            )
 
        if not self.songs:
            self._show_track("No songs", "Add a song to begin", None)
            self._reset_progress()
        elif self.player.state is PlayerState.STOPPED:
            self._show_track("Select a song", "Ready to play", None)
            self._reset_progress()
 
        self._sync_transport()
 
    def _reset_progress(self):
        self.player_bar.set_duration(0)
        self.player_bar.set_position(0)
 
    def _current_song_name(self):
        if self.current_index < len(self.songs):
            return self.songs[self.current_index]
        return None
 
    def add_song(self):
        files = filedialog.askopenfilenames(
            title="Add Songs",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("OGG Files", "*.ogg"),
            ],
        )
 
        for filename, error in library.add_songs(files):
            messagebox.showerror(
                "Error", f"Could not add {filename}\n\n{error}"
            )
 
        self.refresh_playlist()
 
    def remove_song(self, index=None):
        if index is None:
            index = self.playlist_panel.get_selected_index()
 
        if index is None or index >= len(self.songs):
            messagebox.showinfo("Remove Song", "Select a song first.")
            return
 
        song = self.songs[index]
 
        if not messagebox.askyesno(
            "Remove Song", f"Remove '{song}' from your playlist?"
        ):
            return
 
        if index == self.current_index:
            self.player.stop()
 
        if not library.delete_song(song):
            messagebox.showerror("Error", f"Could not remove {song}")
 
        self.refresh_playlist()
 
    def play_index(self, index):
        self.current_index = index
        self.play_song()
 
    # --- Playback ------------------------------------------------------
    def play_song(self):
        if not self.songs:
            messagebox.showinfo("Playlist Empty", "Please add a song first.")
            return
 
        if self.current_index >= len(self.songs):
            self.current_index = 0
 
        filename = self.songs[self.current_index]
 
        try:
            self.player.play(library.song_path(filename))
        except pygame.error as error:
            messagebox.showerror("Playback Error", str(error))
            self._sync_transport()
            return
 
        self._show_track(
            os.path.splitext(filename)[0],
            "Now Playing",
            self._cover_for(self.current_index),
        )
        self.player_bar.set_duration(self.player.length)
        self.player_bar.set_position(0)
 
        self._sync_transport()
        self.playlist_panel.see(self.current_index)
 
    def toggle_play(self):
        
        state = self.player.state
 
        if state is PlayerState.PLAYING:
            self.player.pause()
            self._set_status("Paused")
        elif state is PlayerState.PAUSED:
            self.player.resume()
            self._set_status("Now Playing")
        else:
            self.play_song()
            return
 
        self._sync_transport()
 
    def stop_song(self):
        self.player.stop()
 
        if self.songs:
            self._set_status("Stopped")
 
        self._sync_transport()
 
    def next_song(self):
        if not self.songs:
            return
 
        self.current_index = (self.current_index + 1) % len(self.songs)
        self.play_song()
 
    def previous_song(self):
        if not self.songs:
            return
 
        self.current_index = (self.current_index - 1) % len(self.songs)
        self.play_song()
 
    # --- Seeking -------------------------------------------------------
    def start_seek(self):
        self.is_seeking = True
 
    def end_seek(self, position):
        self.player.seek(position)
        self.player_bar.set_position(position)
        self.is_seeking = False
 
    # --- Background updates --------------------------------------------
    def _update_progress(self):
        if not self.is_seeking and self.player.state is PlayerState.PLAYING:
            self.player_bar.set_position(self.player.position)
 
        if self.player.has_finished():
            self.next_song()
 
        self.window.after(PROGRESS_UPDATE_MS, self._update_progress)
 
    def on_close(self):
        self.player.shutdown()
        self.window.destroy()