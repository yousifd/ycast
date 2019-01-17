class Item:
    def __init__(self):
        # Spec
        self.title = ""
        self.link = ""
        self.description = ""
        # Optional
        self.author = ""
        self.category = []
        self.comments = ""
        self.enclosure = None
        self.guid = None
        self.pubDate = ""
        self.source = None

        # Internal
        self.downloaded = False
        self.progress = 0