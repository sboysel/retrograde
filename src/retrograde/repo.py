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
    def __init__(self, path, url):
        self.path = path
        self.url = url

    def _git(self, subcmd):
        """run an arbitrary git subcommand on the repo located at `self.path`"""
        out = _git(self.path, subcmd=subcmd)
        return out

    def _clone(self):
        """clone from `self.url` to `self.path`"""
        return _clone(self.url, self.path)

    def _current_branch(self):
        """run `git branch --current-branch`"""
        branch = _git(self.path, subcmd=["branch", "--show-current"]).rstrip()
        return branch

    def _checkout_branch(self, branch):
        """run `git checkout [branch]`"""
        _ = _git(self.path, subcmd=["checkout", "--quiet", branch])
        return branch
    
    def _temp_branch(self):
        """run `git checkout -b [branch]`"""
        branch = "retrograde" + _rand_string(10)
        _ = _git(self.path, subcmd=["checkout", "--quiet", "-b", branch])
        return branch

    def _commits(self):
        """return list of commits hashes"""
        out = _git(self.path, subcmd=["log", "--format=%h"])
        return out.splitlines()
    
    def _commits_with_timestamps(self):
        """return list of (commits hashes, timestamp) tuples"""
        out = _git(self.path, subcmd=["log", "--format=%h,%at"])
        return [tuple(x.split(",")) for x in out.splitlines()]
    
    def _reset(self, commit):
        out = _git(self.path, subcmd=["reset", "--hard", commit])
        return out
    
    def _rebase(self, branch):
        out = _git(self.path, subcmd=["rebase", "--quiet", branch])
        return out
        

# === core git binding
def _git(path, cmd=None, subcmd=[None]):
    """exectue git and subcommand at `path`"""
    if not cmd:
        cmd = ["git", "--no-pager", f"--git-dir={path}/.git", f"--work-tree={path}"]
    cmd.extend(subcmd)
    out = subprocess.check_output(cmd, text=True, encoding="utf-8")
    return out

# === clone
def _is_cloned(url, path):
    is_cloned = False
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

# === utilities
def _is_git_repo(path):
    return Path(path, ".git").exists()

def _remote_url(path, name="origin"):
    """get the URL for the remote `name`"""
    out = _git(path, subcmd=["remote", "get-url", name])
    return out.rstrip()

def _rand_string(n):
    """generate random alphanumeric string of length n"""
    choice_set = string.ascii_uppercase + string.ascii_lowercase + string.digits    
    res = ''.join(secrets.choice(choice_set) for i in range(n))
    return str(res)

def _datetime2unix(date_time):
    """convert datetime to UNIX timestamp"""
    return time.mktime(date_time.timetuple())

def _unix2datetime(unix_time):
    """convert UNIX timestamp to datetime"""
    return datetime.datetime.fromtimestamp(unix_time)
