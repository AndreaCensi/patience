import sys

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def fatal(s):
    error(s)
    sys.exit(-1)
    
error = info
