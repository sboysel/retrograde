import subprocess
from pathlib import Path
from pystrata.utils import rand_string

# === core
def _git(path, cmd=None, subcmd=[None]):
    """exectue git and subcommand at `path`"""
    if not cmd:
        cmd = ["git", "--no-pager", f"--git-dir={path}/.git", f"--work-tree={path}"]
    cmd.extend(subcmd)
    out = subprocess.check_output(cmd, text=True, encoding="utf-8")
    return out

# === utilities
def _is_dir(path):
    Path(path).exists()

def _is_empty(path):
    any(Path(path).iterdir())

def _is_git_repo(path):
    return Path(path, ".git").exists()

def _remote_url(path, name="origin"):
    """get the URL for the remote `name`"""
    out = _git(path, subcmd=["remote", "get-url", name])
    return out

# === clone
def _is_cloned(url, path):
    is_cloned = False
    if _is_dir(path):
        if _is_empty(path):
            if _is_git_repo(path):
                if _remote_url(path) == url:
                    is_cloned = True
    return is_cloned

def _clone(url, path):
    """clone from `self.url` to `self.path`"""
    if not _is_cloned(url, path):
        try:
            cmd, subcmd = ["git"], ["clone", f"{url}", f"{path}"]
            _git(path, cmd, subcmd)
        except BaseException as e:
            raise e
        
    return True

# === branches
def _current_branch(path):
    """run `git branch --current-branch`. Requires git>=2.22"""
    out = _git(path, subcmd=["branch", "--show-current"]).rstrip()
    return out

def _checkout_branch(path, branch):
    """"""
    _git(path, subcmd=["checkout", branch])
    return branch

def _checkout_new_branch(path, branch):
    """"""
    _git(path, subcmd=["checkout", "-b", branch])
    return branch

def _temp_branch(path):
    """create a temporary branch for pystrata operations"""
    branch = "pystrata" + rand_string(10)
    _checkout_new_branch(path, branch)
    return branch    

def _delete_branch(path, branch):
    """"""
    _git(path, subcmd=['branch', '-D'])
    return True

# === log
def _log_commits(path):
    out = _git(path, subcmd=["log", "--format=%h"])
    return out.splitlines()

def _log_commit_most_recent(path):
    out = _git(path, subcmd=["log", "-1", "--format=%h"])
    return out.rstrip()

# === reset
def _reset_to_commit(path, commit):
    out = _git(path, subcmd=["reset", "--hard", commit])
    return out

def _reset_to_previous_commit(path):
    out = _git(path, subcmd=["reset", "--hard", "HEAD~1"])
    return 

# === rebase
def _rebase_branch(path, branch):
    out = _git(path, subcmd=["rebase", branch])
