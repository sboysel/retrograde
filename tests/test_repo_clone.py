# SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest
from tempfile import TemporaryDirectory, NamedTemporaryFile
from retrograde.repo import (
    Repo,
    _is_git_repo,
    _is_cloned
)


@pytest.fixture(scope="session", autouse=True)
def test_repo_clone():
    path = TemporaryDirectory()
    url = "https://github.com/sboysel/awesome-oss-research-data"
    repo = Repo(path.name, url)
    yield (repo, path, url)
    path.cleanup()

@pytest.mark.skip()
def test_repo_init(test_repo_clone):
    repo, path, url = test_repo_clone
    assert repo.path == path.name
    assert repo.url == url

@pytest.mark.skip()
def test_repo_clone(test_repo_clone):
    repo, _, _ = test_repo_clone
    assert repo._clone()
    repo.url = "bad url"
    with pytest.raises(Exception) as e:
        repo._clone()

def test_repo_clone_nonempty_directory():
    """cloning into non-empty directories ought to throw an exception"""
    with TemporaryDirectory() as d:
        repo = Repo(
            path = d,
            url = "https://github.com/sboysel/awesome-oss-research-data"
        )
        with NamedTemporaryFile(dir=d) as f:
            with pytest.raises(BaseException) as e:
                repo._clone()

def test_repo_clone_empty_directory():
    """cloning into empty directories should work"""
    repo = Repo(
        path = "demo",
        url = "https://github.com/sboysel/awesome-oss-research-data"
    )
    with TemporaryDirectory() as d:
        repo.path = d
        assert repo._clone()

def test_repo_clone_bad_url():
    """raise an exception for bad URLs"""
    repo = Repo(
        path = "demo",
        url = "bad url"
    )
    with pytest.raises(Exception) as e:
        repo._clone()


def test_repo_is_cloned():
    repo = Repo(
        path = "demo",
        url = "https://github.com/sboysel/awesome-oss-research-data"
    )
    # local clone exists
    assert _is_cloned(repo.url, repo.path)
    # empty directory
    tmpdir = TemporaryDirectory()
    assert not _is_cloned(repo.url, tmpdir.name)
    # cleanup
    tmpdir.cleanup()

def test_is_git_repo():
    assert not _is_git_repo("foo")

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


