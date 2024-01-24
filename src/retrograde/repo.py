# SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>
#
# SPDX-License-Identifier: MIT
import datetime
import secrets
import string
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


# === Repo
class Repo:
    """
    Repo

    path: str
    url:  str

    demo usage:
    ```
    class MyRepo(Repo):
        def measure(self):
            ...
    
    repo = Repo(path, url)
    c = [ ... ]
    with retrograde(repo) as r:
        for c in commits:
            r.reset(commit)
            r.measure()
    ```
    """
    def __init__(self, path: str, url: str):
        self.path = path
        self.url = url

    # === core git
    def git(self, subcmd: list) -> str:
        """run an arbitrary git subcommand on the repo located at `self.path`"""
        out = _git(self.path, subcmd=subcmd)
        return out

    # === clone
    def clone(self) -> bool:
        """clone from `self.url` to `self.path`"""
        return _clone(self.url, self.path)
    
    def remote_url(self, remote="origin") -> str:
        """returns the URL for the remote named `remote`."""
        return _remote_url(self.path, remote=remote)

    # === log
    def log(self, formats=("%h", "%at")) -> list:
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
    
    def latest_commit(self) -> tuple:
        """
        """
        # TODO more efficient to call `git log -1 ...`?
        latest = self.log()[0]
        return latest
    
    def earliest_commit(self) -> tuple:
        """
        """
        # TODO more efficient to call `git log --reverse -1 ...`?
        earliest = self.log()[-1]
        return earliest

    # === branches
    def list_branches(self) -> str:
        """run `git branch --format=%(refname:short)`"""
        branches = _git(self.path, subcmd=["branch", "--format=%(refname:short)"])
        return branches.splitlines()

    def current_branch(self) -> str:
        """run `git branch --current-branch`"""
        branch = _git(self.path, subcmd=["branch", "--show-current"]).rstrip()
        return branch

    def checkout_branch(self, branch: str) -> str:
        """run `git checkout [branch]`"""
        _ = _git(self.path, subcmd=["checkout", "--quiet", branch])
        return branch

    def temp_branch(self) -> str:
        """run `git checkout -b [branch]`"""
        branch = "retrograde" + _rand_string(10)
        _ = _git(self.path, subcmd=["checkout", "--quiet", "-b", branch])
        return branch

    def delete_branch(self, branch) -> bool:
        """run `git checkout -D [branch]`"""
        try:
            _ = _git(self.path, subcmd=["branch", "--quiet", "-D", branch])
            return True
        except BaseException as e:
            raise e

    # === reset
    def reset(self, commit) -> str:
        """hard reset to commit"""
        out = _git(self.path, subcmd=["reset", "--hard", commit])
        return out

    # === rebase
    def rebase(self, branch):
        """rebase current branch from `branch`"""
        out = _git(self.path, subcmd=["rebase", "--quiet", branch])
        return out


@contextmanager
def retrograde(repo: Repo):
    """

    """
    try:
        repo.clone()
        orig_branch = repo.current_branch()
        temp_branch = repo.temp_branch()
        yield repo
    finally:
        repo.checkout_branch(branch=orig_branch)
        repo.delete_branch(branch=temp_branch)
        

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

def _remote_url(path: string, remote="origin") -> str:
    """get the URL for the remote named `remote`"""
    out = _git(path, subcmd=["remote", "get-url", remote])
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


if __name__ == "__main__":
    with TemporaryDirectory() as d:
        repo = Repo(path = str(d), url = ".")
        repo.clone()
        print(repo.rev_list())