from patience.action import Action


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
        s = ""
        from collections import defaultdict
        counter = defaultdict(lambda: 0)
        counter2 = defaultdict(lambda: 0)
        for r, v in results.items():
            if isinstance(v, Exception):
                # XXX: maybe something else
                continue
            
            for b in v.keys():
                counter[b] += 1
                counter2[r] += 1
            
        branches = sorted(counter.keys(), key=lambda x: (-counter[x]))
        resources = sorted(counter2.keys(), key=lambda x: (-counter2[x]))
        
        table = []
        for r in resources:
            v = results[r]
            if isinstance(v, Exception):
                continue
            row = []
            row.append(str(r))
            for b in branches:
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
                            cell += 'M%d' % nmerge
                            if not simple_merge:
                                cell += '!'
                    else: 
                        cell = '='        
                row.append(cell)
            table.append(row)
        
        T = [[''] + branches] + table

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

