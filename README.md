# Welcome to pbash

[![](https://badgen.net/github/release/sguerri/pbash)](https://github.com/sguerri/pbash/releases/)
[![](https://img.shields.io/github/workflow/status/sguerri/pbash/Build/v0.1.0)](https://github.com/sguerri/pbash/actions/workflows/build.yml)
[![](https://badgen.net/github/license/sguerri/pbash)](https://www.gnu.org/licenses/)
[![](https://badgen.net/pypi/v/pbash)](https://pypi.org/project/pbash/)
[![](https://badgen.net/pypi/python/pbash)](#)
[![](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](#)

> Bash Script Manager

**pbash** helps managing a set of bash scripts. It keeps the logic of one file per script, but creates aliases and handle parameter prompt and pipe.

**Main features**
* bash script run
* parameter prompt
* parameter pass through pipe
* automatic cli command and option from the script
* git support
* possibility to handle several distinct stores
* commands and params autocompletion

**Roadmap**
* enhanced filter
* test on other platforms
* code cleaning

---

- [Welcome to pbash](#welcome-to-pbash)
  * [Installation](#installation)
    + [Requirements](#requirements)
    + [Install from pypi](#install-from-pypi)
    + [Install from deb package](#install-from-deb-package)
  * [Usage](#usage)
    + [Initialise](#initialise)
    + [Create a new script](#create-a-new-script)
    + [Script template](#script-template)
    + [Run a script](#run-a-script)
    + [Run a script (example)](#run-a-script--example-)
    + [List scripts](#list-scripts)
    + [Edit a script](#edit-a-script)
    + [Filter](#filter)
    + [Add a new store](#add-a-new-store)
    + [Use a store](#use-a-store)
    + [Initialise new git repository](#initialise-new-git-repository)
    + [Initialise from existing git repository](#initialise-from-existing-git-repository)
    + [Publish to git](#publish-to-git)
    + [Shortcuts and Aliases](#shortcuts-and-aliases)
  * [Build](#build)
  * [Dependencies](#dependencies)
  * [Author](#author)
  * [Issues](#issues)
  * [License](#license)

## Installation

### Requirements

The application is developped and used on ubuntu 21.10, with python 3.9.7. Any feedback on other platforms is welcomed.

- python3 >=3.6.2,<4.0
- git: `sudo apt install git`
- nano: `sudo apt install nano`

### Install from pypi

```bash
pip install pbash
```

For an isolated environment with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install pbash
```

### Install from deb package

A deb package is available, built using `dh-virtualenv`. Installing this package will create a new Python virtual environment in `opt/venvs`. It will then create the symlink `usr/bin/pbash` pointing to `opt/venvs/pbash/bin/pbash`.

Note that `dh-virtualenv` built packages are dependent of python version. Use this only if you have default python version installed:
* ubuntu bionic 18.04: Python 3.6
* ubuntu focal 20.04: Python 3.8
* ubuntu hirsute 21.04: Python 3.9
* ubuntu impish 21.10: Python 3.9

Download latest `.deb` file from the [release page](https://github.com/sguerri/pbash/releases).

```bash
sudo dpkg -i pbash_0.1.0_{{os}}_amd64.deb
```

## Usage

### Initialise

Initialisation is required before using the application, to create the working diretory.

```bash
pbash init
```

A configuration file `.pbashrc` is created in the user home directory.

By default, scripts will be stored in `${HOME}/.pbash/` folder.

The `--edit` option will open configuration file in edit mode.

### Create a new script

You can create a new script file.

```bash
pbash new --name "${NAME}" --desc "${DESCRIPTION}" --param "${PARAM1}" --param "${PARAM2}"
```

If options are not given, they will be prompted at run.

For param details, see below.

### Script template

To add a description to the script, add a comment line beginning with `#DESC `.

```bash
#DESC ...
```

To add a param to the script, add a comment line beginning with `#PARAM `.

```bash
#PARAM <name>, <question>, <default>, <always_prompt>
```

Only `<name>` is required. This value must be strict alphanumeric. The application will automatically create an option `--<name>` for the cli `run` command.

`<question>` is used for cli prompt and option help message. Default is empty string.

`<default>` is the default value. Default is empty string.

`<always_prompt>` is used to display prompt even when a default value is given. Set to `true` if desired. Default is `false`.

### Run a script

The generic `run` command calls the corresponding script.

```bash
pbash run <name>
```

Options are automatically created based on script informations.

### Run a script (example)

Let's take the below script `example.sh`

```bash
#!/bin/bash
#PARAM user, User
#PARAM message, Which message
read -p "User: " user
read -p "Which message: " message
echo "$user says $message"
```

The script can be run directly through terminal.

It can also be run through **pbash** : the params will be prompted

```bash
pbash run example
```

It can be run with options :

```bash
pbash run example --user "Sebastien" --message "Hello World!"
```

Or with piped arguments

```bash
(echo "Sebastien"; echo "Hello World!") | pbash run example
# or
cat <(echo "Sebastien") <(echo "Hello World!") | pbash run example
```

*Note : for piped arguments, all params must be given so that it works*

### List scripts

```bash
pbash list <filter>
```

### Edit a script

Script edition will open the file in default cli editor.

```bash
pbash edit <filter>
```

### Filter

Currently command filter is only done on the script file name.

A future enhancement will provide a better filter functionnality.

`pbash <command> <anything>` will filter displayed scripts based on `anything` value (name containing this value).

### Add a new store

You can create several stores (config sections). Default store path is `${HOME}/.pbash-${NAME}/`

```bash
pbash -c "${STORE}" init --new-section
```

You can also select path via the option `--path`. The folder will be created if it does not exist.

```bash
pbash -c "${STORE}" init --new-section --path "${PATH}"
```

### Use a store

All functions can be used for a specific store by using the `-c` option from **pbash** application.

```bash
pbash -c "${STORE}" new ...
pbash -c "${STORE}" list ...
pbash -c "${STORE}" run ...
# etc.
```

### Initialise new git repository

You can initialise a new git repository in store path. It will set automatic git push for every script creation or modification. The git repository needs to be created on your platform before.

A default branch `main` is created.

```bash
pbash -c "${STORE}" init-git
```

You can also pass parameter through cli command:

```bash
pbash -c "${STORE}" init-git --repo "${REPO}" --user "${USER}" --mail "${EMAIL}" --branch "${BRANCH}"
```

### Initialise from existing git repository

If the git repository already exists, you can restore it in the current store folder by adding the `--pull` option to `init-git` command.

It will download the latest commit from `main` branch. If the branch name is different, you can update it in the config file through `pbash init --edit` or through `--branch` option.

### Publish to git

When a git repository is enabled, all changes to scripts will be pushed to remote. However, there will never be automatic pull to retrieve potential scripts changes from remote (from other application, computer, user, aso.).

It can be done manually through

```bash
pbash -c "${STORE} git pull"
  # or
pbash -c "${STORE} git sync" # pull then push
```

In case a remote change is done but not pulled, the automatic push on script modification will fail. A manual `git sync` will be required to merge local and remote.

### Shortcuts and Aliases

Application must give a fast access to scripts to be useful.

I personnaly defined shortcuts in my home `.bashrc` file:

```bash
alias pb='pbash -c PRO'
alias pbr='pbash -c PRO run'
alias pbp='pbash -c PERSO'
alias pbpr='pbash -c PERSO run'
```

## Build

**Requirements**

- debhelper: `sudo apt install debhelper`
- [dh-virtualenv](https://github.com/spotify/dh-virtualenv)
- [build](https://github.com/pypa/build)
- [virtualenv](https://virtualenv.pypa.io/en/latest/)

**Commands**

```bash
poetry install

# build deb
dpkg-buildpackage -us -uc
dpkg-buildpackage -Tclean

# build python package
python3 -m build
```

## Dependencies

**Python Libraries**
- [click](https://palletsprojects.com/p/click/)
- [rich](https://github.com/Textualize/rich)

**Python Development Libraries**
- [poetry](https://python-poetry.org/)

## Author

Sébastien Guerri - [github page](https://github.com/sguerri)

## Issues

Contributions, issues and feature requests are welcome!

Feel free to check [issues page](https://github.com/sguerri/pbash/issues). You can also contact me.

## License

Copyright (C) 2022 Sebastien Guerri

pbash is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

pbash is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with pbash. If not, see <https://www.gnu.org/licenses/>.