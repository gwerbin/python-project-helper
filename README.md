PPH (Python Project Helper) is a tool designed to help develop Python
software projects.

It is intended to be similar to [Poetry](https://python-poetry.org/) or
[Hatch](https://hatch.pypa.io/), in that it helps you do things like
create isolated virtual environments for your project. However, it is
*unlike* Poetry or Hatch in that it does not implement its own [PEP
517](https://peps.python.org/pep-0517/) build backend. Instead, PPH
works with *any* build backend, using existing tools to build packages
using the standard PEP 517 interface.

It is therefore also intended to be similar to
[Pipenv](https://pipenv.pypa.io/), being primarily a wrapper around
existing tools. However, it is *unlike* Pipenv in that Pipenv is
explicitly only designed to support the case of building an
"application" and not a "library". Instead, PPH makes no assumptions
about the purpose or structure of your project.

The PPH command-line and `pyproject.toml` interfaces are loosely
inspired by Hatch, but I make no claim or attempt at direct
compatibility.

| Feature                                                                                                 | Status                             |
|---------------------------------------------------------------------------------------------------------|------------------------------------|
| Automatically create venvs for your project                                                             | **Done** but still adding features |
| Inspect and extract project metadata                                                                    | **WIP**                            |
| JSON output for scripting                                                                               | **WIP**                            |
| Run project scripts                                                                                     | **TODO**                           |
| Build wheels, wrapping [Build](https://pypi.org/project/build/)                                         | **TODO**                           |
| Upload to PyPI, wrapping [Twine](https://pypi.org/project/twine/)                                       | **TODO**                           |
| CLI documentation & man page                                                                            | **TODO**                           |
| Stable Python API with documentation + readthedocs hosting                                              | **TODO**                           |
| Test suite                                                                                              | **TODO**                           |
| CI/CD                                                                                                   | **TODO**                           |
| Repo packaging                                                                                          | **TODO**                           |
| Generate "locked" requirements files, wrapping [Pip-tools](https://pypi.org/project/pip-tools/)         | **TODO**                           |
| Better UI/UX: shell completion, separating detailed logs from informational output, progress bars, etc. | **TODO**                           |
| "Matrix" environments and/or add an interface to Tox or Nox                                             | **Speculative**                    |
| Pass extra arguments to underlying tools (Pip, Venv, etc)                                               | **TODO**/**Speculative**           |
| Support [PDM](https://pdm.fming.dev/latest/) as a drop-in replacement for Pip?                          | **Speculative**                    |
| Support [Virtualenv](https://virtualenv.pypa.io/) as a drop-in replacement for Venv?                    | **Speculative**                    |

Features

I am deeply grateful to the many developers working hard on the Python
packaging ecosystem, and I mean no disrespect or negativity towards
other projects. I built this tool to meet my own needs, but I hope it
will be useful to other people.

Contributions are welcome, but I am doing this in my spare time and I
can’t guarantee rapid movement on anything.

**WARNING**: PPH is *alpha-quality* software under active development.
The CLI and its output formats are subject to change. Not currently
suitable for scripting.

# Installation

[Pipx](https://pypa.github.io/pipx/) is recommended for installing PPH
for general-purpose use. However it may also be installed using Pip or
any other PyPI-compatible package manager (such as PDM).

In the future, I hope to package PPH for package managers such as
Homebrew, Macports, Arch Linux, Debian, etc.

<div class="formalpara-title">

**Installation**

</div>

``` shell
# Install into the current environment:
pip install python-project-helper

# Install into an isolated environment with Pipx:
pipx install python-project-helper
```

# Usage

<div class="formalpara-title">

**Usage outline**

</div>

``` shell
pph

pph project
pph project inspect

pph env
pph env create {name}
pph env delete {name}
```

Virtual environments are created inside
`+$XDG_STATE_HOME/python-project-helper/`. The format inside this
directory is subject to change; do not depend on it for now.

# Dev instructions

Requires: \* Python (with `venv`) \* Make \* AsciiDoctor \* Pandoc

<div class="formalpara-title">

**Recommended setup**

</div>

``` shell#setup-script
#!/bin/sh

set -eux

git clone git@git.sr.ht:~wintershadows/python-project-helper pph
cd pph

git config user.name '...'
git config user.email '...'
git config user.signingkey '...'

make setup
source dev.venv/bin/activate
```

<div class="formalpara-title">

**Building**

</div>

``` shell#building
make build-python
```

<div class="formalpara-title">

**Publishing**

</div>

``` shell#building
make publish-testpypi
make publish-pypi
```
