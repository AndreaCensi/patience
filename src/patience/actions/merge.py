from patience.action import Action
from patience.structures import ActionException

__all__ = ['Merge']



class Merge(Action):
    
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
        
        if r.something_to_merge() and r.simple_merge():
            r.merge()
                
Action.actions['merge'] = Merge()
