from patience.action import Action


class Install(Action):
    
    def __init__(self): 
        Action.__init__(self, parallel=False, any_order=False)

    def single_action_starting(self, resource): pass

    def single_action_result_display(self, resource, result): pass
    
    def single_action(self, r):
        if r.is_downloaded():
            r.install()
        else:
            raise ActionException('Resource %s not ready.' % r)
    
Action.actions['install'] = Install()
