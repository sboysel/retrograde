import subprocess
from utils import rand_string

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

def _checkout_branch(path, branch):
    """"""
    _git(path, subcmd=["checkout", branch])

def _temp_branch(path):
    """create a temporary branch for pystrata operations"""
    branch = "pystrata" + rand_string(10)
    _git(path, subcmd=["checkout", "-b", branch])
    return branch    

def _delete_branch(path, branch):
    """"""
    _git(path, subcmd=['branch', '-D'])
