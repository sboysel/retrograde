# SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>
#
# SPDX-License-Identifier: MIT
import datetime
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from retrograde.repo import (
    Repo,
    retrograde,
    _datetime2unix,
    _is_git_repo,
    _rand_string,
    _unix2datetime
)

URL = "https://github.com/sboysel/awesome-oss-research-data"
PATH = TemporaryDirectory()
# PATH = Path("/tmp", "awesome-oss-research-data")

@pytest.fixture(scope="session", autouse=True)
def test_repo():
    path, url = PATH, URL
    repo = Repo(
        str(path),
        url
    )
    yield repo
    if isinstance(path, TemporaryDirectory):
        path.cleanup()

# === clone
# RUN THIS TEST FIRST
def test_repo_clone_empty_directory(test_repo):
    """cloning into empty directories should work"""
    repo = test_repo
    assert repo.clone()

def test_repo_clone_bad_url(test_repo):
    """raise an exception for bad URLs"""
    repo = test_repo
    repo.url = "bad url"
    with pytest.raises(subprocess.CalledProcessError) as e:
        repo.clone()
    # reset test repo object
    repo.url = URL

def test_repo_clone_nonempty_directory():
    """cloning into non-empty directories ought to throw an exception"""
    with TemporaryDirectory() as d:
        repo = Repo(
            path = d,
            url = URL
        )
        with NamedTemporaryFile(dir=d) as f:
            with pytest.raises(BaseException) as e:
                repo.clone()

# === main workflow
def test_main_workflow(test_repo):
    repo = test_repo
    orig_branch = repo.current_branch()
    temp_branch = repo.temp_branch()
    assert orig_branch != temp_branch
    log = repo.log()
    n = len(log)
    for commit, _ in log[1:]:
        repo.reset(commit)
        n -= 1
        assert len(repo.log()) == n

    repo.rebase(orig_branch)
    assert log == repo.log()
    repo.checkout_branch(orig_branch)
    assert log == repo.log()

def test_main_workflow_context_manager(test_repo):
    repo = test_repo
    orig_branch = repo.current_branch()
    commits = repo.log()
    with retrograde(repo) as r:
        for commit, _ in commits:
            repo.reset(commit)
    # verify
    assert commits == repo.log()
    assert orig_branch == repo.current_branch()

# === checkout
def test_repo_checkout_branch(test_repo):
    repo = test_repo
    starting_branch = repo.current_branch()
    branches = repo.list_branches()
    assert starting_branch in branches
    # errors when checking out non-existant branchs
    with pytest.raises(subprocess.CalledProcessError) as e:
        repo.checkout_branch(_rand_string(10))
    # temp branches
    temp_branch = repo.temp_branch()
    assert repo.current_branch() == temp_branch
    repo.checkout_branch(starting_branch)
    assert repo.current_branch() == starting_branch
    # deleting branches
    repo.delete_branch(temp_branch)
    assert temp_branch not in repo.list_branches()

# === log
def test_log_commits(test_repo):
    repo = test_repo
    commits = repo.log()
    assert isinstance(commits, list)
    assert isinstance(commits[0], tuple)
    assert len(commits[0]) == 2

def test_log_commits_with_timestamps(test_repo):
    repo = test_repo
    log = repo.log()
    timestamps = [x[1] for x in log]
    assert sorted(timestamps, reverse=True) == timestamps

# === utils
def test_is_git_repo():
    retrograde_project_root = Path.cwd()
    assert _is_git_repo(str(retrograde_project_root))
    assert not _is_git_repo(str(retrograde_project_root / "tests"))
    assert not _is_git_repo(str(retrograde_project_root / "src"))

def test_utils_date_conversions():
    date_time = datetime.datetime(1969, 12, 31, 19, 0)
    assert _datetime2unix(date_time) == 0
    assert _unix2datetime(0) == date_time

def test_utils_rand_string():
    assert isinstance(_rand_string(5), str)
    assert _rand_string(5) != _rand_string(5)
    assert len(_rand_string(5)) == 5
