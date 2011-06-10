from .resources import Resource
from .utils import  system_cmd_result, system_cmd_show, CmdException

from .structures import ActionException

class Git(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        self.branch = config.get('branch', 'master')
        self.show_operations = False 

    def checkout(self):
        self.run(['git', 'clone', self.url, self.destination],
                    cwd='.' # the other was not created yet
                )

    def run(self, cmd, cwd=None,errmsg=None): 
        try:
            if cwd is None: 
                cwd = self.destination
                
            if self.show_operations:
               print('%-30s: %s' % (self.short_path, cmd))
               
            res = system_cmd_result(cwd, cmd,
                                    raise_on_error=True,
                                    display_stdout=self.show_operations,
                                    display_stderr=self.show_operations,
                                    display_prefix=self.short_path
                                    )
            return res.stdout
        except CmdException as e:
            if errmsg:
                s = '%s\n' % errmsg
            else:
                s = 'Command %r failed with error code %d.' % (cmd, e.res.ret)
                if e.res.stdout:
                    s += ' stdout: %r ' % e.res.stdout
                if e.res.stderr:
                    s += ' stderr: %r ' % e.res.stderr          
                
            raise ActionException(s)
            
    def f(self,f,**args):
        ''' formats a string '''
        return f.format(branch=self.branch,**args)

    def runf(self,f,**args):
        ''' Formats and runs a command. '''
        return self.run(self.f(f,**args))
    
        
    def badconf(self, e):
        raise ActionException(e)

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
        ''' Returns the number of commits that we can push to the remote
            branch.'''
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
                self.run(self.destination, ['git', 'commit', '-a', '-m', msg])
    
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
    
