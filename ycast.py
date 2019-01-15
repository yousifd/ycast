import logging
import signal
import sys

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
            
            elif cmd == "info" or cmd == "i":
                # TODO: Print Podcast Info
                pass
            
            elif cmd == "subscribe" or cmd == "sub" or cmd == "add":
                for url in args.split(" "):
                    self.manager.subscribe_to_podcast(url)
            
            elif cmd == "unsubscribe" or cmd == "unsub" or cmd == "remove":
                # TODO: Implement Unsubscribe
                pass
            
            elif cmd == "list" or cmd == "ls":
                self.manager.show_channels()
            
            elif cmd == "download" or cmd == "d":
                # TODO: Download Episodes
                # Possibly show list and be able to move through it using arrow keys
                # Maps options to episode item
                # args = args.split(" ")
                # podcast = args[0]
                # for i in args[1:]:
                #     item = self.manager.channels[podcast].items[int(i)]
                #     self.manager.download_podcast(item)
                pass
            
            elif cmd == "delete" or cmd == "del":
                # TODO: Delete Downloaded Episodes
                # podcast = args[0]
                # for i in args[1:]:
                #     item = self.manager.channels[podcast].items[int(i)]
                #     self.manager.delete_podcast(item)
                pass
            
            elif cmd == "update" or cmd == "u":
                self.manager.update()

            elif cmd == "play" or cmd == "p":
                # TODO: Play Audio: Streamed or Downloaded
                pass
            
            elif cmd == "quit" or cmd == "q" or cmd == "exit":
                self.manager.store_channels()
                quit = True
                print("Goodbye!")

            else:
                print("Invalid Command!")
