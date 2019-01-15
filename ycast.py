from manager import Manager

class YCast:
    def __init__(self):
        self.manager = Manager()
    
    def start(self):
        # RT https://roosterteeth.com/show/rt-podcast/feed/mp3
        # GRC http://leoville.tv/podcasts/sn.xml
        quit = False
        while not quit:
            cmd = input("Options\n1) Manage Subscriptions\n2) Browse Podcasts\n3) Quit\n> ")
            cmd = int(cmd)
            if not isinstance(cmd, int):
                print("Invalid Command!")
                continue
            if cmd == 1:
                print("Manage Subscriptions")
            elif cmd == 2:
                print("Browse Podcasts")
            elif cmd == 3:
                quit = True
            else:
                print("Invalid Command!")
        print("Exiting")
