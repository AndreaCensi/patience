from .git import Git
from .resources import Resource
from .structures import ConfigException
from .subversion import Subversion
import os
import yaml


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
    
def instance_rosinstall_entry(entry, base_dir, errors=[]):
    if 'git' in entry:
        # print entry
        url = entry['git']['uri']
        dest = entry['git']['local-name']
        dest = os.path.join(base_dir, dest)
        branch = entry['git'].get('version', 'master')
        return Git(dict(dir=dest, url=url, branch=branch))
    elif 'tar' in entry:
        msg = 'skipping tar entry %r' % entry
        errors.append(Exception(msg)) 
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
        

def load_resources(filename, errors=[]):
    basename = os.path.basename(filename)
    if 'resources.yaml' in basename:
        # print('loading %r' % filename)
        for x in load_resources_patience(filename, errors):
            yield x
        return
    
    if '.rosinstall' in basename:
        for x in load_resources_rosinstall(filename, errors):
            yield x
        return
    
    msg = 'Strange basename %r' % basename
    assert False, msg
    
def load_resources_rosinstall(filename, errors=[]):
    entries = list(yaml.load_all(open(filename)))[0]
    for entry in entries:
        i = instance_rosinstall_entry(entry, os.path.dirname(filename),
                                      errors=errors)
        if i is not None:
            yield i
    
def load_resources_patience(filename, errors=[]):
    curdir = os.path.dirname(filename)
    
    contents = list(yaml.load_all(open(filename)))
    if not contents:
        print('warning: empty file %s' % filename)
        return
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
                errors.append(Exception(msg))
                continue
            
            if os.path.isdir(f):
                files = find_configuration_in_dir(f)
            else:
                files = [f]
                
            try:
                for ff in files:
                    for x in load_resources(ff, errors):
                        yield x
                
            except Exception as e:
                msg = ('Could not load %r: %s' % (sub, e))
                errors.append(Exception(msg))
            
        else:
            yield instantiate(config, curdir)
