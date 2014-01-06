from patience.action import Action
from patience.status_string import status2string, StatusResult, status_fields
from patience.structures import ActionException


__all__ = ['Status', 'StatusFull']


class Status(Action):
    
    def __init__(self): 
        Action.__init__(self, parallel=True, any_order=False)

    def single_action_starting(self, resource):  # @UnusedVariable
        return None

    def result_display_start(self):
        return """  unknown_       __merges    
modified  |     |    pushes     _branch status
    |     |     |       |      |
"""

    def single_action_result_display(self, resource, result):
        if not isinstance(result, Exception):
            return status2string(resource, result)
    
    def single_action(self, r):
        branch = r.branch
        url = r.url

        current_url = None
        num_modified = None
        num_untracked = None
        to_push = None
        to_merge = None
        simple_merge = None
        simple_push = None
        current_branch = None
        branch_mismatch = None
        local_branch_exists = None
        remote_branch_exists = None
        is_git_repo = None
        track = None
        has_remote = None

        if not r.is_downloaded():
            present = False
        elif not r.is_git_repo():
            present = True
            is_git_repo = False
        else:
            is_git_repo = True
            present = True
            
            if not r.has_remote():
                has_remote = False
            else:
                has_remote = True
                current_url = r.get_remote_url()

            track = r.get_what_tracks(branch)  # XXX
                
            if current_url != url:
                pass
            else:
                remote_branch_exists = r.branch_exists_remote()
               
                current_branch = r.current_branch()
                branch_mismatch = branch != current_branch
                local_branch_exists = r.branch_exists_local()
                
                if branch == current_branch:
                    track = r.get_what_tracks(branch)
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
                    track = r.get_what_tracks(branch)  # XXX

            num_modified = r.num_modified()
            num_untracked = r.num_untracked()
            
        asdict = dict([(k, locals()[k]) for k in status_fields])
        return StatusResult(**asdict)
#
#     def summary(self, resources, results):
#         for resource, result in zip(resources, results):
#             if isinstance(result, ActionException):
#                 print(result)


Action.actions['status'] = Status()


class StatusFull(Status):
    

    def single_action_result_display(self, resource, result):
        if not isinstance(result, Exception):
            return status2string(resource, result)
        else:

            return 'Error: ' + str(result)  # XXX


Action.actions['status-full'] = StatusFull()

