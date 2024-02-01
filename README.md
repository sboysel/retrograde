# retrograde

[![PyPI - Version](https://img.shields.io/pypi/v/retrograde.svg)](https://pypi.org/project/retrograde)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/retrograde.svg)](https://pypi.org/project/retrograde)

Rewind a git repository through its development history.

retrograde automates the process of traversing through the commit log of a git repository and ``rewinding'' the project's state through a sequence snapshots. In a typical workflow, retrograde will clone  a repository, checkout a temporary branch, and iteratively roll back the repository's state to earlier commits. retrograde aims for extensibility by allowing users to integrate their own metrics that can be executed at each snapshot. This enables researchers to effeciently and flexibly characterize the developmental histories of large batches of software repositories. See the [Usage](#usage) section for a demonstration of typical usage.

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [See Also](#see-also)
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
import tempfile
import retrograde

# Extend the base Repo class with your own methods
class ExtendedRepo(retrograde.repo.Repo):
    def n_files(self):
        """
        Count the number of files tracked in the codebase.
        """
        files = self.git(["ls-files"]).splitlines()
        return len(files)

# initialize a repository object
tmp = tempfile.TemporaryDirectory()
repo = ExtendedRepo(tmp, "https://github.com/sboysel/retrograde")


# retrograde clones and rewinds the repository's state in reverse 
# chronological roder.
results = []
with retrograde.retrograde(repo) as r:
    for commit, timestamp in r.log():
        r.reset(commit)
        results.append((timestamp, commit, r.n_files()))        
```

## See Also

- [ishepard/pydriller](https://github.com/ishepard/pydriller)
    - In comparison to pydriller, retrograde simply rewinds a repository through
      a sequence of development snapshots. You can then define your own metric 
      to characterize the repository's state at each snapshot. Hence retrograde
      seeks a narrower scope of functionality and aims for extensibility while
      pydriller develops a more complete mapping between git repository primitives
      and python objects.
- [src-d/hercules](https://github.com/src-d/hercules) and `labours`
- [erikbern/git-of-theseus](https://github.com/erikbern/git-of-theseus)

## License

[MIT License](https://spdx.org/licenses/MIT.html)

Copyright (c) 2024-present Sam Boysel <sboysel@gmail.com>
