#! /usr/bin/python3

import logging
import signal
import sys
import threading

from manager import Manager
from player import Player

class YCast:
    def __init__(self):
        self.quit = False
        self.manager = Manager()
        self.player = Player()
        self.threads = []

        signal.signal(signal.SIGINT, self.handle_exit_sig)
    
    def handle_exit_sig(self, sig, frame):
        self.handle_exit()
        sys.exit(0)

    def handle_exit(self):
        self.player.quit()
        self.manager.store_channels()
        for thread in self.threads:
            if thread.is_alive():
                print(f"Waiting for: {thread.name}")
            thread.join()
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
            if len(line) > 1:
                args = line[1]

            if cmd == "help" or cmd == "?":
                # TODO: Print Usage
                pass

            elif cmd == "":
                continue
            
            elif cmd == "info" or cmd == "i":
                # TODO: Print Channel Info
                pass
            
            elif cmd == "subscribe" or cmd == "sub" or cmd == "add":
                for url in args.split(" "):
                    t = threading.Thread(target=self.manager.subscribe_to_channel, args=(url,), name=f"Subscribing to {url}")
                    t.start()
                    self.threads.append(t)
            
            elif cmd == "unsubscribe" or cmd == "unsub" or cmd == "remove":
                channel = self.select_channel("Unsubscribe")
                self.manager.unsubscribe_from_channel(channel.title)
            
            elif cmd == "list" or cmd == "ls":
                # TODO: Pagination
                self.manager.show_all()
            
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
            
            # TODO: Set Volume
            # TODO: Skip

            elif cmd == "restart":
                self.player.restart()

            else:
                print("Invalid Command!")

    def select_channel(self, purpose):
        while True:

            # TODO: Paginate Results if they are greater than 10 (or some other value)
            channels = list(self.manager.channels.values())
            self.manager.show_channels()

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
            self.manager.show_items(channel)

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
            self.manager.show_items(channel)
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
