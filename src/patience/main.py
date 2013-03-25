import os, yaml

from .subversion import Subversion
from .git import Git
from .resources import Resource

from .logging import error 
from .action import Action
from .actions import *

import datetime
import sys
import platform


class ConfigException(Exception):
    def __init__(self, error, config):
        self.error = error
        self.config = config
        
    def __str__(self):
        return "%s\n%s" % (self.error, self.config)

def instantiate(config, base_dir='.'):

    if not 'url' in config:
        raise ConfigException('Missing key "url".', config)
        
    if not any([x in config for x in ['dir', 'destination']]):
        raise ConfigException('Missing key "dir".',  config)
    
    dir = config.get('dir', config.get('destination'))
    dir = os.path.expandvars(dir)
    dir = os.path.expanduser(dir)
    dir = os.path.join(base_dir, dir)
    dir = os.path.abspath(dir)
    dir = os.path.realpath(dir)
    config['dir'] = dir                 
                                             
    if not 'type' in config:
        url = config['url']
        if 'git' in url:
            config['type'] = 'git'
        elif 'svn' in url:
            # guess git
            config['type'] = 'subversion'
        else:
            raise ConfigException('Could not guess type from url', config)
        
    
    res_type = config['type']
    if res_type == 'subversion':
        return Subversion(config)
    elif res_type == 'git':
        return Git(config)
    elif res_type == 'included':
        return Resource(config)
    else:
        raise ConfigException('Uknown resource type.', config)

def find_configuration(dir=os.path.curdir, name='resources.yaml'):
    while True:
        dir = os.path.realpath(dir)
        config = os.path.join(dir, name)
         
        if os.path.exists(config):
            return config
        
        parent = os.path.dirname(dir)
        if parent == dir: # reached /
            raise Exception('Could not find configuration "%s".' % name)
        
        dir = parent
        
from optparse import OptionParser

def load_resources(filename):
    curdir = os.path.dirname(filename)
    for config in yaml.load_all(open(filename)):
	if config is None: continue
        config['from'] = filename
        sub = config.get('sub', None)
        if sub:
            try:
                for x in load_resources(os.path.join(curdir, sub)):
                    yield x
            except Exception as e:
                error('Could not load %r: %s' % (sub, e))
                raise
        else:
            yield instantiate(config, curdir)

def main():
    
    parser = OptionParser()
    parser.add_option("--config", help="Location of yaml configuration")

    parser.add_option("-s", "--seq", help="Force sequential", default=False,
                    action='store_true')

    parser.add_option("-v", "--verbose", help="Write status messages",  
                    default=False, action='store_true')
                
    parser.add_option("-V", help="Show git operations", 
                     dest='show_operations', 
                    default=False, action='store_true')
    
    parser.add_option("--yaml", help="Write YAML output", default=False,
                    action='store_true')

    (options, args) = parser.parse_args() #@UnusedVariable

    if options.config:
        config = options.config
    else:
        config = find_configuration()
        

        
    resources = list(load_resources(config)) 
    
    if len(args) == 0:
        raise Exception('Please provide command.')
    if len(args) > 1:
        raise Exception('Please provide only one command.')
    command = args[0]
    
    
    quiet = False


    if options.yaml:
        stream = None
    else:
        stream = sys.stdout
        
    if command in Action.actions:
        action = Action.actions[command]
        results = action.go(resources, 
            force_sequential=options.seq, 
            stream=stream, 
            console_status=options.verbose,
            show_operations=options.show_operations)
        
        if options.yaml:
            s = {'date': datetime.datetime.now(),
                 'hostname': platform.node(),
                 'command': command,
                 'config': config,
                 'resources': resources,
                 'results': results}
            #yaml.safe_dump(s, sys.stdout, default_flow_style=False)
            yaml.dump(s, sys.stdout, default_flow_style=False)
        return
        
    if command == 'list':
        repos = [dict(dir=r.destination,url=r.url)  for r in resources]
        yaml.dump(repos, sys.stdout, default_flow_style=False) 
                     
    elif command == 'update':
        for r in resources:
            if not quiet:
                print 'Updating %s' % r

            r.update()

    elif command == 'tag':
        h = []
        for r in resources:
            c = r.config.copy()
            c['revision'] = r.current_revision()
            h.append(c)
        print yaml.dump(h)
         
    elif command == 'commit':
        for r in resources:
            if r.num_modified() > 0 and  r.num_untracked() == 0:
                r.commit()
    else:
        raise Exception('Unknown command "%s".' % command)
        # 
        # def fetch(r):
        #     if r.config['type'] == 'git':
        #         print 'Fetching for %s' % r
        #         res = r.fetch()
        #         if res:  
        #             print "fetched {dir}".format(dir=r)
        

if __name__ == '__main__':
    main()
       
