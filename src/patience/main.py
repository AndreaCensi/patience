import datetime
import platform
import sys
from contracts import contract
from .structures import UserError


def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--config", help="Location of yaml configuration")

    parser.add_option("-s", "--seq", help="Force sequential", default=False,
                      action='store_true')

    parser.add_option("-v", "--verbose", help="Write status messages",
                      default=False, action='store_true')
                
    parser.add_option("-V", help="Show git operations",
                      dest='show_operations',
                      default=False, action='store_true')
    
    parser.add_option("-O", help="Show stdout/stderr of operations",
                      dest='show_stdout',
                      default=False, action='store_true')
        
    parser.add_option("--yaml", help="Write YAML output", default=False,
                    action='store_true')

    (options, args) = parser.parse_args()  # @UnusedVariable

    from .configuration import find_configuration, load_resources

    if options.config:
        configs = [options.config]
    else:    
        configs = list(find_configuration())
        
    resources = []
    errors = []
    found = {}
    for c in configs:
        for r in load_resources(c, errors):
            if r.destination in found:
                continue
            else:
                found[r.destination] = r 
                resources.append(r) 
    
    for e in errors:
        print('error: %s' % e)
        
    from .action import Action
    
    if len(args) == 0:
        msg = 'Please provide command: %s' % (Action.actions.keys()) 
        raise UserError(msg)
    
    selectors = args[1:]
    
    if resources and selectors:
        resources = filter_resources(resources=resources, selectors=selectors)
        if not resources:
            msg = ('warning, selectors %s did not select anything' % selectors)
            raise UserError(msg)
    
#     
#     if len(args) > 1:
#         raise Exception('Please provide only one command.')
#     
    command = args[0]
    
    quiet = False


    if options.yaml:
        stream = None
    else:
        stream = sys.stdout
        
    
    if command in Action.actions:
        action = Action.actions[command]
        
        force_sequential = options.seq
        if command in ['status'] and options.yaml:
            force_sequential = True
            
        results = action.go(resources,
            force_sequential=force_sequential,
            stream=stream,
            console_status=options.verbose,
            show_operations=options.show_operations,
            show_stdout=options.show_stdout)
        
        if options.yaml:
            import yaml
            s = {'date': datetime.datetime.now(),
                 'hostname': platform.node(),
                 'command': command,
                 'config': configs,
                 'resources': resources,
                 'results': results}
            # yaml.safe_dump(s, sys.stdout, default_flow_style=False)
            yaml.dump(s, sys.stdout, default_flow_style=False)
        return
        
    if command == 'list':
        repos = [dict(dir=r.destination, url=r.url)  for r in resources]
        yaml.dump(repos, sys.stdout, default_flow_style=False) 
                     
    elif command == 'update':
        for r in resources:
            if not quiet:
                print('Updating %s' % r)

            r.update()

    elif command == 'tag':
        h = []
        for r in resources:
            c = r.config.copy()
            c['revision'] = r.current_revision()
            h.append(c)
        print(yaml.dump(h))
         
    elif command == 'commit':
        for r in resources:
            if r.num_modified() > 0 and  r.num_untracked() == 0:
                r.commit()
    else:
        commands = ", ".join(Action.actions.keys())
        msg = 'Unknown command %r. Use one of: %s' % (command, commands)
        raise UserError(msg)
        # 
        # def fetch(r):
        #     if r.config['type'] == 'git':
        #         print 'Fetching for %s' % r
        #         res = r.fetch()
        #         if res:  
        #             print "fetched {dir}".format(dir=r)
    

@contract(resources='list', selectors='list(str)', returns='list')    
def filter_resources(resources, selectors):
    """ Selects the resources in the list which match the selectors """
    def match(resource, selector):
        if selector in str(resource):
            return True
        if selector in resource.destination:
            return True
        # print('no %s %s %s' % (resource.destination, resource, selector))
        return False
        
    res = []
    for r in resources:
        for s in selectors:
            if match(r, s):
                res.append(r)
                break
    
    return res
    
    
if __name__ == '__main__':
    main()
       
