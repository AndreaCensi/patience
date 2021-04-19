import os
import sys

from system_cmd.meat import system_cmd_result
import yaml

from . import logger
from .configuration import find_configuration, load_resources

RESOURCES = "resources.yaml"


def main():
    if len(sys.argv) == 1:
        dirname = "."
    else:
        dirname = sys.argv[1]

    # check to see if there is already a resources.yaml
    fn = os.path.join(dirname, RESOURCES)
    found = {}
    if os.path.exists(fn):
        logger.info("Loading known repos from %r" % fn)

        for r in load_resources(fn):
            d = os.path.realpath(r.destination)
            found[d] = r

    output = os.path.join(dirname, RESOURCES)
    if os.path.exists(output):
        logger.warning("Output file %s already exist." % output)
        output = output + ".search_output"
        logger.warning("Using %s instead." % output)

    cols = 80

    def format_string(s):
        return s.ljust(cols)[:cols]

    repolist = []
    repodirs = set()

    def append(r):
        if "sub" in r:
            logger.info(format_string("Found sub in: %s" % repo))
        elif "dir" in r:
            d = os.path.realpath(r["dir"])
            if d in repodirs:
                return
            else:
                repodirs.add(d)
            logger.info(format_string("Found git in: %s" % repo))
        repolist.append(r)

    def consider(repo):
        if RESOURCES in repo:
            append({"sub": os.path.relpath(repo, dirname)})

        if ".git" in repo:
            git_dir = repo
            destination = os.path.relpath(os.path.dirname(git_dir), dirname)
            found = {"dir": destination}
            logger.info("Found git in: %s" % found["dir"])

            try:
                url, branch = get_url_branch(git_dir)
                if branch != "master":
                    found["branch"] = branch
                found["url"] = url
                if not "git" in found["url"]:
                    found["type"] = "git"
            except Exception as e:
                logger.error("Could not locate url for %r: %s" % (git_dir, e))

            append(found)

    def mark():
        mark.count += 1
        markers = ["-", "/", "|", "\\"]
        return markers[mark.count % len(markers)]

    mark.count = 0

    def log(s):
        sys.stderr.write(format_string("%s %5d %s" % (mark(), mark.count, s)))
        sys.stderr.write("\r")

    shallow = False
    for repo in find_repos(dirname, log=log, shallow=shallow):
        consider(repo)

    if len(repolist) == 0:
        logger.fatal("No repos found in %r." % dirname)

    with open(output, "w") as f:
        for repo in repolist:
            if "dir" in repo:
                d = os.path.realpath(repo["dir"])
                if d in found:
                    logger.info("Ignoring repo %s, already known." % d)
                    ok = False
                else:
                    ok = True
            else:
                ok = True
            if ok:
                f.write("---\n")
                yaml.dump(repo, f, default_flow_style=False)


def get_url_branch(git_dir):
    repo = os.path.dirname(git_dir)
    repo = os.path.realpath(repo)

    def system_output(cwd, cmd):
        return system_cmd_result(cwd, cmd).stdout

    remotes = system_output(repo, "git remote")
    if not "origin" in remotes.split():
        raise Exception("No remote origin found for %r." % repo)

    try:
        result = system_output(repo, "git remote show origin")
    except Exception as e:
        raise Exception("Could not get origin URL for %r: %s" % (repo, e))

    tokens = result.split()
    # XXX add checks
    url = tokens[tokens.index("URL:") + 1]

    result = system_output(repo, "git branch --color=never")
    for line in result.split("\n"):
        if line[0] == "*":
            branch = line.split()[1]
            break
    else:
        print("Could not parse branch from %s, using master." % result.__repr__())
        branch = "master"

    return url, branch


def find_repos(directory, log=lambda _: None, followlinks=False, shallow=True):
    reasonable = shallow
    resources = os.path.join(directory, RESOURCES)
    if os.path.exists(resources):
        yield resources
        if reasonable:
            return

    git_repo = os.path.join(directory, ".git")
    if os.path.exists(git_repo):
        yield git_repo
        if reasonable:
            return

    for root, dirs, _ in os.walk(directory, followlinks=followlinks):
        log(root)

        for dirname in list(dirs):
            resources = os.path.join(root, dirname, RESOURCES)
            if os.path.exists(resources):
                yield resources
                dirs.remove(dirname)
            else:
                git_repo = os.path.join(root, dirname, ".git")
                if os.path.exists(git_repo):
                    yield git_repo
                    if reasonable:
                        dirs.remove(dirname)


if __name__ == "__main__":
    main()
