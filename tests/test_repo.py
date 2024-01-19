import pytest
from tempfile import TemporaryDirectory
from pystrata.repo import Repo

@pytest.fixture(scope="session", autouse=True)
def test_repo():
    path = TemporaryDirectory()
    url = "https://github.com/sboysel/awesome-oss-research-data"
    repo = Repo(path.name, url)
    yield (repo, path, url)
    path.cleanup()

@pytest.mark.skip()
def test_repo_init(test_repo):
    repo, path, url = test_repo
    assert repo.path == path.name
    assert repo.url == url

@pytest.mark.skip()
def test_repo_clone(test_repo):
    repo, _, _ = test_repo
    assert repo.clone()

@pytest.mark.skip()
def test_repo_current_branch(test_repo):
    repo, _, _ = test_repo
    assert repo.current_branch() == "main"

@pytest.mark.skip()
def test_repo_checkout_branch(test_repo):
    repo, _, _ = test_repo
    starting_branch = repo.current_branch()
    assert repo.checkout_new_branch("foo")
    assert repo.current_branch() == "foo"
    assert repo.checkout_branch(starting_branch)
    assert repo.current_branch() == starting_branch
