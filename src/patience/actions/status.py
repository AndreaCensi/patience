from patience.action import Action
from patience.status_string import status2string, StatusResult, status_fields


__all__ = ['Status', 'StatusFull']


class Status(Action):
    
    def __init__(self): 
        Action.__init__(self, parallel=True, any_order=False)

    def single_action_starting(self, resource):  # @UnusedVariable
        return None

    def single_action_result_display(self, resource, result):
        if not isinstance(result, Exception):
            return status2string(resource, result)
    
    def single_action(self, r):
        
        branch = r.branch

        if not r.is_downloaded():
            present = False
            num_modified = None
            num_untracked = None
            to_push = None
            to_merge = None
            simple_merge = None
            simple_push = None
            current_branch = None
            branch_mismatch = None
        else:
            current_branch = r.current_branch()
            branch_mismatch = branch != current_branch
            
            present = True
            num_modified = r.num_modified()
            num_untracked = r.num_untracked()
            
            if branch == current_branch:
                
                to_push = r.something_to_push()
                to_merge = r.something_to_merge()
                if to_merge: 
                    simple_merge = r.simple_merge()
                else: 
                    simple_merge = None
                if to_push: 
                    simple_push = r.simple_push()
                else: 
                    simple_push = None
            else:
                to_push = None
                to_merge = None
                simple_merge = None
                simple_push = None
                
                
        asdict = dict([(k, locals()[k]) for k in status_fields])
        return StatusResult(**asdict)

    def summary(self, resources, results):
        pass

Action.actions['status'] = Status()



class StatusFull(Status):
    

    def single_action_result_display(self, resource, result):
        if not isinstance(result, Exception):
            return status2string(resource, result)
        else:
            return str(result)  # XXX


Action.actions['status-full'] = StatusFull()

