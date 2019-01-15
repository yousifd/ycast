from enum import Enum

class Player:
    
    class State(Enum):
        LOADING = "loading"
        PLAYING = "playing"
        PAUSED = "paused"

    def __init__(self):
        self.playlist = []
        self.state = self.State.LOADING
    
    def play(self, source):
        # TODO: Check if source is url or local file
        # TODO: if source == None then play playlist
        self.state = self.State.PLAYING
    
    def play_playlist(self):
        pass
    
    def add_playlist(self, source):
        # TODO: Verify Source
        self.playlist.append(source)
    
    def remove_playlist(self, source):
        # TODO: Verify Source
        self.playlist.remove(source)
    
    def pause(self):
        self.state = self.State.PAUSED
