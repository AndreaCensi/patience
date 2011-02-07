import sys

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def fatal(s):
    error('Some fatal error: %s' % s)
    sys.exit(-1)
    
error = info
