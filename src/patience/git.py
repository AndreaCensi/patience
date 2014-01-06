import os

from contracts import contract
from system_cmd import system_cmd_result, system_cmd_show, CmdException

from .resources import Resource
from .structures import ActionException


__all__ = ['Git']


class Git(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        self.branch = config.get('branch', 'master')
        
        self.show_operations = False 
        self.show_stdout = False
        
    def is_git_repo(self):
        git = os.path.join(self.destination, '.git')
        return os.path.exists(git)

    def current_branch(self):
        # Note: this fails if it is the initial commit
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

    def has_remote(self):
        return 'origin' in self.runf('git remote')

    def check_has_remote(self):
        if not self.has_remote():
            msg = 'Remote not configured.'
            raise ActionException(msg)

    def check_remote_correct(self):
        self.check_has_remote()
        if not self.is_remote_correct():
            msg = 'The remote is not correct: %s' % self.get_remote_url()
            raise ActionException(msg)
                
    def is_remote_correct(self):
        return self.get_remote_url() == self.url
    
    def get_remote_url(self):
        self.check_has_remote()
        url = self.run('git config --get remote.origin.url')
        return url
        
    def check_branch_exists_remote(self, branch=None):
        """ branch = None => self.branch """
        if branch is None:
            branch = self.branch
        self.check_remote_correct()
        if not self.branch_exists_remote(branch):
            msg = 'Remote branch %r does not exist. (Should be fixable by "push".)' % branch
            raise ActionException(msg)

    def check_local_tracks_remote(self, branch, remote):
        res = self.get_what_tracks(branch)
        if res != remote:
            msg = 'Local branch %s tracks %s, not %s.' % (branch, res, remote)
            raise ActionException(msg)
        
    def get_what_tracks(self, branch):
        # could be none
        cmd = 'git rev-parse --symbolic-full-name --abbrev-ref %s@{u}' % branch
        res = self.run0(cmd, raise_on_error=False)
        if 'fatal' in res.stderr:
            if 'fatal: No upstream configured' in res.stderr:
                return None
            # FIXME
        what = res.stdout
        # print('track %s -> %s' % (branch, what))
        return what

    def branch_exists_remote(self, branch=None):
        """ branch = None => self.branch """
        if branch is None:
            branch = self.branch
        res = self.run0('git show-ref --verify refs/remotes/origin/%s' % branch,
                        raise_on_error=False)
        exists = res.ret == 0
        return exists

    def branch_exists_local(self, branch=None):
        if branch is None:
            branch = self.branch
        res = self.run0('git show-ref --quiet --verify -- refs/heads/%s' % branch,
                        raise_on_error=False)
        exists = res.ret == 0
        return exists
    
    def make_local_branch(self):
        return self.runf('git branch {branch}')

    def checkout(self):
        self.run(['git', 'clone', self.url, self.destination],
                    cwd='.'  # the other was not created yet
                )
        self.checkout_right_branch()

    def run(self, cmd, cwd=None, errmsg=None, raise_on_error=True):
        return self.run0(cmd, cwd, errmsg, raise_on_error=raise_on_error).stdout
    
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
                 
#             s = 'On resource:\n\t%s\n' % self +s
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

    @contract(returns='dict(str:str)')
    def list_remote_branches(self, ignore=['gh-pages']):
        # XXX This uses the network
        """ REturns dictionary branch -> sha """
        out = self.run('git ls-remote --heads origin')
        # f93ffca589ad79a3ad2aad32019bf608d43b0956    refs/heads/env_dvsd
        # b4e8e4a0ec8432de4b6c1c61280199f0f3a270bf    refs/heads/env_fault
        # b4e8e4a0ec8432de4b6c1c61280199f0f3a270bf    refs/heads/master
        branches = {}
        for line in linesplit(out):
            tokens = line.split('\t')
            assert len(tokens) == 2, tokens
            sha = tokens[0]
            ref = tokens[1]
            assert 'refs/heads/' in ref
            branch = ref.replace('refs/heads/', '')
            assert branch
            if branch in ignore:
                continue
            branches[branch] = sha
        
        return branches
    
    @contract(returns='dict(str:tuple(int, bool, int, bool))')
    def list_differences_with_remote_branches(self):
        """
            Compares the current branch to the others in the remote.
            Returns dict rbranch -> npush, simple, nmerge, simple_merge.
        """
        res = {}
        for rbranch in self.list_remote_branches():
            lbranch = self.branch
            if lbranch == rbranch:
                continue
            npush = self.something_to_push_to(lbranch=lbranch, rbranch=rbranch)
            if npush > 0:
                simple_push = self.simple_push_generic(lbranch=lbranch, rbranch=rbranch)
            else:
                simple_push = True
            nmerge = self.something_to_merge_from(lbranch=lbranch, rbranch=rbranch)
            if nmerge > 0:
                simple_merge = self.simple_merge_generic(lbranch=lbranch, rbranch=rbranch)
            else:
                simple_merge = True
            res[rbranch] = (npush, simple_push, nmerge, simple_merge) 
        return res

    def something_to_push_to(self, lbranch, rbranch):
        ''' Returns the number of commits that we can push to a remote
            branch.'''
        self.check_right_branch()
        self.check_remote_correct()
        self.check_branch_exists_remote(rbranch)

        if not self.branch_exists_remote(rbranch):
            raise ValueError('%s: The remote branch %r does not exist.' % (self, rbranch))
        
        output = self.runf('git log origin/{rbranch}..{lbranch} --no-merges --pretty=oneline',
                           rbranch=rbranch, lbranch=lbranch)
        commits = linesplit(output)
        return len(commits)
    
    def something_to_merge_from(self, lbranch, rbranch):
        ''' Returns the number of commits that we can merge from a remote branch.'''
        self.check_right_branch()
        self.check_remote_correct()
        # if not self.branch_exists_remote():
        #    return 0
        if not self.branch_exists_remote(rbranch):
            raise ValueError(rbranch)
        output = self.runf('git log  {lbranch}..origin/{rbranch} --no-merges --pretty=oneline',
                           rbranch=rbranch, lbranch=lbranch)
        commits = linesplit(output)
        return len(commits)
    
    def simple_merge_generic(self, lbranch, rbranch):
        ''' Checks that the local lbranch can be fast forwarded to rbranch. '''
        self.check_remote_correct()
        self.check_branch_exists_remote(rbranch)
        rev = self.runf('git rev-parse {lbranch}', lbranch=lbranch).strip()
        base = self.runf('git merge-base {rev} origin/{rbranch}', rev=rev, rbranch=rbranch)
        if rev == base.strip():
            return True
        else:
            return False
    
    def simple_push_generic(self, lbranch, rbranch):
        ''' Returns true if we can do a safe push (assuming we have the last
            revision of the remote branch.) '''
        self.check_remote_correct()
#         if not self.branch_exists_remote():
#             return True

        stdout = self.runf('git rev-list {lbranch}..origin/{rbranch}',
                           lbranch=lbranch, rbranch=rbranch)
        if stdout.strip():
            return False
        else:
            return True
        
    def something_to_push(self):
        ''' Returns the number of commits that we can push to the remote
            branch.'''
        self.check_right_branch()
        self.check_remote_correct()

        # XXX: need to make general
#         self.check_local_tracks_remote(self.branch, 'origin/%s' % self.branch)

        if not self.branch_exists_remote():
            # print('need to push brnach')
            # we need to push the branch, at least
            return 1 
        
        command = 'git log origin/{branch}..{branch} --no-merges --pretty=oneline'
        output = self.runf(command)
        commits = linesplit(output)
#         print('%s -> %s' % (command, commits))
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

    def set_upstream(self, branch, upstream):
        cmd = 'git branch --set-upstream %s %s' % (branch, upstream)
        self.run(cmd)


def linesplit(s):
    ''' Splits a string in lines; removes empty. '''
    return filter(lambda x: x, s.split('\n'))
    
