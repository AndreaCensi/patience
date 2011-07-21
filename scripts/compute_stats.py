import yaml, sys

blacklist = ['adskalman', 'flydra', 'drosophila_eye_map']


def main():
    repos = list(yaml.load_all(sys.stdin))[0]
    for r in repos:
        r['name'] = filter_url(r['url'])
    repos = [r for r in repos if r['name'] not in blacklist]
    name2repo = {}
    for r in repos:
        if not r['name'] in name2repo:
            name2repo[r['name']] = r

#    out = []
    # for name in sorted(name2repo.keys()):
        #print('%-20s %s' % (name, name2repo[name]['dir']))
        
    dirs =  [r['dir'] for r in name2repo.values()]
    yaml.dump(dirs, sys.stdout, default_flow_style=False)
    
def filter_url(url):

    remove = [
        # 'ssh://git@ac.repositoryhosting.com/ac/',
        # 'ssh://git@andreacensi.repositoryhosting.com/ac/',
        '.git',
        # 'git@github.com:',
        # 'git://github.com/'
    ]
    for r in remove:
        url = url.replace(r,'')
    return url.split('/')[-1]
if __name__ == '__main__':
    main()