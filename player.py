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
        self.queue = [] # TODO: Implmenet Play Queue
        self.state = self.State.LOADING
    
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['mixer']
        del d['music']
        return d
    
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.init_mixer()
        self.music.set_volume(self.volume)
    
    def init_mixer(self):
        self.mixer = pygame.mixer
        self.mixer.init()
        self.music = self.mixer.music

    def quit(self):
        self.stop()
        self.mixer.quit()

    def play(self, item, channel):
        if self.item is not None:
            self.stop()
        self.item = item
        if item.downloaded:
            self.play_file(item, channel)
        else: # TODO: Stream
            print("Episode Not Downloaded!")
            return
        self.state = self.State.PLAYING
    
    def play_file(self, item, channel):
        self.music.load(f"downloads/{channel.title}/{item.title}.mp3")
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
    
    def restart(self):
        self.music.rewind()
    
    def set_volume(self, amount):
        if amount < 0 or amount > 1:
            raise PlayerInvalidVolumeChange
        self.volume = amount
        self.music.set_volume(self.volume)

    # TODO: Fix
    def skip_forward(self, amount):
        if not self.music.get_busy():
            print("No Episode is playing right now!")
        print(self.music.get_pos())
        self.music.set_pos(float(amount*1000))
        print(self.music.get_pos())
    
    # TODO: Fix
    def skip_backward(self, amount):
        if not self.music.get_busy():
            print("No Episode is playing right now!")
        cur_pos = (self.music.get_pos()/1000)
        print(f"{amount} {cur_pos}")
        self.music.set_pos(cur_pos-amount)
        print(f"{self.music.get_pos()}")
