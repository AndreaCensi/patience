from patience.action import Action
from patience.structures import ActionException


__all__ = ['Push']


class Push(Action):
    
    def __init__(self):
        Action.__init__(self, parallel=True, any_order=True)

    def single_action_started(self, resource): 
        pass
    
    def single_action_result_display(self, resource, result): 
        pass

    def single_action(self, r):
        if not r.is_downloaded():
            raise ActionException('Not downloaded %s' % r)

        # TODO: add branch check
        if r.something_to_push() and r.simple_push():
            r.push()

    def applicable(self, r):
        return r.is_right_branch()
                
Action.actions['push'] = Push()
            
