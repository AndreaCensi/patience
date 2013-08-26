from patience.action import Action
from patience.structures import ActionException


__all__ = ['Checkout']


class Checkout(Action):
    
    def __init__(self): 
        Action.__init__(self, parallel=False, any_order=False)

    def single_action_starting(self, resource): 
        pass

    def single_action_result_display(self, resource, result): 
        pass
    
    def applicable(self, r):
        return not r.is_downloaded()
    
    def single_action(self, r):
        if r.is_downloaded():
            raise ActionException('Already downloaded %s' % r)

        r.checkout()
    
Action.actions['checkout'] = Checkout()

