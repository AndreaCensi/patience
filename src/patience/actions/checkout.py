from patience.action import Action

__all__ = ['Checkout']


class Checkout(Action):
    
    def __init__(self): 
        Action.__init__(self, parallel=False, any_order=False)

    def single_action_starting(self, resource): 
        pass

    def single_action_result_display(self, resource, result): 
        pass
    
    def single_action(self, r):
        if not r.is_downloaded():
            r.checkout()
    
Action.actions['checkout'] = Checkout()

