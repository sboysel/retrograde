import pytest
from tempfile import TemporaryDirectory
from pystrata.repo import Repo

@pytest.fixture(scope="session", autouse=True)
def test_repo_clone():
    path = TemporaryDirectory()
    url = "https://github.com/sboysel/awesome-oss-research-data"
    repo = Repo(path.name, url)
    yield (repo, path, url)
    path.cleanup()

@pytest.fixture(scope="session", autouse=True)
def test_repo_local():
    repo = Repo(
        path = "demo",
        url = "https://github.com/sboysel/awesome-oss-research-data"
    )
    yield repo

@pytest.mark.skip()
def test_repo_init(test_repo_clone):
    repo, path, url = test_repo_clone
    assert repo.path == path.name
    assert repo.url == url

@pytest.mark.skip()
def test_repo_clone(test_repo_clone):
    repo, _, _ = test_repo_clone
    assert repo._clone()

@pytest.mark.skip()
def test_repo_current_branch(test_repo_clone):
    repo, _, _ = test_repo_clone
    assert repo._current_branch() == "main"

@pytest.mark.skip()
def test_repo_checkout_branch(test_repo_clone):
    repo, _, _ = test_repo_clone
    starting_branch = repo._current_branch()
    assert repo._checkout_new_branch("foo")
    assert repo._current_branch() == "foo"
    assert repo._checkout_branch(starting_branch)
    assert repo._current_branch() == starting_branch

def test_log_checkout(test_repo_local):
    repo = test_repo_local
    orig_branch = repo._current_branch()
    temp_branch = repo._temp_branch()
    assert orig_branch != temp_branch
    commits = repo._commits()
    assert isinstance(commits, list)
    i = len(commits)
    for commit in commits[1:]:
        repo._reset(commit)
        i -= 1
        assert len(repo._commits()) == i
    
    repo._rebase(orig_branch)
    assert commits == repo._commits()
    repo._checkout_branch(orig_branch)
    assert commits == repo._commits()

def test_log_commits():
    repo = test_repo_local
    commits = repo._commits()
    assert isinstance(commits, list)
