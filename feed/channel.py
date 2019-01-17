class Channel:
    def __init__(self):
        # Spec
        self.items = []
        self.title = ""
        self.link = ""
        self.description = ""
        # Optional
        self.language = ""
        self.copyright = ""
        self.managingEditor = ""
        self.webMaster = ""
        self.pubDate = ""
        self.lastBuildDate = ""
        self.category = []
        self.generator = ""
        self.docs = ""
        self.cloud = None
        self.ttl = 60
        self.image = None
        self.textInput = None
        self.skipHours = ""
        self.skipDays = ""

    def info_str(self):
        # TODO: String of Information
        pass

    def __str__(self):
        return self.title