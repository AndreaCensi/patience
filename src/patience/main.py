#!/usr/bin/env python 
import os, yaml

from .subversion import Subversion
from .git import Git
from .resources import Resource

from .logging import error, info, fatal


class ConfigException(Exception):
    def __init__(self, error, config):
        self.error = error
        self.config = config
        
    def __str__(self):
        return "%s\n%s" % (self.error, self.config)

def instantiate(config, base_dir='.'):

    if not all([x in config for x in ['url', 'destination']]):
        raise ConfigException('Incomplete config.',  config)
    
    config['destination'] = os.path.expanduser(os.path.expandvars(config['destination']))
    config['destination'] = os.path.normpath(os.path.join(base_dir, config['destination']))
    
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
    for config in yaml.load_all(open(filename)):
        config['from'] = filename
        sub = config.get('sub', None)
        if sub:
            try:
                for x in load_resources(sub):
                    yield x
            except Exception as e:
                error('Could not load %r: %s' % (sub, e))
        else:
            yield instantiate(config, os.path.dirname(filename))

def main():
    
    parser = OptionParser()
    parser.add_option("--config", help="Location of yaml configuration",
                default='resources.yaml')
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


    if command == 'checkout':
        for r in resources:
            if not r.is_downloaded():
                print 'Downloading %s...' % r
                r.checkout()
            else:
                print 'Already downloaded %s.' % r 
                
    elif command == 'merge':
        for r in resources:
            if r.something_to_merge() and r.simple_merge():
                r.merge()
                
    elif command == 'fetch':
        for r in resources:
        
            if r.config['type'] == 'git':
                if not quiet:
                    print 'Fetching for %s' % r
                res = r.fetch()
                if res:  
                    print "fetched {dir}".format(dir=r)
                
    elif command == 'pfetch':

        from multiprocessing import Pool, TimeoutError
        pool = Pool(processes=10)            
        
        results = {}
        for r in resources:
            results[r] = pool.apply_async(fetch, [r])

        while results:
            print "Still %s to go" % len(results)
            for r, res in list(results.items()):
                try:
                    res.get(timeout=0.1)
                    del results[r]
                except TimeoutError:
                    continue
                except Exception as e:
                    print "%s: Could not fetch: %s" % (r, e)
                    del results[r]
            
        print "done" 
                     
    elif command == 'update':
        for r in resources:
            if not quiet:
                print 'Updating %s' % r

            r.update()

    elif command == 'install':
        for r in resources:
            r.install()

    elif command == 'status':
        for r in resources:

            flags = [''] * 3
            sizes = [10, 13, 13]

            if not r.is_downloaded():
                flags[2] = 'missing'
                # raise Exception('Could not verify status of "%s" before download.' % r)
            else:
                num_modified = r.num_modified()
                num_untracked = r.num_untracked()
                to_push = r.something_to_push()
                to_merge = r.something_to_merge()

            
                if num_modified or num_untracked:
                    fm = '%3dm' % num_modified if num_modified else "    "
                    if num_modified > 99:
                        fm = '>99u'
                    fu = '%3du' % num_untracked if num_untracked else "    "
                    if num_untracked > 99:
                        fu = '>99u'
                
                    flags[0] = fm + ' ' + fu
                
                if to_merge:
                    flags[1] = 'merge (%d)' % to_merge
                    if not r.simple_merge():
                        flags[1] += ' (!)'
                    else:
                        flags[1] += '    '            

                if to_push:
                    flags[2] = 'push (%d)' % to_push
                    if not r.simple_push():
                        flags[2] += ' (!)'
                    else:
                        flags[2] += '    '         
            
                if not all([f == '' for f in flags]):
                    status = ""
                    for i, f in enumerate(flags):
                        fm = "{0:<%d}" % sizes[i]
                        status += fm.format(f)
                    status += " {0}".format(r)

                    print status
            
    elif command == 'tag':
        h = []
        for r in resources:
            c = r.config.copy()
            c['revision'] = r.current_revision()
            h.append(c)
        print yaml.dump(h)
        
    elif command == 'push':
        for r in resources:
            if r.something_to_push() and r.simple_push():
                if not quiet:
                    print 'Pushing for %s' % r

                r.push()

    elif command == 'commit':
        for r in resources:
            if r.num_modified() > 0 and  r.num_untracked() == 0:
                r.commit()
    else:
        raise Exception('Unknown command "%s".' % command)
        
def fetch(r):
    if r.config['type'] == 'git':
        print 'Fetching for %s' % r
        res = r.fetch()
        if res:  
            print "fetched {dir}".format(dir=r)


if __name__ == '__main__':
    main()
       
