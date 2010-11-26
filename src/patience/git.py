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

        if self.something_to_pull():
            if self.can_be_ff():
                print "%s: merging" % self
            
                system_cmd_fail(self.destination, 'git merge origin/%s %s' % 
                    (self.branch, self.branch))
            else:
                print "%s: Will not merge, because more than a FF is required." % self

    def dirty(self):
        command = 'git diff --exit-code --quiet'
        return 0 != system_cmd(self.destination, command) 
        
    def num_modified(self):
        command = 'git ls-files -m -d'
        output = system_output(self.destination, command)
        files = output.split('\n') if output else []
        return len(files)

    def num_untracked(self):
        command = 'git ls-files --other --exclude-standard' #' --directory'
        output = system_output(self.destination, command)
        files = output.split('\n') if output else []
        return len(files)
    
    def something_to_push(self):
        b1 = 'origin/%s' % self.branch
        b2 = self.branch
        command = 'git log {0}..{1} --no-merges'.format(b1,b2)
        output = system_output(self.destination, command)
        if output:
            return True
        else:
            return False

    def something_to_pull(self):
        b1 = self.branch
        b2 = 'origin/%s' % self.branch
        command = 'git log {0}..{1} --no-merges'.format(b1,b2)
#        command = 'git log %s..FETCH_HEAD --no-merges' % self.branch
        output = system_output(self.destination, command)
        if output:
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
            n = self.num_untracked()
            if n >0 :
                print "%s: cannot commit; there are %s untracked files." % (self, n)
            else:
                print "%s: commit" % self
                system_cmd_show(self.destination, 'git status')
                try:
                    msg = raw_input('message: ')
                    system_cmd_fail(self.destination, 'git commit -a -m "%s"' % msg )
                except:
                    print "OK, will not do it"
    
    def push(self):
        if self.can_be_ff():
            system_cmd_fail(self.destination, 'git push')
        else:
            print "%s: cannot push because of conflicts" % self

    def current_revision(self):
        out = system_output('cd %s && git rev-parse HEAD' % self.destination)    
        out = out.split()[0]
        return out
