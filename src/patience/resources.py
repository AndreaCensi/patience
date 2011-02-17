import os
from .utils import system_cmd_fail

def get_friendly(path):
    
    options = []
    
    options.append(os.path.relpath(path, os.getcwd()))

    home = os.path.expanduser('~')
    
    if path.startswith(home):
        options.append(path.replace(home, '~'))
        
    options.append(path)

    options.sort(key=lambda x: len(x))
    return options[0]

class Resource: 
    def __init__(self, config):
        self.config = config
        self.destination = config['destination']
        self.short_path =get_friendly(self.destination)
        

    def is_downloaded(self):
        return os.path.exists(self.destination)
    
    def __str__(self):
        return self.short_path
    
    def __repr__(self):
        return 'Resource(%r)' % self.destination
    
    def checkout(self):    
        pass

    def update(self):
        pass
        
    def current_revision(self):
        return None

    def something_to_commit(self):
        return False

    def commit(self):
        pass

    def install(self):

        install_type = self.config.get('install', None)
        if install_type is None:
            print "Skipping %s" % self
            return

        if install_type == 'setuptools':
            system_cmd_fail(self.destination, 'python setup.py develop')
        elif install_type == 'cmake':
            system_cmd_fail(self.destination, 'cmake -DCMAKE_INSTALL_PREFIX=${BVENV_PREFIX} .')
            system_cmd_fail(self.destination, 'make')
        
            system_cmd_fail(self.destination, 'make install')
        
        
        else:
            raise Exception('Unknown install type "%s".' % install_type)
