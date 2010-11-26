import os

class Resource: 
    def __init__(self, config):
        self.config = config
        self.destination_orig = config['destination']
        self.destination = os.path.expanduser(os.path.expandvars(self.destination_orig))
    
    def is_downloaded(self):
        return os.path.exists(self.destination)
    
    def __str__(self):
        return self.destination
    
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
            system_cmd_fail(self.destination, 'make' )
        
            system_cmd_fail(self.destination, 'make install')
        
        
        else:
            raise Exception('Uknown install type "%s".' % install_type)
