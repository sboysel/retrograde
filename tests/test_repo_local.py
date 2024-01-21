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

def test_log_commits(test_repo_local):
    repo = test_repo_local
    commits = repo._commits()
    assert isinstance(commits, list)

def test_log_commits_with_timestamps(test_repo_local):
    repo = test_repo_local
    commits = repo._commits_with_timestamps()
    timestamps = [x[1] for x in commits]
    assert sorted(timestamps, reverse=True) == timestamps