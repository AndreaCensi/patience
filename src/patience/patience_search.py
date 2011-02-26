#!/usr/bin/env python
import  fnmatch, sys, os
import yaml

from .utils  import system_output
from .logging import error, info, fatal

RESOURCES = 'resources.yaml'

def main():
    if len(sys.argv)== 1:
        dir = '.'
    else:
        dir = sys.argv[1]

    output = os.path.join(dir, RESOURCES)
    if os.path.exists(output):
        raise Exception('Output file %s already exist.' % output)
    
    def format(s):
        return s.ljust(80)[:80]
    
    repolist = []
    def append(r):
        cols = 80
        if 'sub' in r:
            info(format("Found sub in: %s" % repo))
        elif 'dir' in r:
            info(format('Found git in: %s' % repo))
        repolist.append(r)
        
    def consider(repo):
        if RESOURCES in repo:
            append({'sub':  os.path.relpath(repo, dir)})
            
        if '.git' in repo:
            git_dir = repo
            destination = os.path.relpath(os.path.dirname(git_dir), dir)
            found = {'dir': destination}
            info('Found git in: %s' % found['dir'])
                
            try:
                url, branch = get_url_branch(git_dir)
                if branch != 'master':
                    found['branch'] = branch
                found['url'] = url
                if not 'git' in found['url']:
                    found['type'] = 'git'
            except Exception as e:
                error('Could not locate url for %r: %s' % (git_dir, e))
                
            append(found)
    
    
    def mark():
        mark.count += 1
        markers = ['-','/','|','\\']
        return markers[mark.count % len(markers)]
      
    mark.count = 0
    
    def log(s):
        sys.stderr.write(format('%s %5d %s' % (mark(), mark.count, s)))
        sys.stderr.write('\r');
   
    for repo in find_repos(dir, log=log, shallow=True):
        consider(repo)
   
    if len(repolist) == 0:
        fatal('No repos found in %r.' % dir)
 
    with open(output,'w') as f:
        for repo in repolist:
            f.write('---\n')
            yaml.dump(repo, f, default_flow_style=False)
 

def get_url_branch(git_dir):
    repo = os.path.dirname(git_dir)
    repo = os.path.realpath(repo)

    remotes = system_output(repo, 'git remote')
    if not 'origin' in remotes.split():
        raise Exception("No remote origin found for %r." % repo)
            
    try:
        result = system_output(repo, 'git remote show origin')
    except Exception as e:
        raise Exception("Could not get origin URL for %r: %s" % (repo, e))
                
    tokens = result.split()
    # XXX add checks
    url = tokens[tokens.index('URL:') + 1]
    
    result = system_output(repo, 'git branch --color=never')
    for line in result.split('\n'):
        if line[0] == '*':
            branch = line.split()[1]
            break
    else:
        print("Could not parse branch from %s, using master." % 
              result.__repr__())
        branch = 'master'

    return url, branch
    

def find_repos(directory, log= lambda x: None, followlinks=False, shallow= True):
    reasonable = shallow
    resources = os.path.join(directory, RESOURCES)
    if os.path.exists(resources):
        yield resources
        if reasonable: return

    git_repo = os.path.join(directory, '.git')
    if os.path.exists(git_repo):
        yield git_repo
        if reasonable: return
        
    for root, dirs, files in os.walk(directory, followlinks=followlinks):
        log(root)
        
        for dir in list(dirs):
            resources = os.path.join(root, dir, RESOURCES)
            if os.path.exists(resources):
                yield resources
                dirs.remove(dir)
            else:
                git_repo = os.path.join(root, dir, '.git')
                if os.path.exists(git_repo):
                    yield git_repo
                    if reasonable: dirs.remove(dir)
                    
if __name__ == '__main__':
    main()
