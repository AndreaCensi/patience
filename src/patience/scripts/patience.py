#!/usr/bin/env python
import yaml, os, re, sys
import subprocess

def system_cmd(cwd, cmd):
    val = subprocess.call(cmd.split(), cwd=cwd)
    if val != 0:
        pass
        # print "%s: %s : %s" % (val, cwd, cmd)
    return val
    
def system_cmd_fail(cwd, cmd):

    res = system_cmd(cwd,cmd)
    if res != 0:
        raise Exception('Command "%s" failed. (ret value: %s)' % (cmd, res))

def system_output(cmd):
    ''' Gets the output of a command. '''
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    return output
    
class Resource:
    def __init__(self, config):
        self.config = config
        self.destination_orig = config['destination']
        self.destination = expand_environment(self.destination_orig)
        
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
        
        
class Subversion(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        
    def checkout(self):
        system_cmd_fail('.', 'svn checkout %s %s' % (self.url, self.destination))

    def update(self):
        system_cmd_fail(self.destination, 'svn update')

    def something_to_commit(self):
        return "" != system_output('svn status %s' % (self.destination))

    def commit(self):
        system_cmd_fail(self.destination, 'svn commit' )
        
    def current_revision(self):
        out = system_output('svnversion %s' % self.destination)
        out = out.split()[0]
        return out


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
        
    def something_to_commit(self):
        return 0 != system_cmd(self.destination, 'git diff --quiet --exit-code origin/%s' % self.branch)
        
    def commit(self):
        if self.something_to_commit():
            system_cmd_fail(self.destination, 'git commit -a' )
        system_cmd_fail(self.destination, 'git push')
        
    def current_revision(self):
        out = system_output('cd %s && git rev-parse HEAD' % self.destination)    
        out = out.split()[0]
        return out
    
def expand_environment(s):
    while True:
        m = re.match('(.*)\$\{(\w+)\}(.*)', s)
        if not m:
            return s
        before = m.group(1)
        var = m.group(2)
        after = m.group(3)
        if not var in os.environ:
            raise ValueError('Could not find environment variable "%s".' % var)
        sub = os.environ[var]
        s = before + sub + after


def instantiate(config):
    res_type = config['type']
    if res_type == 'subversion':
        return Subversion(config)
    elif res_type == 'git':
        return Git(config)
    elif res_type == 'included':
        return Resource(config)
    else:
        raise Exception('Uknown resource type "%s".' % res_type)

def find_configuration(dir=os.path.curdir, name='resources.yaml'):
    while True:
        dir = os.path.realpath(dir)
        config = os.path.join(dir, name) 
        if os.path.exists(config):
            return config
        
        parent  = os.path.dirname(dir)
        if parent == dir: # reached /
            raise Exception('Could not find configuration "%s".' % name)
        
        dir = parent
        

def main():
    config = find_configuration()
    resources = list(yaml.load_all(open(config)))
    resources = filter(lambda x: x is not None, resources)
    resources = map(instantiate, resources)
    
    
    if len(sys.argv) < 2:
        raise Exception('Please provide command.')
    command = sys.argv[1]
    

    if command == 'checkout':
        for r in resources:
            if not r.is_downloaded():
                print 'Downloading %s...' % r
                r.checkout()
            else:
                print 'Already downloaded %s.' % r 
                
    elif command == 'update':
        for r in resources:
            r.update()

    elif command == 'install':
        for r in resources:
            r.install()

    elif command == 'status':
        for r in resources:
            if not r.is_downloaded():
                raise Exception('Could not verify status of "%s" before download.' % r)
            
            if r.something_to_commit():
                print "%s: something to commit." % r
            else:
                pass
#                print "%s: all ok." % r
    elif command == 'tag':
        h = []
        for r in resources:
            c = r.config.copy()
            c['revision'] = r.current_revision()
            h.append(c)
        print yaml.dump(h)
    elif command == 'commit':
        for r in resources:
            if r.something_to_commit():
                r.commit()
    else:
        raise Exception('Uknown command "%s".' % command)
        
if __name__ == '__main__':
    main()
       
