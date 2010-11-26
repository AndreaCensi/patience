from patience.resources import *
from patience.utils import *

class Git(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        self.branch = config.get('branch', 'master')

    def checkout(self):    
        system_cmd_fail('.', 'git clone %s %s' % (self.url, self.destination))

    def fetch(self):
        stdout = system_output(self.destination, 'git fetch')
        if stdout:
            return True
        else:
            return False
            
    def can_be_ff(self):
        stdout = system_output(self.destination,    
          'git rev-list {branch}..origin/{branch}'.format(branch=self.branch))
        if stdout:
            return False
        else:
            return True
            
    def update(self):
        system_cmd_fail(self.destination, 'git fetch')

        if self.can_be_ff():
            system_cmd_fail(self.destination, 'git merge origin/%s %s' % 
                (self.branch, self.branch))
        else:
            print "%s: Will not merge, because more than a FF is required." % r

    def dirty(self):
        command = 'git diff --exit-code --quiet'
        return 0 != system_cmd(self.destination, command) 
    
    def something_to_push(self):
        command = 'git push --dry-run --porcelain'
        output = system_output(self.destination, command)

        # XXX, use instead
        # http://stackoverflow.com/questions/2176278/preview-a-git-push
        if not '=' in output.split('\n \t'):
            return True
        else:
            return False
            
        
    def branches_are_different(self):
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
