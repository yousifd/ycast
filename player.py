from enum import Enum
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from exceptions import YCastException

class PlayerException(YCastException):
    pass

class PlayerInvalidVolumeChange(PlayerException):
    pass

class Player:
    
    class State(Enum):
        LOADING = "loading"
        PLAYING = "playing"
        PAUSED = "paused"
        STOPPED = "stopped"

    def __init__(self):
        self.init_mixer()
        self.volume = self.music.get_volume()

        self.item = None
        self.file = None
        self.state = self.State.LOADING
        self.q = list()
    
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['mixer']
        del d['music']
        del d['file']
        return d
    
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.file = None
        self.init_mixer()
        self.music.set_volume(self.volume)
    
    def init_mixer(self):
        self.mixer = pygame.mixer
        self.mixer.init()
        self.music = self.mixer.music

    def quit(self):
        self.stop()
        self.mixer.quit()

    def play(self, items, channel):
        if self.item is not None:
            self.stop()
        self.item = items
        if self.item.downloaded:
            self.play_file(self.item, channel)
        self.state = self.State.PLAYING
    
    def play_file(self, item, channel):
        self.file = open(item.filename, "rb")
        self.music.load(self.file)
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
        if self.file is not None:
            self.file.close()
        self.music.stop()
        self.state = self.State.STOPPED
    
    def restart(self):
        self.music.rewind()
    
    def set_volume(self, amount):
        if amount < 0 or amount > 1:
            raise PlayerInvalidVolumeChange
        self.volume = amount
        self.music.set_volume(self.volume)
