#! /usr/bin/python3

import logging
import signal
import sys
import threading
import os
import pickle

from manager import Manager
from player import Player, PlayerInvalidVolumeChange

class YCast:
    def __init__(self):
        self.quit = False
        self.manager = Manager()
        self.player = Player()
        self.threads = []

        signal.signal(signal.SIGINT, self.handle_exit_sig)

        if not os.path.exists("config"):
            os.makedirs("config")
        else:
            with open("config/manager.pkl", "rb") as input:
                self.manager = pickle.load(input)
            with open("config/player.pkl", "rb") as input:
                self.player = pickle.load(input)
    
    def handle_exit_sig(self, sig, frame):
        self.handle_exit()
        sys.exit(0)

    def handle_exit(self):
        self.player.quit()
        for thread in self.threads:
            if thread.is_alive():
                print(f"Waiting for: {thread.name}")
            thread.join()
        with open("config/manager.pkl", "wb") as output:
            pickle.dump(self.manager, output, pickle.HIGHEST_PROTOCOL)
        with open("config/player.pkl", "wb") as output:
            pickle.dump(self.player, output, pickle.HIGHEST_PROTOCOL)
        self.quit = True
        print("Goodbye!")
    
    def start(self):
        # RT https://roosterteeth.com/show/rt-podcast/feed/mp3
        # GRC http://leoville.tv/podcasts/sn.xml
        # CC https://corridorcast.libsyn.com/rss
        while not self.quit:
            line = input("ycast> ")
            logging.debug(line)
            line = line.split(" ", 1)
            cmd = line[0]
            args = None
            if len(line) > 1:
                args = line[1]

            if cmd == "help" or cmd == "?":
                # TODO: Print Usage
                pass

            elif cmd == "":
                continue
            

            # TODO: Channel Info
            # TODO: Item Info
            elif cmd == "info" or cmd == "i":
                channel = self.select_channel("Info")
                print(channel.info_str())
            
            elif cmd == "subscribe" or cmd == "sub" or cmd == "add":
                if args is None:
                    print("Please specify a Podcast to subscribe to!")
                    continue
                for url in args.split(" "):
                    t = threading.Thread(target=self.manager.subscribe_to_channel, args=(url,), name=f"Subscribing to {url}")
                    t.start()
                    self.threads.append(t)
            
            elif cmd == "unsubscribe" or cmd == "unsub" or cmd == "remove":
                channel = self.select_channel("Unsubscribe")
                self.manager.unsubscribe_from_channel(channel.title)
            
            elif cmd == "list" or cmd == "ls":
                self.show_all()
            
            elif cmd == "download" or cmd == "d":
                channel = self.select_channel("Download")
                for item_index in self.select_item_indexes(channel, "Download"):
                    item = channel.items[item_index]
                    logging.info(f"Downloading {item.title}")
                    t = threading.Thread(target=self.manager.download_item, args=(item_index, channel), name=f"Downloading {channel.title}: {item.title}")
                    t.start()
                    self.threads.append(t)
            
            elif cmd == "delete" or cmd == "del":
                channel = self.select_channel("Delete")
                for item_index in self.select_item_indexes(channel, "Delete"):
                    item = channel.items[item_index]
                    t = threading.Thread(target=self.manager.delete_item, args=(item, channel))
                    t.start()
                    self.threads.append(t)
            
            elif cmd == "sync":
                self.manager.update_all()

            elif cmd == "update" or cmd == "u":
                channel = self.select_channel("Update")
                self.manager.update(channel)

            elif cmd == "play" or cmd == "p":
                channel = self.select_channel("Play")
                item = channel.items[self.select_item(channel, "Play")]
                self.player.play(item, channel)

            elif cmd == "pause":
                self.player.pause()
            
            elif cmd == "unpause" or cmd == "continue":
                self.player.unpause()
            
            elif cmd == "stop":
                self.player.stop()
            
            elif cmd == "quit" or cmd == "q" or cmd == "exit":
                self.handle_exit()
            
            elif cmd == "volume":
                if args is None:
                    print("Please specify volume value!")
                    continue
                amount = self.player.volume
                try:
                    amount = int(args)
                except ValueError:
                    print("Invalid Volume Value")
                try:
                    self.player.set_volume(float(amount)/10.0)
                except PlayerInvalidVolumeChange:
                    print("Volume Value must be between 0 and 10")
            
            # elif cmd == "forward":
            #     if args is None:
            #         print("Please specify forward skip seconds!")
            #         continue
            #     amount = 0
            #     try:
            #         amount = int(args)
            #     except ValueError:
            #         print("Invalid number of seconds to skip!")
            #     self.player.skip_forward(amount)
            
            # elif cmd == "backward":
            #     if args is None:
            #         print("Please specify backward skip seconds!")
            #         continue
            #     amount = 0
            #     try:
            #         amount = int(args)
            #     except ValueError:
            #         print("Invalid number of seconds to skip!")
            #     self.player.skip_backward(amount)

            # TODO: Play Queue Support
                # TODO: Skip Current Episode

            elif cmd == "restart":
                self.player.restart()

            else:
                print("Invalid Command!")

    def show_all(self):
        # TODO: Pagination
        if not self.manager.channels.keys():
            print("No Podcasts Available Yet!")
            return
        
        for i, pair in enumerate(self.manager.channels.items()):
            channel = pair[1]
            print(f"{i}) {channel.title}")
            for i, item in enumerate(channel.items):
                print(
                    f"  {i}) {item.downloaded} {item.title} ({item.enclosure.url})")
    
    def show_items(self, channel):
        if channel.title not in self.manager.title_to_url:
            print(f"Podcast {channel.title} doesn't Exist!")
            return
        print(f"{channel.title}")
        for i, item in enumerate(channel.items):
            print(f"  {i}) {item.title} ({item.enclosure.url})")

    def show_channels(self):
        if not self.manager.channels.keys():
            print("No Podcasts Available Yet!")
            return
        for i, pair in enumerate(self.manager.channels.items()):
            channel = pair[1]
            print(f"{i}) {channel.title}")

    def select_channel(self, purpose):
        while True:

            # TODO: Paginate Results if they are greater than 10 (or some other value)
            channels = list(self.manager.channels.values())
            self.show_channels()

            try:
                channel_index = int(input(f"Which Channel do you want to {purpose} from? "))
            except ValueError:
                print("Invalid Input!")
                continue

            if channel_index > len(self.manager.channels.keys()) or channel_index < 0:
                print(f"Option must be between {0} and {len(self.manager.channels.keys())}")
                continue

            return self.manager.channels[self.manager.title_to_url[channels[channel_index].title]]
    
    def select_item(self, channel, purpose):
        while True:

            # TODO: Paginate Results if they are greater than 10 (or some other value)
            self.show_items(channel)

            try:
                item_index = int(input(f"Which item do you want to {purpose}? "))
            except ValueError:
                print("Invalid Input!")
                continue

            if item_index > len(channel.items) or item_index < 0:
                print(f"Option must be between {0} and {len(channel.items)-1}")
                continue

            return item_index

    def select_item_indexes(self, channel, purpose):
        cont = True
        while cont:

            cont = False
            # TODO: Paginate Results if they are greater than 10 (or some other value)
            self.show_items(channel)
            item_indexes = input(f"Which Items do you want {purpose}? ")

            try:
                item_indexes = list(map(int, item_indexes.split(" ")))
            except ValueError:
                print("Invalid Input!")
                cont = True
                continue

            for i in item_indexes:
                if i > len(channel.items) or i < 0:
                    print(f"Options must be between {0} and {len(channel.items)-1}")
                    cont = True
                    break

        return item_indexes

if __name__ == "__main__":
    cast = YCast()
    cast.start()
