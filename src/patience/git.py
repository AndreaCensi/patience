from patience.resources import *
from patience.utils import *

class Git(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        self.branch = config.get('branch', 'master')

    def checkout(self):    
        system_cmd_fail('.', 'git clone %s %s' % (self.url, self.destination))

    def update(self):
        system_cmd_fail(self.destination, 'git fetch')
        system_cmd_fail(self.destination, 'git pull origin %s' % self.branch)

    def dirty(self):
        command = 'git diff --exit-code --quiet'
        return 0 != system_cmd(self.destination, command) 
    
    def something_to_push(self):
        command = 'git diff --exit-code --quiet origin/%s %s' % (self.branch, self.branch)
        return 0 != system_cmd(self.destination, command) 

    def something_to_commit(self):
        return self.dirty()
        
    def commit(self):
        if self.something_to_commit():
            system_cmd_fail(self.destination, 'git commit -a' )
        system_cmd_fail(self.destination, 'git push')

    def current_revision(self):
        out = system_output('cd %s && git rev-parse HEAD' % self.destination)    
        out = out.split()[0]
        return out