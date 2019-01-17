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
        res = []
        res.append(f"{self.title} ({self.link})\n")
        if self.language:
            res.append(f"Language: {self.language}\n")
        if self.copyright:
            res.append(f"Copyright: {self.copyright}\n")
        if self.category:
            for category in self.category:
                if category == self.category[-1]:
                    res.append(f"{category.value}\n")
                else:
                    res.append(f"{category.value}, ")
        res.append(f"Description: {self.description}")
        return "".join(res)

    def __str__(self):
        return self.title
