from patience.action import Action
from patience.structures import ActionException

__all__ = ['Fetch']

        
class Fetch(Action):
    
    def __init__(self):
        Action.__init__(self, parallel=True, any_order=True)

    def single_action_result_display(self, resource, result):  # @UnusedVariable
        if isinstance(result, Exception):
            return "%s" % result
        else:
            if result:
                return "fetched: %s" % result
            else:
                return None
            
    def single_action(self, r):
        if not r.is_downloaded():
            raise ActionException('Not downloaded %s' % r)

#         if isinstance(r, Git):
        return r.fetch()
        
#         raise ActionException("Not implemented for %r" % r.config['type'])

Action.actions['fetch'] = Fetch()

        