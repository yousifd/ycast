class Enclosure:
    def __init__(self):
        self.url = ""
        self.length = ""
        self.type = ""

    def __str__(self):
        return f'url={self.url} length={self.length} type={self.type}'
