from patience.action import Action
from patience.structures import ActionException

__all__ = ['MakeBranch']


class MakeBranch(Action):
    """ Makes the required local branch if it does not exist and switches to it. """
    
    def single_action_starting(self, resource): 
        pass

    def single_action_result_display(self, resource, result): 
        pass

    def applicable(self, r):
        return not r.is_right_branch()
        
    def single_action(self, r):
        if r.is_right_branch():
            raise ActionException('Already on branch')
        
        if not r.branch_exists_local():
            r.make_local_branch()
            
        if not r.is_right_branch():
            r.checkout_right_branch() 


    
Action.actions['make-branch'] = MakeBranch()

