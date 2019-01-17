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
        self.music = self.mixer.music

        self.item = None
        self.state = self.State.LOADING
    
    def quit(self):
        self.stop()
        self.mixer.quit()

    def play(self, item, channel):
        self.item = item
        if item.downloaded:
            self.play_file(item, channel)
        else: # Stream
            # TODO: Implement Streaming
            print("Not Downloaded!")
            return
        self.state = self.State.PLAYING
    
    def play_file(self, item, channel):
        self.music.load(f"downloads/{channel.title}/{item.title}.mp3")
        # self.music.set_pos(item.progress/1000)
        self.music.play(start=item.progress/1000)
    
    def pause(self):
        self.item.progress += self.music.get_pos()
        self.music.pause()
        self.state = self.State.PAUSED
    
    def unpause(self):
        self.music.unpause()
        self.state = self.State.PLAYING
    
    def stop(self):
        if self.item is not None:
            self.item.progress += self.music.get_pos()
        self.music.stop()
        self.state = self.State.STOPPED
