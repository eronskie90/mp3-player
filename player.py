from enum import Enum

import pygame


class PlayerState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioPlayer:
    def __init__(self, volume_percent=70):
        pygame.mixer.init()

        self.state = PlayerState.STOPPED
        self.length = 0.0          # length of the current song in seconds
        self._start_offset = 0.0   # where playback started (after a seek)

        self.set_volume(volume_percent)

    # Playback controls 
    def play(self, path, start=0.0):
        try:
            pygame.mixer.music.load(path)
            self.length = pygame.mixer.Sound(path).get_length()

            if start > 0:
                pygame.mixer.music.play(start=start)
            else:
                pygame.mixer.music.play()
        except pygame.error:
            self.stop()
            raise

        self._start_offset = start
        self.state = PlayerState.PLAYING

    def pause(self):
        if self.state is PlayerState.PLAYING:
            pygame.mixer.music.pause()
            self.state = PlayerState.PAUSED

    def resume(self):
        if self.state is PlayerState.PAUSED:
            pygame.mixer.music.unpause()
            self.state = PlayerState.PLAYING

    def stop(self):
        pygame.mixer.music.stop()

        # Release the file so it can be deleted (matters on Windows).
        if hasattr(pygame.mixer.music, "unload"):
            pygame.mixer.music.unload()

        self.state = PlayerState.STOPPED
        self._start_offset = 0.0

    def seek(self, seconds):
    
        if self.state is PlayerState.STOPPED:
            return

        was_paused = self.state is PlayerState.PAUSED

        pygame.mixer.music.play(start=seconds)
        self._start_offset = seconds

        if was_paused:
            pygame.mixer.music.pause()

    def set_volume(self, percent):
        pygame.mixer.music.set_volume(float(percent) / 100)

    # Status 
    @property
    def position(self):
        if self.state is PlayerState.STOPPED:
            return 0.0

        elapsed_ms = pygame.mixer.music.get_pos()

        if elapsed_ms < 0:
            return self._start_offset

        return min(self._start_offset + elapsed_ms / 1000, self.length)

    def has_finished(self):
        return (
            self.state is PlayerState.PLAYING
            and not pygame.mixer.music.get_busy()
        )

    def shutdown(self):
        self.stop()
        pygame.mixer.quit()