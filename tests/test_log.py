import pytest
from pystrata.repo import Repo

def test_log_commits():
    repo = Repo(
        path = "demo",
        url = "https://github.com/sboysel/awesome-oss-research-data"
    )
    commits = repo.commits()
    assert commits[0] == repo.commit_most_recent()