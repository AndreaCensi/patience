

class PatienceException(Exception):
    pass

class ActionException(PatienceException):
    pass

class ConfigException(PatienceException):
    def __init__(self, error, config):
        self.error = error
        self.config = config
        
    def __str__(self):
        return "%s\n%s" % (self.error, self.config)


class UserError(PatienceException):
    pass
