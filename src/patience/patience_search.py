#!/usr/bin/env python
import  fnmatch, sys, os
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

    repos = list(find_repos(dir, verbose=False))
    if not repos:
        fatal('No repos found in %r.' % dir)
        
    f = open(output, 'w')
    for repo in repos:
        if RESOURCES in repo:
            info("Found sub in: %s" % repo)
            f.write('---\n')
            f.write('sub: %s\n' % os.path.relpath(repo, dir))
        if '.git' in repo:
            git_dir = repo
            destination = os.path.relpath(os.path.dirname(git_dir), dir)
            f.write('---\n')
            f.write('destination: %s\n' % destination)
            f.write('type: git\n')

            try:
                url, branch = get_url_branch(git_dir)
                f.write('branch: %s\n' % branch)
                f.write('url: %s\n' % url)
            except Exception as e:
                error('Could not locate url for %r: %s' % (git_dir, e))
                
    f.close()


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
    


def find_files(directory, pattern, verbose=False, followlinks=False):
    for root, dirs, files in os.walk(directory, followlinks=followlinks):
        if verbose:
            print root
            
        for basename in files + dirs:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def find_repos(directory, verbose=False, followlinks=False):
    git_repo = os.path.join(directory, '.git')
    if os.path.exists(git_repo):
            yield git_repo
        
    for root, dirs, files in os.walk(directory, followlinks=followlinks):
        if verbose:
            print root
        
        for dir in list(dirs):
            resources = os.path.join(root, dir, RESOURCES)
            if os.path.exists(resources):
                yield resources
                dirs.remove(dir)
            else:
                git_repo = os.path.join(root, dir, '.git')
                if os.path.exists(git_repo):
                    yield git_repo
                
if __name__ == '__main__':
    main()
