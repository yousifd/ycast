class CLIException(Exception):
    pass

class TriggerAlreadyExists(CLIException):
    pass

class CLI:
    def __init__(self, mapping=dict()):
        self.mapping = mapping
    
    def quit_(self):
        self.quit = True

    def add_cmd(self, trigger, action):
        if trigger in self.mapping:
            raise TriggerAlreadyExists
        self.mapping[trigger] = action
    
    def ask(self, preprompt, prompt):
        line = input(prompt)
        line = line.split(" ", 1)
        cmd = line[0]
        args = None
        if len(line) > 1:
            args = line[1]
        
        if cmd not in self.mapping:
            return line
        
        if args is not None:
            self.mapping[cmd](args)
        else:
            self.mapping[cmd]()
        
        return None