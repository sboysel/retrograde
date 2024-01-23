# SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>
#
# SPDX-License-Identifier: MIT
import datetime
import secrets
import string
import subprocess
import time
from pathlib import Path

# === Repo
class Repo:
    """
    """
    def __init__(self, path: str, url: str):
        self.path = path
        self.url = url

    def _git(self, subcmd: list) -> str:
        """run an arbitrary git subcommand on the repo located at `self.path`"""
        out = _git(self.path, subcmd=subcmd)
        return out

    def _clone(self) -> bool:
        """clone from `self.url` to `self.path`"""
        return _clone(self.url, self.path)

    def _current_branch(self) -> str:
        """run `git branch --current-branch`"""
        branch = _git(self.path, subcmd=["branch", "--show-current"]).rstrip()
        return branch

    def _checkout_branch(self, branch: str) -> str:
        """run `git checkout [branch]`"""
        _ = _git(self.path, subcmd=["checkout", "--quiet", branch])
        return branch
    
    def _temp_branch(self) -> str:
        """run `git checkout -b [branch]`"""
        branch = "retrograde" + _rand_string(10)
        _ = _git(self.path, subcmd=["checkout", "--quiet", "-b", branch])
        return branch

    def _log(self, formats=("%h", "%at")) -> list:
        """return the git log as a list of tuples. each tuple is an element from
           the tuple `formats`. The default is `formats = ('%h', '%at')`. See 
           https://git-scm.com/docs/pretty-formats"""
        if isinstance(formats, tuple):
            formats = ",".join(formats)
            out = _git(self.path, subcmd=["log", f"--format={formats}"])
            out = [tuple(x.split(",")) for x in out.splitlines()]
        else:
            out = _git(self.path, subcmd=["log", f"--format={formats}"])
            out = out.splitlines()        
        return out
    
    def _reset(self, commit) -> str:
        """hard reset to commit"""
        out = _git(self.path, subcmd=["reset", "--hard", commit])
        return out
    
    def _reset(self, commit):
        out = _git(self.path, subcmd=["reset", "--hard", commit])
        return out
    
    def _rebase(self, branch):
        """rebase current branch from `branch`"""
        out = _git(self.path, subcmd=["rebase", "--quiet", branch])
        return out
        

# === core git binding
def _git(path, cmd=None, subcmd=[None]) -> str:
    """exectue git and subcommand at `path`"""
    if not cmd:
        cmd = ["git", "--no-pager", f"--git-dir={path}/.git", f"--work-tree={path}"]
    cmd.extend(subcmd)
    out = subprocess.check_output(cmd, text=True, encoding="utf-8")
    return out

# === clone
def _is_cloned(url: str, path: str):
    """
    Check if the path is a local clone of the repo.  Will return True if `path` is a
    git repository and the URL for origin remote matches `url`.
    """
    is_cloned = False
    if _is_git_repo(path):
        if _remote_url(path) == url:
            is_cloned = True
    return is_cloned

def _clone(url: str, path: str) -> bool:
    """clone from `self.url` to `self.path`"""
    if not _is_cloned(url, path):
        try:
            cmd, subcmd = ["git"], ["clone", f"{url}", f"{path}"]
            _git(path, cmd, subcmd)
        except BaseException as e:
            raise e
    return True

# === utilities
def _is_git_repo(path: str) -> str:
    return Path(path, ".git").exists()

def _remote_url(path: string, name="origin") -> str:
    """get the URL for the remote `name`"""
    out = _git(path, subcmd=["remote", "get-url", name])
    return out.rstrip()

def _rand_string(n: int) -> str:
    """generate random alphanumeric string of length n"""
    choice_set = string.ascii_uppercase + string.ascii_lowercase + string.digits    
    res = ''.join(secrets.choice(choice_set) for i in range(n))
    return str(res)

def _datetime2unix(date_time: datetime.datetime) -> int:
    """convert datetime to UNIX timestamp"""
    return int(time.mktime(date_time.timetuple()))

def _unix2datetime(unix_time: int) -> datetime.datetime:
    """convert UNIX timestamp to datetime"""
    return datetime.datetime.fromtimestamp(unix_time)
