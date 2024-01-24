# retrograde

[![PyPI - Version](https://img.shields.io/pypi/v/retrograde.svg)](https://pypi.org/project/retrograde)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/retrograde.svg)](https://pypi.org/project/retrograde)

`retrograde` automates the process of rewinding a git repository and observing 
its development history. The typical workflow is the clone a repository, 
checkout a temporary branch, and iteratively roll back the repository's state to
earlier commits. This allows you to characterize the state the repository over 
its evolution at a high level of temporal granularity. In addition to this core
functionality, `retrograde` aims to be flexible and extensible by allowing
researchers to integrate their own metrics. See the [Usage](#usage) section for 
a demonstration.

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Dependencies

```
git
```

`git` must be installed and the executable must be accessible to `subprocess`. Tested with `v2.43.0`.

## Installation

Install with `pip`

```console
pip install git+https://github.com/sboysel/retrograde.git
```

## Usage

```python
import retrograde

# Extend Repo class with your own methods
class ExtendedRepo(retrograde.repo.Repo):
    def n_files(self):
        files = self.git(["ls-files"]).splitlines()
        return len(files)


# Define repo and commits to traverse over        
repo = ExtendedRepo(path, url)

# Safely traverse over *all* commits
results = []
with retrograde.retrograde(repo) as r:
    for commit, timestamp in r.log():
        r.reset(commit)
        results.append((timestamp, commit, r.n_files()))
```

## License

`retrograde` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
