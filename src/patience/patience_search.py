#!/usr/bin/env python
import glob, sys, os, fnmatch
from utils import *

def main():
    dirs = sys.argv[1:]
    if not dirs:
        dirs = ['.']

    output = 'resources.yaml'
    if os.path.exists(output):
        raise Exception('Output file %s already exist.' % output)

    f = open(output, 'w')

    def repos():
        for dir in dirs:
            for f in find_files(dir, '.git'):
                yield f
                
    for repo in repos():
        git_dir = repo
        repo = os.path.dirname(git_dir)
        repo = os.path.realpath(repo)

        print "Found repository in: %s" % repo

        # val = system_cmd(repo, 'git ls-remote')
        # if  val != 0:
        #     print "No remote origin found for %s; skipping."  % repo
        #     continue
        remotes = system_output(repo, 'git remote')
        if not 'origin' in remotes.split():
            print "No remote origin found for %s; skipping."  % repo
            continue
                
        try:
            result = system_output(repo, 'git remote show origin')
        except Exception as e:
            print "Could not get origin URL for %s; skipping."  % repo
            continue
            
        tokens = result.split()
        # XXX add checks
        url = tokens[tokens.index('URL:') + 1]
        
        print "     url: %s" % url
        
        result = system_output(repo, 'git branch --color=never')
        for line in result.split('\n'):
            if line[0] == '*':
                branch = line.split()[1]
                break
        else:
            print("Could not parse branch from %s, using master." %
                  result.__repr__())
            branch = master
                
        
        branch = 'master'

        print "  branch: %s" % branch

        f.write('---\n')
        f.write('destination: %s\n' % repo)
        f.write('branch: %s\n' % branch)
        f.write('url: %s\n' % url)
    
    f.close()

def find_files(directory, pattern, verbose=False):
    for root, dirs, files in os.walk(directory):
        if verbose:
            print root
            
        for basename in files + dirs:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename
                
if __name__ == '__main__':
    main()