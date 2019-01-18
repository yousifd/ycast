import html2text

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
        self.filename = ""
        self.downloaded = False
        self.progress = 0
    
    def info_str(self):
        h = html2text.HTML2Text()
        res = []
        res.append(f"{self.title} ({self.enclosure.url})\n")
        if self.author:
            res.append(f"Author: {self.author}\n")
        if self.pubDate:
            res.append(f"Published On: {self.pubDate}\n")
        if self.category:
            for category in self.category:
                if category == self.category[-1]:
                    res.append(f"{category.value}\n")
                else:
                    res.append(f"{category.value}, ")
        if self.guid:
            res.append(f"GUID: {self.guid}\n")
        if self.comments:
            res.append(f"Comments: {self.comments}\n")
        res.append(f"Description: {h.handle(self.description)}\n")
        res.append(f"Downloaded: {self.downloaded}")
        return "".join(res)
    
    def __str__(self):
        return self.title
