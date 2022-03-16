# Copyright (C) 2022 Sebastien Guerri
#
# This file is part of pbash.
#
# pbash is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# pbash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Handle git actions
"""

import os
import subprocess


class git:
    """Static class for git actions
    """

    @staticmethod
    def status(path: str):
        """Return git status

        Args:
            path (str): working directory
        """
        subprocess.run(["git", "-C", path, "status"])

    @staticmethod
    def init(path: str, repo: str, branch: str, user: str, mail: str, pull: bool = False):
        """Initialise working directory

        Args:
            path (str): working directory
            repo (str): remote git repository
            branch (str): remote git repository branch
            user (str): remote git repository user
            mail (str): remote git repository email
            pull (bool, optional): If True, pull git repo instead of creating a new one. Defaults to False.
        """
        subprocess.run(["git", "-C", path, "init"], capture_output=False)
        subprocess.run(["git", "-C", path, "config", "user.name", user], capture_output=False)
        subprocess.run(["git", "-C", path, "config", "user.email", mail], capture_output=False)
        subprocess.run(["git", "-C", path, "remote", "add", "origin", repo], capture_output=False)
        if pull:
            git.pull(path, branch)
        else:
            subprocess.run(["git", "-C", path, "branch", "-M", branch], capture_output=False)
            fpath = os.path.join(path, ".gitignore")
            f = open(fpath, "w")
            f.close()
            git.commit(path, "Initial commit", branch)

    @staticmethod
    def pull(path: str, branch: str):
        """Pull remote repository

        Args:
            path (str): working directory
        """
        subprocess.run(["git", "-C", path, "pull", "origin", branch])
        subprocess.run(["git", "-C", path, "checkout", branch])

    @staticmethod
    def push(path: str, branch: str):
        """Push changes to remote

        Args:
            path (str): working directory
            branch (str): push branch
        """
        subprocess.run(["git", "-C", path, "push", "-u", "origin", branch])

    @staticmethod
    def sync(path: str, branch: str):
        """Pull then Push changes to remote

        Args:
            path (str): working directory
            branch (str): push branch
        """
        git.pull(path, branch)
        git.push(path, branch)

    @staticmethod
    def commit(path: str, message: str, branch: str):
        """Commit and push changes to remote

        Args:
            path (str): working directory
            message (str): commit message
            branch (str): commit branch
        """
        subprocess.run(["git", "-C", path, "add", "."], capture_output=False)
        subprocess.run(["git", "-C", path, "commit", "-m", message], capture_output=False)
        git.push(path, branch)
