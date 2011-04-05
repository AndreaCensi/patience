import os
from .utils import system_cmd_fail

def replace_variables(path, rules):
    for k, v in rules:
        if path.startswith(v):
            # print("  applied %s => %s" % (v, k))
            path = path.replace(v, k)
    return path

def get_friendly(path, use_environment=True): # TODO: make switch
    original = path
    options = []
    
    options.append(os.path.relpath(path, os.getcwd()))

    home = os.path.expanduser('~')
    
    rules = []
    rules.append( ('~', os.path.expanduser('~')) ) 
    
    if use_environment:
        envs = dict(os.environ)
        # remove unwanted 
        for e in list(envs.keys()):
            if 'PWD' in e:
                del envs[e]
    
        for k, v in envs.items():
            if v:
                rules.append(('$%s'%k, v))
        
    
        
    # apply longest first
    rules.sort(key=lambda x: -len(x[1]))
    path = replace_variables(path, rules)
    
    options.append(path)

    weight_doubledot = 5
    def score(s):
        # penalize '..' a lot
        s = s.replace('..','*' * weight_doubledot)
        return len(s)
        
    options.sort(key=score)
    
    if False:
        print('Options for %s' % original)
        for o in options:
            print( '- %4d %s' % (score(o), o))
        
    result = options[0]
    
    # print('Converted %s  => %s' % (original, result))

    return result

class Resource: 
    def __init__(self, config):
        self.config = config
        self.destination = config['dir']
        self.short_path = config.get('nick', get_friendly(self.destination))
        
        if os.path.exists(os.path.join(self.destination, 'setup.py')):
            self.config['install'] = 'setuptools'

    def is_downloaded(self):
        return os.path.exists(self.destination)
    
    def __str__(self):
        return self.short_path
    
    def __repr__(self):
        return 'Resource(%r)' % self.destination
    
    def checkout(self):    
        pass

    def update(self):
        pass
        
    def current_revision(self):
        return None

    def something_to_commit(self):
        return False

    def commit(self):
        pass

    def install(self):
    

        install_type = self.config.get('install', None)
        if install_type is None:
            self.badconf("No setup method known.")

        if install_type == 'setuptools':
            self.run('python setup.py develop')
        elif install_type == 'cmake':
            # XXX: qui come va?
            system_cmd_fail(self.destination, 'cmake -DCMAKE_INSTALL_PREFIX=${BVENV_PREFIX} .')
        elif install_type == 'make':
            self.run('make')
            # XXX:
            system_cmd_fail(self.destination, 'make install')
        
        else:
            raise ActionException('Unknown install type %r.' % install_type)
            
            
