from . import actions  # @UnusedImport
from .action import Action
from .git import Git
from .resources import Resource
from .subversion import Subversion
from optparse import OptionParser
from patience import logger
import datetime
import os
import platform
import sys
import yaml
from .visualization import error



class ConfigException(Exception):
    def __init__(self, error, config):
        self.error = error
        self.config = config
        
    def __str__(self):
        return "%s\n%s" % (self.error, self.config)

def instantiate(config, base_dir='.'):
    """ 
        config['url']
        config['dir']
        config['type'] = git, subversion
    
    """
    
    if not 'url' in config:
        raise ConfigException('Missing key "url".', config)
        
    if not any([x in config for x in ['dir', 'destination']]):
        raise ConfigException('Missing key "dirname".', config)
    
    dirname0 = config.get('dir', config.get('destination'))
    dirname = os.path.expandvars(dirname0)
    dirname = os.path.expanduser(dirname)
    dirname = os.path.join(base_dir, dirname)
    dirname = os.path.abspath(dirname)
    dirname = os.path.realpath(dirname)
    config['dir'] = dirname                 
                                   
#     if not os.path.exists(dirname):
#         print('warn: %r does not exist (%s from %s)' % (dirname, dirname0, base_dir))
#     else:
#         print('found %r %r' % (dirname, config))
                    
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
    
def instance_rosinstall_entry(entry, base_dir):
    if 'git' in entry:
        # print entry
        url = entry['git']['uri']
        dest = entry['git']['local-name']
        dest = os.path.join(base_dir, dest)
        branch = entry['git'].get('version', 'master')
        return Git(dict(dir=dest, url=url, branch=branch))
    elif 'tar' in entry:
        # print('skipping tar entry %r' % entry)
        return None
    else:
        msg = 'Cannot interpret entry %r' % entry
        raise Exception(msg)

def find_configuration_in_dir(dirname, names=['resources.yaml', '.rosinstall']):
    for name in names:
        config = os.path.join(dirname, name)
     
        if os.path.exists(config):
            yield config

    
def find_configuration(dirname=os.path.curdir):
    while True:
        dirname = os.path.realpath(dirname)
        
        files = list(find_configuration_in_dir(dirname))
        
        for f in files:
            yield f
            
        if files:
            return
        
        parent = os.path.dirname(dirname)
        
        if parent == dirname:  # reached /
            raise Exception('Could not find configuration files.')
        
        dirname = parent
        

def load_resources(filename):
    basename = os.path.basename(filename)
    if 'resources.yaml' in basename:
        # print('loading %r' % filename)
        for x in load_resources_patience(filename):
            yield x
        return
    
    if '.rosinstall' in basename:
        for x in load_resources_rosinstall(filename):
            yield x
        return
    
    msg = 'Strange basename %r' % basename
    assert False, msg
    
def load_resources_rosinstall(filename):
    entries = list(yaml.load_all(open(filename)))[0]
    for entry in entries:
        i = instance_rosinstall_entry(entry, os.path.dirname(filename))
        if i is not None:
            yield i
    
def load_resources_patience(filename):
    curdir = os.path.dirname(filename)
    
    contents = list(yaml.load_all(open(filename)))
    if isinstance(contents[0], list):
        contents = contents[0]
        
    for config in contents:
        if config is None:
            continue
        config['from'] = filename
        sub = config.get('sub', None)
        if sub:
            f = os.path.join(curdir, sub)
            
            if not os.path.exists(f):
                msg = ('Could not load sub %s.' % f)
                logger.error(msg)
                raise Exception(msg)
            
            if os.path.isdir(f):
                files = find_configuration_in_dir(f)
            else:
                files = [f]
                
            try:
                for ff in files:
                    for x in load_resources(ff):
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

    (options, args) = parser.parse_args()  # @UnusedVariable

    if options.config:
        configs = [options.config]
    else:
        configs = list(find_configuration())
        
    resources = []
    for c in configs:
        resources.extend(load_resources(c)) 
    
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
        
        force_sequential = options.seq
        if command in ['status'] and options.yaml:
            force_sequential = True
            
        results = action.go(resources,
            force_sequential=force_sequential,
            stream=stream,
            console_status=options.verbose,
            show_operations=options.show_operations)
        
        if options.yaml:
            s = {'date': datetime.datetime.now(),
                 'hostname': platform.node(),
                 'command': command,
                 'config': configs,
                 'resources': resources,
                 'results': results}
            # yaml.safe_dump(s, sys.stdout, default_flow_style=False)
            yaml.dump(s, sys.stdout, default_flow_style=False)
        return
        
    if command == 'list':
        repos = [dict(dir=r.destination, url=r.url)  for r in resources]
        yaml.dump(repos, sys.stdout, default_flow_style=False) 
                     
    elif command == 'update':
        for r in resources:
            if not quiet:
                print('Updating %s' % r)

            r.update()

    elif command == 'tag':
        h = []
        for r in resources:
            c = r.config.copy()
            c['revision'] = r.current_revision()
            h.append(c)
        print(yaml.dump(h))
         
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
       
