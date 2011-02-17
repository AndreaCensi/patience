#!/usr/bin/env python
import sys, subprocess

def cmd2args(s):
    ''' if s is a list, leave it like that; otherwise split()'''
    if isinstance(s, list):
        return s
    else:
        return s.split()
        
def system_cmd(cwd, cmd):
    ''' Do not output; return return value. '''
    val = subprocess.call(cmd2args(cmd), cwd=cwd, stdout=subprocess.PIPE,
     stderr=subprocess.PIPE) 
    return val

def system_cmd_show(cwd, cmd): 
    res = subprocess.call(cmd2args(cmd), cwd=cwd, stdout=sys.stdout, stderr=sys.stderr)
    if res != 0:
        raise Exception('Command %r failed. (ret value: %s)' % (cmd, res))

def system_output(cwd, cmd):
    ''' Gets the output of a command,  raise exception if it failes '''
    p = subprocess.Popen(cmd2args(cmd), stdout=subprocess.PIPE,
     stderr=subprocess.PIPE, cwd=cwd)
    output, stderr = p.communicate()
    p.wait()
    ret = p.returncode 
    if ret != 0:
        raise Exception("Command %r (%s) failed in cwd = %s: got return code: %s\n\n%s" % \
            (cmd.__repr__(), cmd2args(cmd).__repr__(), cwd, ret, stderr))
    return output
        
def system_cmd_fail(cwd, cmd):
    res = system_cmd(cwd, cmd)
    if res != 0:
        raise Exception('Command %r failed. (ret value: %s)' % (cmd, res))

def system_run(cwd, cmd):
    ''' Gets the output of a command,  raise exception if it failes '''
    p = subprocess.Popen(cmd2args(cmd), stdout=subprocess.PIPE,
     stderr=subprocess.PIPE, cwd=cwd)
    output, stderr = p.communicate()
    p.wait()
    ret = p.returncode 
    output = "\n".join(output.split('\n'))
    stderr = "\n".join(stderr.split('\n'))
    return ret, output, stderr
    
    