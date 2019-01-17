from enum import Enum
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from exceptions import YCastException

class PlayerException(YCastException):
    pass

class Player:
    
    class State(Enum):
        LOADING = "loading"
        PLAYING = "playing"
        PAUSED = "paused"
        STOPPED = "stopped"

    def __init__(self):
        self.mixer = pygame.mixer
        self.mixer.init()

        self.item = None
        self.playlist = []
        self.state = self.State.LOADING
    
    def quit(self):
        self.stop()
        self.mixer.quit()

    def play(self, item, channel):
        # TODO: Store current position and start from there next time you play
        self.item = item
        if item.downloaded:
            self.play_file(item, channel)
        else: # Stream
            print("Not Downloaded!")
            return
        self.state = self.State.PLAYING
    
    def play_file(self, item, channel):
        print(f"PLAYING {item.title}")
        self.mixer.music.load(f"downloads/{channel.title}/{item.title}.mp3")
        self.mixer.music.play()
    
    def pause(self):
        # TODO: Track Progress
        self.mixer.music.pause()
        self.state = self.State.PAUSED
    
    def unpause(self):
        self.mixer.music.unpause()
        self.state = self.State.PLAYING
    
    def stop(self):
        # TODO: Track Progress
        self.mixer.music.stop()
        self.state = self.State.STOPPED

    def add_playlist(self, item):
            # TODO: Verify Source
        self.playlist.append(item)

    def remove_playlist(self, item):
        # TODO: Verify Source
        self.playlist.remove(item)
