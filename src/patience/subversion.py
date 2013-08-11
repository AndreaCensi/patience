from .resources import Resource

__all__ = ['Subversion']

class Subversion(Resource):
    def __init__(self, config):
        Resource.__init__(self, config)
        self.url = config['url']

    def checkout(self):
        system_cmd_fail('.', 'svn checkout %s %s' % (self.url, self.destination))

    def update(self):
        system_cmd_fail(self.destination, 'svn update')

    def something_to_commit(self):
        return "" != system_output('svn status %s' % (self.destination))

    def commit(self):
        system_cmd_fail(self.destination, 'svn commit')

    def current_revision(self):
        out = system_output('svnversion %s' % self.destination)
        out = out.split()[0]
        return out

