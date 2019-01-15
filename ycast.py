import readline
import logging

from manager import Manager

class YCast:
    def __init__(self):
        self.manager = Manager()
    
    def start(self):
        # RT https://roosterteeth.com/show/rt-podcast/feed/mp3
        # GRC http://leoville.tv/podcasts/sn.xml
        quit = False
        while not quit:
            line = input("ycast> ")
            logging.debug(line)
            line = line.split(" ")
            cmd = line[0]
            if cmd == "help" or cmd == "h":
                # TODO: Print Usage
                print("HELP")
            elif cmd == "subscribe" or cmd == "sub":
                for url in line[1:]:
                    self.manager.subscribe_to_podcast(url)
            elif cmd == "list" or cmd == "ls":
                self.manager.show_channels()
            elif cmd == "download" or cmd == "d":
                for url in line[1:]:
                    # TODO: self.manager.download_podcast(url, )
                    pass
            elif cmd == "delete" or cmd == "del":
                # TODO: Delete downloaded Podcasts
                continue
            elif cmd == "quit" or cmd == "q":
                quit = True
                print("Goodbye!")
            else:
                print("Invalid Command!")
