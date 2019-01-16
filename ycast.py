import logging
import signal
import sys
import threading

from manager import Manager
from player import Player

class YCast:
    def __init__(self):
        self.manager = Manager()
        self.player = Player()

        signal.signal(signal.SIGINT, self.handle_exit)
    
    def handle_exit(self, sig, frame):
        self.manager.store_channels()
        sys.exit(0)
    
    def start(self):
        # RT https://roosterteeth.com/show/rt-podcast/feed/mp3
        # GRC http://leoville.tv/podcasts/sn.xml
        # CC https://corridorcast.libsyn.com/rss
        quit = False
        while not quit:
            line = input("ycast> ")
            logging.debug(line)
            line = line.split(" ", 1)
            cmd = line[0]
            if len(line) > 1:
                args = line[1]

            if cmd == "help" or cmd == "?":
                # TODO: Print Usage
                print("HELP")

            elif cmd == "":
                continue
            
            elif cmd == "info" or cmd == "i":
                # TODO: Print Podcast Info
                pass
            
            elif cmd == "subscribe" or cmd == "sub" or cmd == "add":
                for url in args.split(" "):
                    t = threading.Thread(target=self.manager.subscribe_to_podcast, args=(url,))
                    t.start()
            
            elif cmd == "unsubscribe" or cmd == "unsub" or cmd == "remove":
                channels = list(self.manager.channels.values())
                self.manager.show_channels()
                channel_index = int(input("Which Channel do you want to unsubscribe from? "))
                self.manager.unsubscribe_from_podcast(channels[channel_index])
            
            elif cmd == "list" or cmd == "ls":
                self.manager.show_all()
            
            elif cmd == "download" or cmd == "d":
                # TODO: Paginate Results if they are greater than 10 (or some other value)
                channels = list(self.manager.channels.values())
                self.manager.show_channels()
                channel_index = int(input("Which Channel do you want to download from? "))
                channel = channels[channel_index]
                self.manager.show_items(channel)
                item_index = int(input("Which Item do you want download? "))
                item = channel.items[item_index]
                t = threading.Thread(target=self.manager.download_podcast, args=(item, channel))
                t.start()
            
            elif cmd == "delete" or cmd == "del":
                # TODO: Delete Downloaded Episodes
                # podcast = args[0]
                # for i in args[1:]:
                #     item = self.manager.channels[podcast].items[int(i)]
                #     self.manager.delete_podcast(item)
                pass
            
            elif cmd == "update" or cmd == "u":
                self.manager.update_all()

            elif cmd == "play" or cmd == "p":
                # TODO: Play Audio: Streamed or Downloaded
                pass
            
            elif cmd == "quit" or cmd == "q" or cmd == "exit":
                # TODO: Wait on all downloads (Maybe get a download manager)
                self.manager.store_channels()
                quit = True
                print("Goodbye!")

            else:
                print("Invalid Command!")
