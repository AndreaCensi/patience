#!/usr/bin/env python
import yaml, os, re, sys
import subprocess

def system_cmd(cwd, cmd):
    val = subprocess.call(cmd.split(), cwd=cwd,  stdout=subprocess.PIPE,
     stderr=subprocess.PIPE)
    if val != 0:
        pass
        # print "%s: %s : %s" % (val, cwd, cmd)
    return val
    
def system_cmd_fail(cwd, cmd):
    res = system_cmd(cwd,cmd)
    if res != 0:
        raise Exception('Command "%s" failed. (ret value: %s)' % (cmd, res))

def system_cmd_show(cwd, cmd):
    res = subprocess.call(cmd.split(), cwd=cwd, stdout=sys.stdout, stderr=sys.stderr)
    if res != 0:
        raise Exception('Command "%s" failed. (ret value: %s)' % (cmd, res))


def system_output(cwd, cmd):
    ''' Gets the output of a command,  raise exception if it failes '''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
     stderr=subprocess.PIPE, cwd=cwd, shell=True)
    output, stderr = p.communicate()
    p.wait()
    ret = p.returncode 
    if ret != 0:
        raise Exception("Got return code: %s\n\n%s" %  (ret, stderr))
    return output