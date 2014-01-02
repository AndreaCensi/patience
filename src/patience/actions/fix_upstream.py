
from patience.action import Action
from patience.structures import ActionException


__all__ = ['FixUpstream']


class FixUpstream(Action):
    
    def __init__(self):
        Action.__init__(self, parallel=True, any_order=True)

    def single_action_started(self, resource): 
        pass
    
    def single_action_result_display(self, resource, result): 
        pass

    def single_action(self, r):
        branch = r.branch
#         print('will do: %s' % r)
        r.set_upstream(branch, 'origin/%s' % branch)

    def applicable(self, r):
        if not r.branch_exists_local(r.branch):
            return False

        if not r.is_remote_correct():
            return False

        if not r.branch_exists_remote(branch=r.branch):
            print('I dont find remote branch')
            return False

        res = r.get_what_tracks(r.branch)
        expected = 'origin/%s' % r.branch
        if res != expected:
            return True
        else:
            return False


Action.actions['fix-upstream'] = FixUpstream()
            
