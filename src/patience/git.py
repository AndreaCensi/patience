from .resources import Resource
from .utils import system_output, system_cmd_fail, system_cmd_show, system_run

from .structures import ActionException

class Git(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        self.branch = config.get('branch', 'master')

    def checkout(self):    
        system_cmd_fail('.', 'git clone %s %s' % (self.url, self.destination))

    def run(self, cmd, errmsg=None):
        ret, stdout, stderr = system_run(self.destination, cmd)
        if ret != 0:
            if errmsg:
                e = '%s\n' % errmsg
            else:
                e = ''
            e += "Command %r returned %d." % (cmd, ret)
            if stdout:
                e += '\n--- output --- \n%s--- (end)' % stdout
            if stderr:
                e += '\n--- stderr --- \n%s--- (end)' % stderr
            raise ActionException(e)
        return stdout
        
    def f(self,f,**args):
        ''' formats a string '''
        return f.format(branch=self.branch,**args)

    def runf(self,f,**args):
        ''' Formats and runs a command. '''
        return self.run(self.f(f,**args))
    
        
    def badconf(self, e):
        raise ActionException("%s: %s" % (self, e))

    def fetch(self):
        self.run('git fetch')
            
    def update(self):
        self.fetch()
        self.merge()

    def merge(self):
        if self.something_to_merge():
            if self.simple_merge():
                self.runf('git merge origin/{branch}')
            else:
                self.badcond("Cannot merge, because more than a FF is required.")
    

    def num_modified(self):
        output = self.run('git ls-files -m -d')
        files = linesplit(output)
        return len(files)

    def num_untracked(self):
        command = 'git ls-files --others --exclude-standard' #' --directory'
        output = self.run(command)
        files = linesplit(output)
        return len(files)
    
    def something_to_push(self):
        ''' Returns the number of commits that we can push to the remote branch.'''
        command = 'git log origin/{branch}..{branch} --no-merges --pretty=oneline'
        output = self.runf(command)
        commits = linesplit(output)
        return len(commits)

    def something_to_merge(self):
        ''' Returns the number of commits that we can merge from remote branch.'''
        command = 'git log {branch}..origin/{branch} --no-merges --pretty=oneline'
        output = self.runf(command)
        commits = linesplit(output)
        return len(commits)
    
    def simple_merge(self):
        ''' Checks that our branch can be fast forwarded. ''' 
        rev =  self.runf('git rev-parse {branch}').strip()
        base = self.runf('git merge-base {rev} origin/{branch}',rev=rev)
        if rev == base.strip():
            return True
        else:
            return False
    
    def simple_push(self):
        ''' Returns true if we can do a safe push (assuming we have the last
            revision of the remote branch.) '''
        stdout = self.runf('git rev-list {branch}..origin/{branch}')
        if stdout.strip():
            return False
        else:
            return True
    
    def commit(self):
        if self.num_modified():
            n = self.num_untracked()
            if n > 0 :
                self.badcond("Cannot commit; there are %s untracked files." % n)
            else: 
                # TODO
                system_cmd_show(self.destination, 'git status')
                try:
                    msg = raw_input('message: ')
                except Exception as e:
                    print e
                    return
                system_cmd_fail(self.destination, ['git', 'commit', '-a', '-m', msg])
    
    def push(self):
        if self.simple_push():
            self.run('git push')
        else:
            self.badcond("Cannot push because of conflicts.")

    def current_revision(self):
        out = self.run('git rev-parse HEAD')
        out = out.split()[0]
        return out

def linesplit(s):
    ''' Splits a string in lines; removes empty. '''
    return filter(lambda x:x, s.split('\n'))
    
