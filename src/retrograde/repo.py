"""Repo class and associated git methods

This module implements the class `Repo` and the core functionality of retrograde.
The `Repo` class represents a git repository and exposes methods that execute git
operations on that respository.

`retrograde` automates the process of rewinding a git repository and observing 
its development history. In a typical workflow, `retrograde` will clone a repository, 
checkout a temporary branch, and iteratively roll back the repository's state to
earlier commits. This allows you to characterize the state the repository over 
its evolution at a high level of temporal granularity. In addition to this core
functionality, `retrograde` aims to be flexible and extensible by allowing
researchers to integrate their own metrics.

Usage:

    import retrograde

    # Extend Repo class with your own methods
    class ExtendedRepo(retrograde.repo.Repo):
        def n_files(self):
            files = self.git(["ls-files"]).splitlines()
            return len(files)


    # Define repo and commits to traverse over        
    repo = ExtendedRepo(path, url)

    # Safely traverse over *all* commits
    results = []
    with retrograde.retrograde(repo) as r:
        for commit, timestamp in r.log():
            r.reset(commit)
            results.append((timestamp, commit, r.n_files()))

            
SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>

SPDX-License-Identifier: MIT
"""
import datetime
import secrets
import string
import subprocess
import time
import traceback
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


# === Repo
class Repo:
    """<one line class description>

    <main class description>

    Attributes:
        path: path to local repository.
        url:  remote URL of the repository.
    """
    def __init__(self, path: str, url: str):
        """Initialize Repo object

        Args:
            path: path to local repository.
            url:  remote URL of the repository.
        """
        self.path = path
        self.url = url
        self._orig_branch = None
        self._temp_branch = None

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
        """returns the URL for the remote named `remote`. Therefore not 
           necessarily identical to `self.url`."""
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
    
    def latest_commit_since(self, timestamp) -> str:
        """
        Return the commit hash of the most recent commit *before* `timestamp`.
        `timestamp` needs to be some timestamp format recognized by git. See
        https://git-scm.com/docs/git-log
        """
        out = _git(
            self.path, 
            subcmd=["log", "-1", f"--before={timestamp}", "--format=%h"]
        ).rstrip()
        return out

    def latest_commit(self) -> tuple:
        """returns most recent hash and UNIX timestamp of most recent commit"""
        # TODO more efficient to call `git log -1 ...`?
        return self.log()[0]
    
    def earliest_commit(self) -> tuple:
        """returns most recent hash and UNIX timestamp of earliest commit"""
        # TODO more efficient to call `git log --reverse -1 ...`?
        return self.log()[-1]
    
    def is_history_linear(self) -> bool:
        """
        """
        begin = self.latest_commit()
        end = self.earliest_commit()
        commits_with_multiple_parents = _git(
            self.path, 
            subcmd=["rev-list", "--count", "--min-parents", f"{begin}..{end}"]
        ).rstrip()
        commits_with_multiple_parents = int(commits_with_multiple_parents)
        return commits_with_multiple_parents > 0

    # === branches
    def list_branches(self) -> str:
        """run `git branch --format=%(refname:short)`"""
        branches = _git(
            self.path,
            subcmd=["branch", "--format=%(refname:short)"]
        )
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
    
    # === utils
    def extract_commits_from_timestamps(self, timestamps):
        """For a list of timestamps, return a set of commits reflecting the 
           project state.
        
        For example,

        timestamps = [ 1           3, 4,          8,          10]
        log        = [  (hash1, 2),    (hash2, 6), (hash3, 9)]

        would return [(None, 1), (hash1, 3), (hash1, 3), (hash3, 8)]

        """
        # convert datetime inputs to UNIX timestamps
        unix_timestamps = [_datetime2unix(x) for x in timestamps]
        
        # for each timestamp, get the most recent commit at that point in time
        log = []
        for t in unix_timestamps:
            commit = self.latest_commit_since(timestamp=t)
            if commit == "":
                commit = None
            log.append((commit, t))

        # note: there may be duplicate commits in log
        return log


@contextmanager
def retrograde(repo: Repo):
    """Safely run retrograde operations in temporary branch"""
    repo.clone()
    orig_branch = repo.current_branch()
    temp_branch = repo.temp_branch()
    try:
        yield repo
    finally:
        repo.checkout_branch(branch=orig_branch)
        repo.delete_branch(branch=temp_branch)
        

# === core git binding
def _git(path, cmd=None, subcmd=[None]) -> str:
    """exectue git and subcommand at `path`"""
    if not cmd:
        cmd = ["git", "--no-pager", f"--git-dir={path}/.git", 
               f"--work-tree={path}"]
    cmd.extend(subcmd)
    try:
        out = subprocess.check_output(cmd, text=True, encoding="utf-8")
        return out
    except subprocess.CalledProcessError as e:
        print("git subprocess error : ", e.returncode, e.output)
        raise

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
    res = "".join(secrets.choice(choice_set) for i in range(n))
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

        timestamps = [
            datetime.datetime(2024, 1, 1, 1, 1, 1),
            datetime.datetime(2024, 1, 20, 1, 1, 1),
            datetime.datetime(2024, 1, 21, 1, 1, 1),
            datetime.datetime(2024, 1, 22, 1, 1, 1),
            datetime.datetime(2024, 1, 24, 1, 1, 1)
        ]
        print(timestamps)
        print(repo.extract_commits_from_timestamps(timestamps))