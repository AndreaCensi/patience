from .structures import ActionException
import sys
from abc import ABCMeta, abstractmethod


__all__ = ['Action']

# from contracts import ContractsMeta


class Action(object):
    
    __metaclass__ = ABCMeta

    def single_action_started(self, resource): 
        pass
    
    def result_display_start(self):
        return None
    
    @abstractmethod
    def single_action_result_display(self, resource, result): 
        pass

    @abstractmethod
    def single_action(self, r):
        pass
    
    def applicable(self, r):  # @UnusedVariable
        """ Return True if it is applicable to this resource. """
        return True
    
    actions = {}
    
    def __init__(self, parallel=True, any_order=False):
        self.parallel = parallel
        self.any_order = any_order
        
    def filter_applicable(self, resources):
        """ Returns the resoruces for which this action is applicable. """
        return filter(self.applicable, resources)
        
    def go(self, resources, force_sequential=False,
                 max_processes=3, stream=sys.stdout,
                 console_status=False,
                 show_operations=False,
                 show_stdout=False):
        
        s = self.result_display_start()
        if s is not None:            
            if stream:
                stream.write(s)
  
        resources = self.filter_applicable(resources)
         
        for r in resources:
            r.show_operations = show_operations
            r.show_stdout = show_stdout 
            
        if not self.parallel or force_sequential:
            return self._go_sequential(resources, stream,
                     console_status=console_status)
        else:
            return self._go_parallel(resources, stream,
                    any_order=self.any_order,
                    max_processes=max_processes,
                    console_status=console_status)
    
    def _go_sequential(self, resources, stream, console_status):
        results = {}
        for i, r in enumerate(resources): 

            if console_status:
                write_console_status("%3d/%d %s" % (i + 1, len(resources), r))

            try:
                result = self.single_action(r)
            except ActionException as e:
                result = e

            if stream:
                m2 = self.single_action_result_display(r, result)
                write_message(stream, r, m2)

            results[r.short_path] = result
            
        if stream:
            m3 = self.summary(resources, results)
            if m3: 
                stream.write('%s\n' % m3)
    
        return results
    

    def _go_parallel(self, resources, stream, any_order, max_processes,
        console_status):

        from multiprocessing import Pool, TimeoutError
        pool = Pool(processes=max_processes)            
        
        handles = {}
        for r in resources: 
            handles[r] = pool.apply_async(slave, [(self, r)])

        results = {}
        r2messages = {}
        to_write = list(resources)
        while handles:
            # print("handles: %d" % len(handles))
            # print(" to write: %d" % len(to_write))
            # print(" r2message: %d" % len(r2messages))
            # print(" results:  %d" % len(results))
            if console_status:
                sys.stderr.write("%3d to go (%3d to write %d)      \r" % 
                (len(handles), len(r2messages), len(to_write)))
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

            while to_write and to_write[0] in r2messages:
                which = to_write[0]
                r = to_write.pop(to_write.index(which))
                m = r2messages[r]
                del r2messages[r]
                write_message(stream, r, m)
                
        if stream:
            m3 = self.summary(resources, results)
            if m3:
                stream.write('%s\n' % m3)

    def summary(self, resources, results):  # @UnusedVariable
        s = ''
        for path, res in results.items():
            if isinstance(res, Exception):
                e = str(res).split('\n')[0]
                s += '{0:<30}: {1}\n'.format(path, e)
        return s
        
# Load actions 
from . import actions  # @UnusedImport

    


def slave(task):
    action, resource = task
    return action.single_action(resource)
    
    
def write_message(stream, r, m):
    if not m: 
        return
    name = '%s' % r
    if name in m:
        stream.write('%s\n' % m)
    else:
        stream.write('%s: %s\n' % (name, m))
        
def write_console_status(s):
    s = s.ljust(100)  # TODO: add correct lengt
    sys.stderr.write(s + '\r')
    