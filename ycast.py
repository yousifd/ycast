#! /usr/bin/python3

import logging
import signal
import sys
import threading
import os
import pickle

from manager import Manager
from player import Player, PlayerInvalidVolumeChange
from paginator import Paginator, FirstPageException, LastPageException

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
        self.wait_for_all_threads()
        with open("config/manager.pkl", "wb") as output:
            pickle.dump(self.manager, output, pickle.HIGHEST_PROTOCOL)
        with open("config/player.pkl", "wb") as output:
            pickle.dump(self.player, output, pickle.HIGHEST_PROTOCOL)
        self.quit = True
        print("Goodbye!")

    def wait_for_all_threads(self):
        for thread in self.threads:
            if thread.is_alive():
                print(f"Waiting for: {thread.name}")
            thread.join()
    
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
                if channel is not None:
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
                if channel is not None:
                    self.manager.unsubscribe_from_channel(channel.title)
            
            elif cmd == "list" or cmd == "ls":
                self.wait_for_all_threads()
                self.show_all()
            
            elif cmd == "download" or cmd == "d":
                channel = self.select_channel("Download")
                if channel is not None:
                    item_indexes = self.select_item_indexes(channel, "Download")
                    if item_indexes is not None:
                        for item_index in item_indexes:
                            item = channel.items[item_index]
                            logging.info(f"Downloading {item.title}")
                            t = threading.Thread(target=self.manager.download_item, args=(item_index, channel), name=f"Downloading {channel.title}: {item.title}")
                            t.start()
                            self.threads.append(t)
            
            elif cmd == "delete" or cmd == "del":
                channel = self.select_channel("Delete")
                if channel is not None:
                    item_indexes = self.select_item_indexes(channel, "Delete")
                    if item_indexes is not None:
                        for item_index in item_indexes:
                            item = channel.items[item_index]
                            t = threading.Thread(target=self.manager.delete_item, args=(item, channel))
                            t.start()
                            self.threads.append(t)
            
            elif cmd == "sync":
                self.manager.update_all()

            elif cmd == "update" or cmd == "u":
                channel = self.select_channel("Update")
                if channel is not None:
                    self.manager.update(channel)

            elif cmd == "play" or cmd == "p":
                # TODO: Ability to go back to channels list
                channel = self.select_channel("Play")
                if channel is not None:
                    item_index = self.select_item(channel, "Play")
                    if item_index is not None:
                        item = channel.items[item_index]
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

            # TODO: Play Queue Support
                # TODO: Skip Current Episode

            elif cmd == "restart":
                self.player.restart()

            else:
                print("Invalid Command!")

    def show_all(self):
        # TODO: Choose Channel then browse items under channel
        if not self.manager.channels.keys():
            print("No Podcasts Available Yet!")
            return
        
        for i, pair in enumerate(self.manager.channels.items()):
            channel = pair[1]
            print(f"{i}) {channel.title}")
            for i, item in enumerate(channel.items):
                print(
                    f"  {i}) {item.title} ({item.enclosure.url})")

    def select_channel(self, purpose):
        channels = list(self.manager.channels.values())
        paginator = Paginator(channels, 0, len(channels))

        if len(channels) == 0:
            print("No Podcasts Available Yet!")
            return

        while True:
            for i, channel in enumerate(paginator.get_current_page()):
                print(f"{i+paginator.current_min}) {channel.title}")

            channel_index = input(f"Which Channel do you want to {purpose} from? ")
            if channel_index == "n":
                try:
                    paginator.get_next()
                except LastPageException:
                    print("Last Page")
            elif channel_index == "b":
                try:
                    paginator.get_prev()
                except FirstPageException:
                    print("First Page")
            elif channel_index == "q":
                break
            else:
                try:
                    channel_index = int(channel_index)
                except ValueError:
                    print("Invalid Input!")
                    continue

                if channel_index > len(self.manager.channels.keys()) or channel_index < 0:
                    print(f"Option must be between {0} and {len(self.manager.channels.keys())}")
                    continue

                return self.manager.channels[self.manager.title_to_url[channels[channel_index].title]]
    
    def select_item(self, channel, purpose):
        items = channel.items
        paginator = Paginator(items, 0, len(items))

        while True:
            print(channel.title)
            for i, item in enumerate(paginator.get_current_page()):
                print(f"  {i+paginator.current_min}) {item.title} ({item.enclosure.url})")

            item_index = input(f"Which item do you want to {purpose}? ")
            if item_index == "n":
                try:
                    paginator.get_next()
                except LastPageException:
                    print("Last Page")
            elif item_index == "b":
                try:
                    paginator.get_prev()
                except FirstPageException:
                    print("First Page")
            elif item_index == "q":
                break
            else:
                try:
                    item_index = int(item_index)
                except ValueError:
                    print("Invalid Input!")
                    continue

                if item_index > len(channel.items) or item_index < 0:
                    print(f"Option must be between {0} and {len(channel.items)-1}")
                    continue

                return item_index

    def select_item_indexes(self, channel, purpose):
        items = channel.items
        paginator = Paginator(items, 0, len(items))

        cont = True
        while cont:
            cont = False
            for i, item in enumerate(paginator.get_current_page()):
                print(f"  {i+paginator.current_min}) {item.title} ({item.enclosure.url})")

            item_indexes = input(f"Which Items do you want {purpose}? ")
            if item_indexes == "n":
                try:
                    paginator.get_next()
                except LastPageException:
                    print("Last Page")
            elif item_indexes == "b":
                try:
                    paginator.get_prev()
                except FirstPageException:
                    print("First Page")
            elif item_indexes == "q":
                break
            else:
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
            cont = True

if __name__ == "__main__":
    cast = YCast()
    cast.start()
