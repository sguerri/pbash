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

"""Handle commands
"""

import os
import stat
import json


class CommandFileParam:
    """CommandFileParam object
    """
    name: str
    message: str
    default: str
    ask_always: bool

    def __init__(self, name: str, message: str, default: str, ask_always: bool):
        self.name = name
        self.message = message
        self.default = default
        self.ask_always = ask_always

    def to_json(self) -> json:
        json_item: json = {}
        json_item["name"] = self.name
        json_item["message"] = self.message
        json_item["default"] = self.default
        json_item["ask_always"] = self.ask_always
        return json_item


class CommandFile:
    """CommandFile object
    """
    path: str
    root: str
    root_name: str
    f: str
    f_name: str
    desc: str
    params: list[CommandFileParam]

    def __init__(self, base: str, path: str):
        base = os.path.dirname(base)
        self.path = path
        self.root = os.path.dirname(self.path)
        self.root_name = self.root.replace(base, "")
        self.root_name = "/" if self.root_name == "" else self.root_name
        self.f = os.path.basename(self.path)
        self.f_name = self.f.replace(".sh", "")
        self.desc = ""
        self.params = []

        f = open(path)
        lines = f.readlines()
        for line in lines:
            if line.startswith("#DESC "):
                self.desc = line.removeprefix("#DESC ").strip()
            if line.startswith("#PARAM"):
                content = line.removeprefix("#PARAM").strip()
                items = content.split(",")
                param_name = items[0].strip()
                param_help = items[1].strip() if len(items) > 1 else ""
                param_default = items[2].strip() if len(items) > 2 else ""
                param_askalways = items[3].strip().lower() == "true" if len(items) > 3 else False
                self.params.append(CommandFileParam(param_name, param_help, param_default, param_askalways))
        f.close()

    def to_json(self) -> json:
        json_item: json = {}
        json_item["path"] = self.path
        json_item["root"] = self.root
        json_item["root_name"] = self.root_name
        json_item["f"] = self.f
        json_item["f_name"] = self.f_name
        json_item["desc"] = self.desc
        json_item["params"] = list(map(lambda p: p.to_json(), self.params))
        return json_item


class commands:
    """Static class for command files
    """

    @staticmethod
    def create(path: str, desc: str, param: list[str]):
        """Create a new command file

        Args:
            path (str): file path
            desc (str): file description
            param (list[str]): list of parameters
        """
        f = open(path, "w")
        f.write("#!/bin/bash\n")
        if desc != "":
            f.write(f"#DESC {desc}\n")
        for p in param:
            f.write(f"#PARAM {p}\n")
        f.write("echo \"Hello World!\"\n")
        f.close()
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)

    @staticmethod
    def get_list(path: str, filter: str = "") -> list[CommandFile]:
        """Return the list of command files

        Args:
            path (str): working directory
            filter (str): name filter

        Returns:
            list[CommandFile]: list of command files
        """
        assert (os.path.exists(path)), f"Path <{path}> does not exist"
        assert (os.path.isdir(path)), f"Path <{path}> is not a valid directory"

        items: list[CommandFile] = []
        for (root, dirs, files) in os.walk(path):
            # Loop all directories (only one level)
            dirs.sort()
            files.sort()
            is_root_ok = False

            root_name = root.replace(os.path.join(path, ""), "")

            if ".git" in root_name:
                # Skip git directory
                continue
            if filter == "" or filter.lower() in root_name.lower():
                # Check directory name vs filter
                # is_root_ok = True
                # TODO set this flag to True with enhanced filters
                pass

            for f in files:
                # Loop all files
                f_name = f.replace(".sh", "")

                is_file_ok = is_root_ok
                if not f.endswith(".sh"):
                    # Skip non sh files
                    continue
                if filter == "" or filter.lower() in f_name.lower():
                    # Check file name vs filter
                    is_file_ok = True
                if is_file_ok:
                    # Add to returned list
                    # items.append(CommandFile(root, root_name, f, f_name, os.path.join(root, f)))
                    items.append(CommandFile(path, os.path.join(root, f)))

        return items
