from collections import namedtuple
   
        
status_fields = ('present num_modified num_untracked to_push simple_push '
                'to_merge simple_merge branch current_branch branch_mismatch').split()
StatusResult = namedtuple('StatusResult', status_fields)

__all__ = ['StatusResult', 'status_fields', 'status2string']

def status2string(r, res):
    flags = [''] * 4
    sizes = [10, 18, 18, 10]
    
    flag_modified = 0
    flag_merge = 1
    flag_push = 2
    flag_branch = 3
    
    if not res.present:
        flags[flag_modified] = 'missing'
    else:    
        if res.num_modified or res.num_untracked:
            fm = '%3dm' % res.num_modified if res.num_modified else "    "
            if res.num_modified > 99:
                fm = '>99u'
            fu = '%3du' % res.num_untracked if res.num_untracked else "    "
            if res.num_untracked > 99:
                fu = '>99u'
        
            flags[flag_modified] = fm + ' ' + fu
        
        if res.branch_mismatch:
            flags[flag_branch] = '!branch'
        else:                
            if res.to_merge:
                flags[flag_merge] = 'merge (%d)' % res.to_merge
                if not res.simple_merge:
                    flags[flag_merge] += ' (!)'
                else:
                    flags[flag_merge] += '    '            
    
            if res.to_push:
                flags[flag_push] = 'push (%d)' % res.to_push
                if not res.simple_push:
                    flags[flag_push] += ' (!)'
                else:
                    flags[flag_push] += '    '
                         
            
    if not all([f == '' for f in flags]):
        status = ""
        for i, f in enumerate(flags):
            fm = "{0:<%d}" % sizes[i]
            status += fm.format(f)
        status += " {0}".format(r)
        return status
    else:
        return None
