from rfc822 import parsedate
from time import mktime
from datetime import datetime
from os import popen
from sys import argv,stderr,stdout
from collections import namedtuple
import sys, os
import yaml, time
import yaml, sys
from collections import namedtuple, defaultdict

def datetime2timestamp(d, other=None):
    return time.mktime(d.timetuple())

def seconds2days(s):
    return s / (24 * 60 * 60)


class Stats(object):
    def __init__(self, name):
        self.now = time.time()
        self.count = defaultdict(lambda:0)
        
    def count_commit(self, commit):
        age = seconds2days(self.now - datetime2timestamp(commit.date))
        age = int(age)
        self.count[age] += commit.adds # + commit.dels
    
def main():
    groups = {'code': ['.py'],
            'write': ['.lyx']}
            
    group_stats = {}
    for group in groups:
        group_stats[group] = Stats(group)
        
    
    for r in yaml.load(sys.stdin):
        for commit in read_commits(r + '/.git'):
            ext=  os.path.splitext(commit.filename)[1]
            for group, extensions in groups.items():
                if ext in extensions: 
                    group_stats[group].count_commit(commit)
                    
    out = {}
    for group, stats in group_stats.items():
        out[group] = dict(**stats.count)
    yaml.dump(out, sys.stdout, default_flow_style=False)
        
                        
FileCommit = namedtuple('FileCommit', 'date filename adds dels')
def read_commits(repo):
    date = None
    for x in popen('git --git-dir %r  log --since "1 month ago" --numstat' % repo):
        if x.startswith('Date'):
            date=datetime(*parsedate(x[5:])[:7])
            # t=mktime(parsedate(x[5:]))

        tokens = x.split()
        if len(tokens) == 3 and x[0].isdigit():
            # print('Found: %r' % tokens)
            adds = int(tokens[0])
            dels = int(tokens[1])
            filename = tokens[2]
            yield FileCommit(date=date, filename=filename,
                             adds=adds,dels=dels)
        
if __name__ == '__main__':
    main()
    
    
        