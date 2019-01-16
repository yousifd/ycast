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
        self.threads = []

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
                    t = threading.Thread(target=self.manager.subscribe_to_podcast, args=(url,), name=f"Subscribing to {url}")
                    t.start()
                    self.threads.append(t)
            
            elif cmd == "unsubscribe" or cmd == "unsub" or cmd == "remove":
                # TODO: Move Channel selection to standalone function
                channels = list(self.manager.channels.values())
                self.manager.show_channels()
                channel_index = int(input("Which Channel do you want to unsubscribe from? "))
                self.manager.unsubscribe_from_podcast(channels[channel_index])
            
            elif cmd == "list" or cmd == "ls":
                # TODO: Pagination
                self.manager.show_all()
            
            elif cmd == "download" or cmd == "d":
                # TODO: Paginate Results if they are greater than 10 (or some other value)
                # TODO: Move Channel selection and item selection to standalone function
                channels = list(self.manager.channels.values())
                self.manager.show_channels()
                channel_index = int(input("Which Channel do you want to download from? "))
                channel = channels[channel_index]
                self.manager.show_items(channel)
                item_index = int(input("Which Item do you want download? "))
                item = channel.items[item_index]
                t = threading.Thread(target=self.manager.download_podcast, args=(item, channel), name=f"Downloading {channel.title}: {item.title}")
                t.start()
                self.threads.append(t)
            
            elif cmd == "delete" or cmd == "del":
                # TODO: Delete Downloaded Episodes
                # podcast = args[0]
                # for i in args[1:]:
                #     item = self.manager.channels[podcast].items[int(i)]
                #     self.manager.delete_podcast(item)
                pass
            
            # TODO: Sync cmd updates all channels

            elif cmd == "update" or cmd == "u":
                # TODO: Only updates a specific channel
                self.manager.update_all()

            elif cmd == "play" or cmd == "p":
                # TODO: Play Audio: Streamed or Downloaded
                    # Only 1 audio can be played at a time (automatically stop currently running and play new one)
                    # Store current position and start from there next time you play
                pass

            elif cmd == "pause":
                # TODO: Pause Audio
                pass
            
            elif cmd == "unpause" or cmd == "continue":
                # TODO: Unpause Audio:
                pass
            
            elif cmd == "stop":
                # TODO: Stop Audio
                pass
            
            elif cmd == "quit" or cmd == "q" or cmd == "exit":
                self.manager.store_channels()
                for thread in self.threads:
                    print(f"Waiting for: {thread.name}")
                    thread.join()
                quit = True
                print("Goodbye!")

            else:
                print("Invalid Command!")
