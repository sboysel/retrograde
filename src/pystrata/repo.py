from pystrata.git import (
    _git,
    _clone,
    _current_branch,
    _checkout_branch,
    _checkout_new_branch,
    _log_commits,
    _log_commit_most_recent
) 
    
class Repo:
    """
    """
    def __init__(self, path, url):
        self.path = path
        self.url = url
        self.clone()

    def _git(self, subcmd):
        """run an arbitrary git subcommand on the repo located at `self.path`"""
        return _git(self.path, subcmd=subcmd)

    def clone(self):
        """clone from `self.url` to `self.path`"""
        return _clone(self.url, self.path)

    def current_branch(self):
        """run `git branch --current-branch`"""
        return _current_branch(self.path)

    def checkout_branch(self, branch):
        """run `git checkout [branch]`"""
        return _checkout_branch(self.path, branch)
    
    def checkout_new_branch(self, branch):
        """run `git checkout -b [branch]`"""
        return _checkout_new_branch(self.path, branch)

    def commits(self):
        """return list of commits hashes"""
        return _log_commits(self.path)
    
    def commit_most_recent(self):
        """return list of commits hashes"""
        return _log_commit_most_recent(self.path)      
        
