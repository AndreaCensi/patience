#!/usr/bin/env python

from rfc822 import parsedate
from time import mktime
from datetime import datetime
from os import popen
from sys import argv,stderr,stdout
from collections import namedtuple
import sys, os
import yaml
FileCommit = namedtuple('FileCommit', 'date filename adds dels')
def read_commits(repo):
    date = None
    for x in popen('git --git-dir %r log --numstat' % repo):
        if x.startswith('Date'):
            date=datetime(*parsedate(x[5:])[:7])
            # t=mktime(parsedate(x[5:]))

        tokens = x.split()
        if len(tokens) == 3 and x[0].isdigit():
            # print('Found: %r' % tokens)
            adds = int(tokens[0])
            dels = int(tokens[1])
            filename = tokens[2]
            yield FileCommit(date=date, filename=filename,adds=adds,dels=dels)
        
        
if __name__ == '__main__':
    if len(argv) >= 3:
        suffix = argv[2]
    else:
        suffix = None
    repo = os.path.join(argv[1], '.git')

        
    for x in read_commits(repo):
        if suffix and not x.filename.endswith(suffix): continue
        # print(x)
        y = {'adds': x.adds, 'date': x.date, 'dels': x.dels, 'filename': x.filename}
        yaml.dump([y], sys.stdout)
        
        