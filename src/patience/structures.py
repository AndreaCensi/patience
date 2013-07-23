
class ActionException(Exception):
    pass

class ConfigException(Exception):
    def __init__(self, error, config):
        self.error = error
        self.config = config
        
    def __str__(self):
        return "%s\n%s" % (self.error, self.config)
