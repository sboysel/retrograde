import subprocess

def _proc(cmd):
    subprocess.run(cmd, capture_output=False)

def _proc_out(cmd):
    subprocess.run(cmd, capture_output=True, text=True).stdout

def _clone(url, path):
    """clone from `self.url` to `self.path`"""    
    cmd = ["git", "clone", f"{url}", f"{path}"]
    _proc(cmd)

def _status(path):
    """run `git status`"""
    cmd = ["git", f"--git-dir={path}/.git", f"--work-tree={path}", "status"]
    out = _proc_out(cmd)
    return out

def _current_branch(path):
    """run `git branch --current-branch`. Requires git>=2.22"""
    cmd = ["git", f"--git-dir={path}/.git", f"--work-tree={path}", "branch", "--current-branch"]
    out = _proc_out(cmd)
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
        
