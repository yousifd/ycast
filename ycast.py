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

            elif cmd == "cinfo" or cmd == "ci":
                self.get_channel_apply("Info", lambda c: print(c.info_str()))
            
            elif cmd == "iinfo" or cmd == "ii":
                self.get_items_apply("Info", lambda i, c: print(i.info_str()))
            
            elif cmd == "subscribe" or cmd == "sub" or cmd == "add":
                if args is None:
                    print("Please specify a Podcast to subscribe to!")
                    continue
                for url in args.split(" "):
                    t = threading.Thread(target=self.manager.subscribe_to_channel, args=(url,), name=f"Subscribing to {url}") # TODO: Move into manager
                    t.start()
                    self.threads.append(t)
            
            elif cmd == "unsubscribe" or cmd == "unsub" or cmd == "remove":
                self.get_channel_apply("Unsubscribe", self.manager.unsubscribe_from_channel)
            
            elif cmd == "list" or cmd == "ls":
                self.wait_for_all_threads()
                self.show_all()
            
            elif cmd == "download" or cmd == "d":
                # TODO: Use universal function
                item_indexes = None
                while item_indexes is None:
                    channel = self.select_channel("Download")
                    if channel is not None:
                        item_indexes = self.select_item_indexes(channel, "Download")
                        if item_indexes is not None:
                            for item_index in item_indexes:
                                item = channel.items[item_index]
                                logging.info(f"Downloading {item.title}")
                                t = threading.Thread(target=self.manager.download_item, args=(item, channel), name=f"Downloading {channel.title}: {item.title}") # TODO: Move into manager
                                t.start()
                                self.threads.append(t)
                    else:
                        break
            
            elif cmd == "delete" or cmd == "del":
                # TODO: Use universal function
                item_indexes = None
                while item_indexes is None:
                    channel = self.select_channel("Delete")
                    if channel is not None:
                        item_indexes = self.select_item_indexes(channel, "Delete")
                        if item_indexes is not None:
                            for item_index in item_indexes:
                                item = channel.items[item_index]
                                t = threading.Thread(target=self.manager.delete_item, args=(item, channel)) # TODO: Move into manager
                                t.start()
                                self.threads.append(t)
                    else:
                        break
            
            elif cmd == "sync":
                updates = self.manager.update_all()
                print(updates)

            elif cmd == "update" or cmd == "u":
                self.get_channel_apply("Update", self.update_channel)

            elif cmd == "play" or cmd == "p":
                self.get_items_apply("Play", self.player.play)

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

            elif cmd == "restart":
                self.player.restart()

            else:
                print("Invalid Command!")

    def update_channel(self, channel):
        update = self.manager.update(channel)
        print(update)

    def show_all(self):
        item_index = None
        while item_index is None:
            channel = self.select_channel("List")
            if channel is not None:
                paginator = Paginator(channel.items)

                while True:
                    for i, item in enumerate(paginator.get_current_page()):
                        print(f"  {i+paginator.current_min}) {item.title} ({item.enclosure.url}) Downloaded={item.downloaded}")

                    item_index = input(f"{channel.title}> ")
                    if item_index == "n":
                        try:
                            paginator.get_next()
                        except LastPageException:
                            print("Last Page")
                    elif item_index == "p":
                        try:
                            paginator.get_prev()
                        except FirstPageException:
                            print("First Page")
                    elif item_index == "q":
                        item_index = None
                        break
                    else:
                        print("Invalid Command!")
            else:
                break
    
    def get_channel_apply(self, purpose, action):
        channel = self.select_channel(purpose)
        if channel is not None:
            action(channel)
    
    def get_items_apply(self, purpose, action):
        item_indexes = None
        while item_indexes is None:
            channel = self.select_channel(purpose)
            if channel is not None:
                item_indexes = self.select_item_indexes(channel, purpose)
                if item_indexes is not None:
                    for item_index in item_indexes:
                        item = channel.items[item_index]
                        action(item, channel)
            else:
                break

    def select_channel(self, purpose):
        channels = list(self.manager.channels.values())
        paginator = Paginator(channels)

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
            elif channel_index == "p":
                try:
                    paginator.get_prev()
                except FirstPageException:
                    print("First Page")
            elif channel_index == "q":
                channel_index = None
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
        paginator = Paginator(items)

        while True:
            print(channel.title)
            for i, item in enumerate(paginator.get_current_page()):
                print(f"  {i+paginator.current_min}) {item.title} ({item.enclosure.url}) Downloaded={item.downloaded}")

            item_index = input(f"Which item do you want to {purpose}? ")
            if item_index == "n":
                try:
                    paginator.get_next()
                except LastPageException:
                    print("Last Page")
            elif item_index == "p":
                try:
                    paginator.get_prev()
                except FirstPageException:
                    print("First Page")
            elif item_index == "q":
                item_index = None
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
        paginator = Paginator(items)

        cont = True
        while cont:
            cont = False
            for i, item in enumerate(paginator.get_current_page()):
                print(f"  {i+paginator.current_min}) {item.title} ({item.enclosure.url}) Downloaded={item.downloaded}")

            item_indexes = input(f"Which Items do you want {purpose}? ")
            if item_indexes == "n":
                try:
                    paginator.get_next()
                except LastPageException:
                    print("Last Page")
            elif item_indexes == "p":
                try:
                    paginator.get_prev()
                except FirstPageException:
                    print("First Page")
            elif item_indexes == "q":
                item_indexes = None
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
