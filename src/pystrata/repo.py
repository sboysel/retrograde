from git import (
    _clone, 
    _status, 
    _current_branch
) 
    
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
        
