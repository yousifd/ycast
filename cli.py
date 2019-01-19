class CLIException(Exception):
    pass

class TriggerAlreadyExists(CLIException):
    pass

class CLI:
    # TODO: Support default action?
    def __init__(self, mapping=dict()):
        self.mapping = mapping
        self.quit = False

    def add_cmd(self, trigger, action, args=None):
        if trigger in self.mapping:
            print("TRIGGER", trigger, self.mapping)
            raise TriggerAlreadyExists
        self.mapping[trigger] = (action, args)
    
    def add_quit_cmd(self, trigger, action=None, args=None):
        if action is not None:
            self.add_cmd(trigger, self.quit_cmd, args=(action, args))
        else:
            self.add_cmd(trigger, self.quit_cmd)
    
    def quit_cmd(self, action=None, args=None):
        self.quit = True
        if action is not None:
            if args is not None:
                action(*args)
            else:
                action()
    
    def ask(self, prompt):
        line = input(prompt)
        split_line = line.split(" ", 1)
        cmd = split_line[0]
        args = None
        if len(split_line) > 1:
            args = split_line[1]
        
        if cmd not in self.mapping:
            return line
        
        action = self.mapping[cmd][0]
        ext_args = self.mapping[cmd][1]
        if ext_args is not None:
            if args is not None:
                action(args, *ext_args)
            else:
                action(*ext_args)
        else:
            if args is not None:
                action(args)
            else:
                action()
        
        return None
