#!/usr/bin/env python
import yaml, os, re, sys
import subprocess

def system_cmd(cmd):
    val = os.system(cmd)
    if val != 0:
        print "%s: %s" % (val, cmd)
    return val
    
def system_cmd_fail(cmd):
    print cmd
    res = os.system(cmd)
    if res != 0:
        raise Exception('Command "%s" failed. (ret value: %s)' %(cmd, res))

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

    def install(self):
        pass
        
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
            system_cmd_fail('cd %s && python setup.py develop' % self.destination)
        elif install_type == 'cmake':
            system_cmd_fail('cd %s && cmake -DCMAKE_INSTALL_PREFIX=${BVENV_PREFIX} .' % self.destination)
            system_cmd_fail('cd %s && make' % self.destination)
            
            system_cmd_fail('cd %s && make install' % self.destination)
            
            
        else:
            raise Exception('Uknown install type "%s".' % install_type)
        
class Subversion(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']
        
    def checkout(self):
        system_cmd_fail('svn checkout %s %s' % (self.url, self.destination))

    def update(self):
        system_cmd_fail('svn update %s' % (self.destination))

    def something_to_commit(self):
        return "" != system_output('svn status %s' % (self.destination))

    def commit(self):
        system_cmd_fail('svn commit %s' % (self.destination))
        
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
        system_cmd_fail('git clone %s %s' % (self.url, self.destination))

    def update(self):
    # XXX: branch :
        # system_cmd_fail('cd %s && git pull origin ' % (self.destination))
        system_cmd_fail('cd %s && git pull origin master' % (self.destination))
        
    def something_to_commit(self):
        return 0 != system_cmd('cd %s && git diff --quiet --exit-code origin/%s' % (self.destination, self.branch))
        
    def commit(self):
        system_cmd_fail('cd %s && git commit -a' % (self.destination))
        system_cmd_fail('cd %s && git push' % (self.destination))
        
    def current_revision(self):
        out = system_output('cd %s && git rev-parse HEAD' % self.destination)    
        out = out.split()[0]
        return out
    
def expand_environment(s):
    while True:
        m =  re.match('(.*)\$\{(\w+)\}(.*)', s)
        if not m:
            return s
        before = m.group(1)
        var = m.group(2)
        after = m.group(3)
        if not var in os.environ:
            raise ValueError('Could not find environment variable "%s".' % var)
        sub = os.environ[var]
        s = before+sub+after
        #print 'Expanded to %s' % s
#            
#def expand(r):
#    ''' Expand environment variables found. '''
#    for k in r.keys():
#        r[k] = expand_environment(r[k])
#    return r

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

def main():
    config = 'resources.yaml'
    resources = list(yaml.load_all(open(config)))
    resources = filter( lambda x: x is not None, resources)
#    resources = map(expand, resources)
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
        
if __name__=='__main__':
    main()
       
