import subprocess


def _git(path, cmd=None, subcmd=[None]):
    """exectue git and subcommand at `path`"""
    if not cmd:
        cmd = ["git", "--no-pager", f"--git-dir={path}/.git", f"--work-tree={path}"]
    cmd.extend(subcmd)
    out = subprocess.check_output(cmd, text=True, encoding="utf-8")
    return out

def _clone(url, path):
    """clone from `self.url` to `self.path`"""    
    cmd, subcmd = ["git"], ["clone", f"{url}", f"{path}"]
    try: 
        _git(path, cmd, subcmd)
        return True
    except BaseException as e:
        raise e

def _status(path):
    """run `git status`"""
    out = _git(path, subcmd=["status"])
    return out

def _current_branch(path):
    """run `git branch --current-branch`. Requires git>=2.22"""
    out = _git(path, subcmd=["branch", "--show-current"])
    return out


class Repo:
    """
    """
    def __init__(self, path, url):
        self.path = path
        self.url = url

    def clone(self):
        """clone from `self.remote` to `self.path`"""
        try:
            _clone(self.url, self.path)
            return True
        except BaseException as e:
            raise e
    
    def status(self):
        """run `git status`"""
        return _status(self.path)


    def current_branch(self):
        """run `git branch --current-branch`"""
        return _current_branch(self.path)        
        
