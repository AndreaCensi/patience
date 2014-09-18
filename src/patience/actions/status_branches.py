from patience.action import Action
from patience.utils.coloredterm import termcolor_colored


__all__ = ['StatusBranches']


class StatusBranches(Action):
    """ Lists the differences with all remote branches """
    
    def __init__(self): 
        Action.__init__(self, parallel=True, any_order=False)

    def single_action_starting(self, resource):  # @UnusedVariable
        return None

    def result_display_start(self):
        return ""

    def single_action_result_display(self, resource, result):  # @UnusedVariable
        return None

    def single_action(self, r):
        return r.list_differences_with_remote_branches()
        
    def summary(self, resources, results):  # @UnusedVariable
        
        only_show_ahead = False
        only_show_ahead = True
        s = ""
        from collections import defaultdict
        counter = defaultdict(lambda: 0)
        counter2 = defaultdict(lambda: 0)
        for r, v in results.items():
            if isinstance(v, Exception):
                s += '%s: %s\n' % (r, v)
                # XXX: maybe something else
                continue
            for b in v.keys():
                counter[b] += 1
                counter2[r] += 1
            
        branches_sorter = lambda x: (-counter[x])
        branches = sorted(counter.keys(), key=branches_sorter)
        resources = sorted(counter2.keys(), key=lambda x: (-counter2[x]))
        
        # only show branches that have some interesting change
        branches_ahead = set()
        branches_behind = set()

        for r in resources:
            v = results[r]
            if isinstance(v, Exception):
                continue
            for b in branches:
                if not b in v: continue
                npush, simple_push, nmerge, simple_merge = v[b]
                if npush:
                    branches_behind.add(b)
                if nmerge:
                    branches_ahead.add(b)

#         print('Branches behind: %s' % branches_behind)
#         print('Branches ahead: %s' % branches_ahead)
#         branches_rest = set(branches) - branches_ahead - branches_behind
#         print('Rest: %s' % branches_rest)
        
        if only_show_ahead:
            print('Showing only branches ahead.')
            branches_to_show = sorted(branches_ahead, key=branches_sorter)
        else:
            branches_to_show = branches

        table = []
        for r in resources:
            v = results[r]
            if isinstance(v, Exception):
                continue
            row = []
            row.append(str(r))
            for b in branches_to_show:
                if not b in v:
                    cell = ''
                else:
                    npush, simple_push, nmerge, simple_merge = v[b]
                    if npush or nmerge:
                        cell = ''
                        if npush:
                            cell += 'P%d' % npush
                            if not simple_push:
                                cell += '!'
                        if nmerge:
                            if npush:
                                cell += ' '
                            
                            cell_m = 'M%d' % nmerge
                            cell_m = termcolor_colored(cell_m, color='magenta')
                            
                            cell += cell_m 
                            if not simple_merge:
                                cell += '!'
                    else: 
                        cell = '='        
                row.append(cell)
            table.append(row)
        
        T = [[''] + branches_to_show] + table

        s += format_table(T)
        return s
        
def format_table(T, between='  '):
    s = ""
    nrows = len(T)
    ncols = len(T[0])
    column_sizes = [max([len(T[row][col]) for row in range(nrows)]) 
                    for col in range(ncols)] 
    
    for row in T:
        for cell, colsize in zip(row, column_sizes):
            c = cell.ljust(colsize)
            s += c + between
        s += '\n'
    
    return s


Action.actions['branches'] = StatusBranches()

