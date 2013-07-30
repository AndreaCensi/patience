from .resources import Resource
from .utils import  system_cmd_result, system_cmd_show, CmdException

from .structures import ActionException

class Git(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        self.branch = config.get('branch', 'master')
        
        self.show_operations = False 
        self.show_stdout = False
        
    def current_branch(self):
        branch = self.run('git rev-parse --abbrev-ref HEAD').strip()
        
        return branch + ''

    def check_right_branch(self):
        """ Raise exception if we are not on the right branch. """
        if not self.is_right_branch():
            cur_branch = self.current_branch()
            msg = ('Currently on branch %r rather than %r' % 
                    (cur_branch, self.branch)) 
            raise ActionException(msg)
    
    def checkout_right_branch(self):
        return self.runf('git checkout {branch}') 
    
    def is_right_branch(self):
        """ return false  if we are not on the branche
            declared in the configuration. """
        cur_branch = self.current_branch()
        return cur_branch == self.branch
            
    def check_remote_correct(self):
        if not self.is_remote_correct():
            msg = 'The remote is not correct: %s' % self.get_remote_url()
            raise ActionException(msg)
                
    def is_remote_correct(self):
        return self.get_remote_url() == self.url
    
    def get_remote_url(self):
        url = self.run('git config --get remote.origin.url')
        return url
        
    def check_branch_exists_remote(self):
        self.check_remote_correct()
        if not self.branch_exists_remote():
            msg = 'Remote branch %r does not exist.' % self.branch
            raise ActionException(msg)
            
    def branch_exists_remote(self):
        res = self.run0('git show-ref --verify refs/remotes/origin/%s' % self.branch,
                        raise_on_error=False)
        exists = res.ret == 0
        return exists

    def branch_exists_local(self):
        res = self.run0('git show-ref --quiet --verify -- refs/heads/%s' % self.branch,
                        raise_on_error=False)
        exists = res.ret == 0
        return exists
    
    def make_local_branch(self):
        return self.runf('git branch {branch}')

    def checkout(self):
        self.run(['git', 'clone', self.url, self.destination],
                    cwd='.'  # the other was not created yet
                )

    def run(self, cmd, cwd=None, errmsg=None): 
        return self.run0(cmd, cwd, errmsg).stdout
    
    def run0(self, cmd, cwd=None, errmsg=None, raise_on_error=True): 
        try:
            if cwd is None: 
                cwd = self.destination
                
            display_prefix = '%-30s: ' % self.short_path
            
            if self.show_operations:
                print(display_prefix + ' %s ' % cmd)
               
            display_prefix = '%-30s  ' % ''
            res = system_cmd_result(cwd, cmd,
                                    raise_on_error=raise_on_error,
                                    display_stdout=self.show_operations,
                                    display_stderr=self.show_operations,
                                    display_prefix=display_prefix
                                    )
            return res
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
            
    def f(self, f, **args):
        ''' formats a string '''
        return f.format(branch=self.branch, **args)

    def runf(self, f, **args):
        ''' Formats and runs a command. '''
        return self.run(self.f(f, **args))
        
    def badconf(self, e):
        raise ActionException(e)

    def fetch(self):
        self.check_remote_correct()
        self.run('git fetch')
            
    def update(self):
        self.fetch()
        self.merge()

    def merge(self):
        self.check_remote_correct()
        self.check_right_branch()
        self.check_branch_exists_remote()
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
        command = 'git ls-files --others --exclude-standard'  # ' --directory'
        output = self.run(command)
        files = linesplit(output)
        return len(files)
    
    def something_to_push(self):
        ''' Returns the number of commits that we can push to the remote
            branch.'''
        self.check_right_branch()
        self.check_remote_correct()
        if not self.branch_exists_remote():
            # print('need to push brnach')
            # we need to push the branch, at least
            return 1 
        
        command = 'git log origin/{branch}..{branch} --no-merges --pretty=oneline'
        output = self.runf(command)
        commits = linesplit(output)
        return len(commits)

    def something_to_merge(self):
        ''' Returns the number of commits that we can merge from remote branch.'''
        self.check_right_branch()
        self.check_remote_correct()
        if not self.branch_exists_remote():
            return 0
        
        command = 'git log {branch}..origin/{branch} --no-merges --pretty=oneline'
        output = self.runf(command)
        commits = linesplit(output)
        return len(commits)
    
    def simple_merge(self):
        ''' Checks that our branch can be fast forwarded. '''
        self.check_right_branch() 
        self.check_remote_correct()
        self.check_branch_exists_remote()
        rev = self.runf('git rev-parse {branch}').strip()
        base = self.runf('git merge-base {rev} origin/{branch}', rev=rev)
        if rev == base.strip():
            return True
        else:
            return False
    
    def simple_push(self):
        ''' Returns true if we can do a safe push (assuming we have the last
            revision of the remote branch.) '''
        self.check_right_branch()
        self.check_remote_correct()
        if not self.branch_exists_remote():
            return True

        stdout = self.runf('git rev-list {branch}..origin/{branch}')
        if stdout.strip():
            return False
        else:
            return True
    
    def commit(self):
        self.check_right_branch()
        if self.num_modified():
            n = self.num_untracked()
            if n > 0:
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
        self.check_right_branch()
        self.check_remote_correct()

        if not self.simple_push():
            self.badcond("Cannot push because of conflicts.")
            
        self.runf('git push origin {branch}')
            

    def current_revision(self):
        out = self.run('git rev-parse HEAD')
        out = out.split()[0]
        return out

def linesplit(s):
    ''' Splits a string in lines; removes empty. '''
    return filter(lambda x: x, s.split('\n'))
    
