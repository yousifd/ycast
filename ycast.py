import readline
import logging

from manager import Manager

class YCast:
    def __init__(self):
        self.manager = Manager()
    
    def start(self):
        # RT https://roosterteeth.com/show/rt-podcast/feed/mp3
        # GRC http://leoville.tv/podcasts/sn.xml
        # CC https://corridorcast.libsyn.com/rss
        # TODO: Deal with force quitting
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
            
            elif cmd == "subscribe" or cmd == "sub" or cmd == "add":
                for url in args.split(" "):
                    self.manager.subscribe_to_podcast(url)
            
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
                self.manager.download_podcast(self.manager.channels["Corridor Cast"].items[0])
            
            elif cmd == "delete" or cmd == "del":
                # TODO: Delete Downloaded Episodes
                podcast = args[0]
                for i in args[1:]:
                    item = self.manager.channels[podcast].items[int(i)]
                    self.manager.delete_podcast(item)
            
            elif cmd == "update" or cmd == "u":
                # TODO: Check for episode updates
                self.manager.update()
                pass
            
            elif cmd == "quit" or cmd == "q" or cmd == "exit":
                self.manager.store_channels()
                quit = True
                print("Goodbye!")

            else:
                print("Invalid Command!")
