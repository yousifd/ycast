from enum import Enum
import threading

# import sounddevice as sd
# import soundfile as sf

class Player:
    
    class State(Enum):
        LOADING = "loading"
        PLAYING = "playing"
        PAUSED = "paused"

    def __init__(self):
        self.playlist = []
        self.state = self.State.LOADING
        # https://python-sounddevice.readthedocs.io/en/0.3.12/examples.html
    
    def play(self, source):
        # TODO: Check if source is url or local file
        # TODO: if source == None then play playlist
        # TODO: Implement play
        self.state = self.State.PLAYING
    
    def add_playlist(self, source):
        # TODO: Verify Source
        self.playlist.append(source)
    
    def remove_playlist(self, source):
        # TODO: Verify Source
        self.playlist.remove(source)
    
    def pause(self):
        # TODO: Implement Pause
        self.state = self.State.PAUSED
