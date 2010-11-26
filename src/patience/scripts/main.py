#!/usr/bin/env python
import yaml, os, re, sys
import subprocess 

from patience.subversion import *
from patience.git import *

        # 
        # def expand_environment(s):
        #     while True:
        #         m = re.match('(.*)\$\{(\w+)\}(.*)', s)
        #         if not m:
        #             return s
        #         before = m.group(1)
        #         var = m.group(2)
        #         after = m.group(3)
        #         if not var in os.environ:
        #             raise ValueError('Could not find environment variable "%s".' % var)
        #         sub = os.environ[var]
        #         s = before + sub + after


def instantiate(config):
    if not all([x in config for x in ['url', 'destination']]):
        raise Exception('Incomplete config: %s' % config)
    
    if not 'type' in config:
        if 'git' in config['url']:
            config['type'] = 'git'
        elif 'svn' in config['url']:
            # guess git
            config['type'] = 'subversion'
        else:
            raise Exception('Could not guess type from url "%s".' % url)
        
    
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
            to_commit = r.something_to_commit()
            to_push = r.something_to_push()
#           to_pull = r.something_to_pull()
            
            if to_commit or to_push:
                s1 = "commit" if to_commit else ""
                s2 = "push" if to_push else ""
                
                print "{s1:>8} {s2:>8}  {dir}".format(s1=s1,s2=s2,dir=r)
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
       