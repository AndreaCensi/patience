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
        url = config['url']
        if 'git' in url:
            config['type'] = 'git'
        elif 'svn' in url:
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
        
from optparse import OptionParser

def main():
    
    parser = OptionParser()
    parser.add_option("--config", help="Location of yaml configuration")
    (options, args) = parser.parse_args() #@UnusedVariable

    if options.config:
        config = options.config
    else:
        config = find_configuration()
        
    resources = list(yaml.load_all(open(config)))
    resources = filter(lambda x: x is not None, resources)
    resources = map(instantiate, resources)
    
    
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
                    ret = res.get(timeout=0.1)
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
            if not r.is_downloaded():
                raise Exception('Could not verify status of "%s" before download.' % r)
            num_modified = r.num_modified()
            num_untracked = r.num_untracked()
            to_push = r.something_to_push()
            to_pull = r.something_to_pull()
            if to_push or to_pull:
               ff = r.can_be_ff()
            else:
               ff = False
            
            flags = [''] * 4
            
            if num_modified or num_untracked:
                fm = '%2dm' % num_modified if num_modified else "   "
                fu = '%2du' % num_untracked if num_untracked else "   "
                
                flags[0] = fm +' '+ fu
                
            if to_pull:
                flags[1] = 'pull'

            if to_push:
                flags[2] = 'push'
            
            if to_push or to_pull:
            
                if ff:
                    flags[3] = 'ok'
                else:
                    flags[3] = 'X'
            
            if not all([f == '' for f in flags]):
                status = ""
                for f in flags:
                    status += '{0:>8}'.format(f)
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
            if r.something_to_push() and r.can_be_ff():
                if not quiet:
                     print 'Fetching for %s' % r

                r.push()

    elif command == 'commit':
        for r in resources:
            if r.something_to_commit():
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
       
