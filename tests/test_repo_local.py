# SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest
from retrograde.repo import Repo


@pytest.fixture(scope="session", autouse=True)
def test_repo_local():
    repo = Repo(
        path = "demo",
        url = "https://github.com/sboysel/awesome-oss-research-data"
    )
    yield repo

def test_log_iterate(test_repo_local):
    repo = test_repo_local
    orig_branch = repo._current_branch()
    temp_branch = repo._temp_branch()
    assert orig_branch != temp_branch
    log = repo._log()
    n = len(log)
    for commit, _ in log[1:]:
        repo._reset(commit)
        n -= 1
        assert len(repo._log()) == n
    
    repo._rebase(orig_branch)
    assert log == repo._log()
    repo._checkout_branch(orig_branch)
    assert log == repo._log()

def test_log_commits(test_repo_local):
    repo = test_repo_local
    commits = repo._log()
    assert isinstance(commits, list)
    assert isinstance(commits[0], tuple)
    assert len(commits[0]) == 2

def test_log_commits_with_timestamps(test_repo_local):
    repo = test_repo_local
    log = repo._log()
    timestamps = [x[1] for x in log]
    assert sorted(timestamps, reverse=True) == timestamps

