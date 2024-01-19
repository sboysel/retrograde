from tempfile import TemporaryDirectory
from pystrata.repo import Repo

tmp = TemporaryDirectory()

repo = Repo(
    path = tmp.name,
    url = "https://github.com/sboysel/awesome-oss-research-data"
)

assert repo.clone()
print(repo.status())
print(repo.current_branch())
# assert repo.status()
# assert repo.current_branch() == "main"

tmp.cleanup()
