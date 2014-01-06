from collections import namedtuple
   
        
status_fields = ('present num_modified num_untracked to_push simple_push '
                'to_merge simple_merge branch current_branch branch_mismatch '
                'local_branch_exists remote_branch_exists url current_url track '
                'is_git_repo has_remote').split()
StatusResult = namedtuple('StatusResult', status_fields)

__all__ = ['StatusResult', 'status_fields', 'status2string']

sizes = [2, 14, 8, 8, 4, 4, 4, 4]
flag_modified = 1
flag_merge = 2
flag_push = 3
flag_branch = 4
flag_branch_remote = 5
flag_branch_local = 6
flag_track = 7


def status2string(r, res):
    
    flags = [''] * len(sizes)
    
    
    remarks = []
    
    if not res.present:
        flags[flag_modified] = '!'
        remarks.append('Dir does not exists')
    elif not res.is_git_repo:
        flags[flag_modified] = '!'
        remarks.append('Dir exists but no git repo found.'
                       ' (Fix with "git init".)')
    elif not res.has_remote:
        flags[flag_branch_remote] = '!'
        remarks.append('No remote configured.'
                       ' (Fix with "git remote add origin %s".)' % r.url)
    else:    
        if res.num_modified or res.num_untracked:
            fm = '%3dm' % res.num_modified if res.num_modified else "    "
            if res.num_modified > 99:
                fm = '>99u'
            fu = '%3du' % res.num_untracked if res.num_untracked else "    "
            if res.num_untracked > 99:
                fu = '>99u'
        
            flags[flag_modified] = fm + ' ' + fu
        
        if (res.current_url is not None) and (res.url != res.current_url):
            remarks.append('Wrong remote url: %s' % res.current_url)
            remarks.append('(expected %s)' % res.url)

        # print('%s < %s' % (res.branch, res.track))
        if res.track == None:
            if res.remote_branch_exists:
                remarks.append('No upstream configured.'
                               ' (Should be fixable by "pat fix-upstream".)')
            else:
                remarks.append('No upstream configured and no remote branch.')
            flags[flag_branch_remote] = '!R'

        if  res.local_branch_exists == False:
            flags[flag_branch_local] = 'no local %s' % res.branch
            flags[flag_branch_local] = '!L'
            
            remarks.append('Local branch %r does not exist.' % res.branch +
                           ' (Should be fixable by "pat make-branch".)')
        
        if  res.remote_branch_exists == False:
            flags[flag_branch_remote] = 'no remote %s' % res.branch
            flags[flag_branch_remote] = '!R' 
            
            remarks.append('Remote branch %r does not exist.' % res.branch +
                           ' (Should be fixable by "pat push".)')

        
        if res.branch_mismatch == True:
            # flags[flag_branch] = 'on %s instead of %s' % (res.current_branch, res.branch)
            flags[flag_branch] = '~B'
            
            remarks.append('On branch %r rather than %r.' % (res.current_branch, res.branch)
                           + ' (Correct using "git checkout %s".)' % res.branch)
        else:                
            if res.to_merge > 0:
                flags[flag_merge] = 'M %d' % res.to_merge
                if res.simple_merge == False:
                    flags[flag_merge] += '!'
                    remarks.append('There might be conflicts when merging.')
                else:
                    pass
                    # flags[flag_merge] += '    '            
    
            if res.to_push > 0:
                flags[flag_push] = 'P %d' % res.to_push
                if res.simple_push == False:
                    flags[flag_push] += '!'
                    remarks.append('There might be conflicts when pushing.')
                else:
                    pass
                    # flags[flag_push] += '    '
                         
            
    if not all([f == '' for f in flags]) or remarks:
        status = ""
        for i, f in enumerate(flags):
            fm = "{0:<%d}" % sizes[i]
            status += fm.format(f)
        status += " {0}".format(r)
        if remarks:
            lleft = sum(sizes)  # + (len(sizes) - 1)
            prefix = ' ' * lleft 
            for r in remarks:
                status += '\n' + prefix + '  - %s' % r
                
        return status
    else:
        return None
