

# import sys
# import subprocess
# 
# def cmd2args(s):
#     ''' if s is a list, leave it like that; otherwise split()'''
#     if isinstance(s, list):
#         return s
#     elif isinstance(s, str):
#         return s.split() 
#     else: 
#         assert False
# 
# 
# class CmdResult(object):
#     def __init__(self, cwd, cmd, ret, stdout, stderr):
#         self.cwd = cwd
#         self.cmd = cmd
#         self.ret = ret
#         self.stdout = stdout
#         self.stderr = stderr
#         
#     def format(self):
#         return result_format(self.cwd, self.cmd, self.ret, self.stdout, self.stderr)
#     
#     
# class CmdException(Exception):
#     def __init__(self, cmd_result):
#         Exception.__init__(self, cmd_result.format())
#         self.res = cmd_result
#         
# def system_cmd_result(
#     cwd, cmd,
#     display_stdout=False,
#     display_stderr=False,
#     raise_on_error=False,
#     display_prefix=None):
#     
#     ''' Returns a tuple CmdResult; raises CmdException. '''
#     if display_prefix is None:
#         display_prefix = '%s %s' % (cwd, cmd)
#     
#     p = subprocess.Popen(
#             cmd2args(cmd),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             cwd=cwd)
#     
#     if 1:  # XXX?
#         stdout, stderr = p.communicate()
#         
#         stdout = stdout.strip()
#         stderr = stderr.strip()
#         
#         prefix = display_prefix + 'err> '
#         if display_stderr and stderr:
#             print(indent(stderr, prefix))
#             
#         prefix = display_prefix + 'out> '
#         if display_stdout and stdout:
#             print(indent(stdout, prefix))
#     
#         p.wait()
#     else:
#         # p.stdin.close()
#         stderr = ''
#         stdout = ''
#         stderr_lines = []
#         stdout_lines = []
#         stderr_to_read = True
#         stdout_to_read = True
#         
#         def read_stream(stream, lines):
#             if stream:
#                 nexti = stream.readline()
#                 if not nexti:
#                     stream.close()
#                     return False
#                 lines.append(nexti)
#                 return True
#             else:
#                 stream.close()
#                 return False
#                 
#         # XXX: read all the lines
#         while stderr_to_read or stdout_to_read:
#             
#             if stderr_to_read:
#                 stderr_to_read = read_stream(p.stderr, stderr_lines)
# #             stdout_to_read = False
#         
#             if stdout_to_read:
#                 stdout_to_read = read_stream(p.stdout, stdout_lines)
#             
#             while stderr_lines:
#                 l = stderr_lines.pop(0)
#                 stderr += l
#                 if display_stderr:
#                     sys.stderr.write('%s ! %s' % (display_prefix, l))
#                     
#             while stdout_lines:
#                 l = stdout_lines.pop(0)
#                 stdout += l
#                 if display_stdout:
#                     sys.stderr.write('%s   %s' % (display_prefix, l))
#                 
#         stdout = p.stdout.read()
#         p.wait()
#             
#     ret = p.returncode 
#     
#     res = CmdResult(cwd, cmd, ret, stdout, stderr)
#     
#     if raise_on_error:
#         if res.ret != 0:
#             raise CmdException(res)
#     
#     return res
#         
# 
# def system_cmd_show(cwd, cmd): 
#     ''' Display command, raise exception. '''
#     system_cmd_result(
#             cwd, cmd,
#             display_stdout=True,
#             display_stderr=True,
#             raise_on_error=True)
#         
# def system_cmd(cwd, cmd):
#     ''' Do not output; return value. '''
#     res = system_cmd_result(
#             cwd, cmd,
#             display_stdout=False,
#             display_stderr=False,
#             raise_on_error=False)
#     return res.ret
# 
# def system_run(cwd, cmd):
#     ''' Gets the output of a command,  raise exception if it failes '''
#     res = system_cmd_result(
#             cwd, cmd,
#             display_stdout=False,
#             display_stderr=False,
#             raise_on_error=True)
#     return res.stdout
# 
# # todo: remove these
# system_cmd_fail = system_run
# system_output = system_run
#     
# def wrap(header, s, N=30):
#     header = '  ' + header + '  '
#     l1 = '-' * N + header + '-' * N
#     l2 = '-' * N + '-' * len(header) + '-' * N
#     return  l1 + '\n' + s + '\n' + l2
# 
# def result_format(cwd, cmd, ret, stdout=None, stderr=None):
#     msg = ('Command:\n\t{cmd}\n'
#            'in directory:\n\t{cwd}\nfailed with error {ret}').format(
#             cwd=cwd, cmd=cmd, ret=ret
#            )
#     if stdout is not None:
#         msg += '\n' + wrap('stdout', stdout)
#     if stderr is not None:
#         msg += '\n' + wrap('stderr', stderr)
#     return msg
#     
# 
# def indent(s, prefix):
#     lines = s.split('\n')
#     lines = ['%s%s' % (prefix, line.rstrip()) for line in lines]
#     return '\n'.join(lines)
