from enum import Enum

class Cloud:
    """
    Its purpose is to allow processes to register with a cloud to be notified of
    updates to the channel, implementing a lightweight publish-subscribe
    protocol for RSS feeds.
    """
    def __init__(self):
        self.domain = ""
        self.port = ""
        self.path = ""
        self.registerProcedure = ""
        self.protocol = ""