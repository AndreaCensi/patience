import sys
from collections import namedtuple

from .structures import ActionException

def slave(task):
    action, resource = task
    return action.single_action(resource)
    
    
def write_message(stream, r, m):
    if not m: return
    name = '%s' % r
    if name in m:
        stream.write('%s\n' % m)
    else:
        stream.write('%s: %s\n' % (name, m))
    
class Action(object):
    actions = {}
    
    def __init__(self, parallel=True, any_order=False):
        self.parallel = parallel
        self.any_order = any_order
        
    def go(self, resources, force_sequential=False, max_processes=3,stream=sys.stderr):
        if not self.parallel or force_sequential:
            self.go_sequential(resources, stream)
        else:
            self.go_parallel(resources, stream, 
                    any_order=self.any_order,
                    max_processes=max_processes)
    
    def go_sequential(self, resources, stream):
        results = {}
        for r in resources:
            # m = self.single_action_started(r)
            # write_message(stream, r, m)

            try:
                results[r] = self.single_action(r)
            except ActionException as e:
                results[r] = e

            m2 = self.single_action_result_display(r, results[r])
            write_message(stream, r, m2)

        m3 = self.summary(resources, results)

        if m3:
            stream.write('%s\n' % m3)

    def go_parallel(self, resources, stream, any_order, max_processes):

        from multiprocessing import Pool, TimeoutError
        pool = Pool(processes=20)            
        
        handles = {}
        for r in resources:
            handles[r] = pool.apply_async(slave, [(self, r)])

        results = {}
        r2messages = {}
        to_write = list(resources)
        while handles:
            while to_write and to_write[0] in r2messages:
                r = to_write.pop(0)
                m = r2messages[r]
                del r2messages[r]
                write_message(stream, r, m)
                
            sys.stderr.write("%3d to go (%3d to write)      \r" % 
                (len(handles), len(r2messages)))
            for r, res in list(handles.items()):
                try:
                    results[r] = res.get(timeout=0.05)
                except TimeoutError:
                    continue
                except ActionException as e:
                    results[r] = e
            
                del handles[r]
                    
                m2 = self.single_action_result_display(r, results[r])
                if any_order:
                    write_message(stream, r, m2)
                else:
                    r2messages[r] = m2

        m3 = self.summary(resources, results)
        if m3:
            stream.write('%s\n' % m3)


    def summary(self, resources, results):
        s = ''
        for r in resources:
            if isinstance(results[r], Exception):
                e = str(results[r]).split('\n')[0]
                s += '{0:<30}: {1}\n'.format(r, e)
        return s
        
    
    # def single_action_started(self, resource): pass
    # def single_action_result_display(self, resource, result): pass
    

        
class Fetch(Action):
    
    def __init__(self):
        Action.__init__(self, parallel=True, any_order=True)

    def single_action_result_display(self, resource, result):
        if isinstance(result, Exception):
            return "%s" % result
        else:
            if result:
                return "fetched: %s" % result
            else:
                return None
            
    def single_action(self, r):
        if r.config['type'] == 'git':
            return r.fetch()
        raise ActionException("Not implemented for %r" % r.config['type'])

Action.actions['fetch'] = Fetch()

        
class Merge(Action):
    
    def __init__(self):
        Action.__init__(self, parallel=True, any_order=True)

    def single_action_started(self, resource): pass
    def single_action_result_display(self, resource, result): pass

    def single_action(self, r):
        if r.something_to_merge() and r.simple_merge():
            r.merge()
                
Action.actions['merge'] = Merge()

class Push(Action):
    
    def __init__(self):
        Action.__init__(self, parallel=True, any_order=True)

    def single_action_started(self, resource): pass
    def single_action_result_display(self, resource, result): pass

    def single_action(self, r):
        if r.something_to_push() and r.simple_push():
            r.push()

                
Action.actions['push'] = Push()
            
        
        
status_fields = ('present num_modified num_untracked to_push simple_push '
                'to_merge simple_merge').split()
StatusResult = namedtuple('StatusResult',status_fields)


def status2string(r, res):
    flags = [''] * 3
    sizes = [10, 18, 18]
    
    if not res.present:
        flags[0] = missing
    else:    
        if res.num_modified or res.num_untracked:
            fm = '%3dm' % res.num_modified if res.num_modified else "    "
            if res.num_modified > 99:
                fm = '>99u'
            fu = '%3du' % res.num_untracked if res.num_untracked else "    "
            if res.num_untracked > 99:
                fu = '>99u'
        
            flags[0] = fm + ' ' + fu
        
        if res.to_merge:
            flags[1] = 'merge (%d)' % res.to_merge
            if not res.simple_merge:
                flags[1] += ' (!)'
            else:
                flags[1] += '    '            

        if res.to_push:
            flags[2] = 'push (%d)' % res.to_push
            if not res.simple_push:
                flags[2] += ' (!)'
            else:
                flags[2] += '    '         
            
    if not all([f == '' for f in flags]):
        status = ""
        for i, f in enumerate(flags):
            fm = "{0:<%d}" % sizes[i]
            status += fm.format(f)
        status += " {0}".format(r)
        return status
    else:
        return None

class Status(Action):
    
    def __init__(self):
        # Action.__init__(self, parallel=True, any_order=True)
        Action.__init__(self, parallel=True, any_order=False)

    def single_action_starting(self, resource):
        return None

    def single_action_result_display(self, resource, result):
        if not isinstance(result, Exception):
            return status2string(resource ,result)
    
    def single_action(self, r):
        
        if not r.is_downloaded():
            present = False
            num_modified = None
            num_untracked = None
            to_push = None
            to_merge = None
            simple_merge = None
            simple_push = None
        else:
            present = True
            num_modified = r.num_modified()
            num_untracked = r.num_untracked()
            to_push = r.something_to_push()
            to_merge = r.something_to_merge()
            if to_merge: 
                simple_merge = r.simple_merge()
            else: simple_merge = None
            if to_push: 
                simple_push = r.simple_push()
            else: simple_push = None


                
        asdict =dict([(k, locals()[k]) for k in status_fields])
        return StatusResult(**asdict)

    def summary(self, resources, results):
        pass

Action.actions['status'] = Status()



    