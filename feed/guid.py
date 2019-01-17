class GUID:
    def __init__(self):
        self.value = ""
        self.isPermaLink = True
    
    def __str__(self):
        return self.value
    
    def __hash__(self):
        return self.value
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __ne__(self, other):
        return not (self.value == other.value)