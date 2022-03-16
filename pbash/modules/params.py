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

"""Utils for handling cli parameters validation
"""

import os

from rich import print
from rich.prompt import Prompt

from .commands import CommandFile

from .ui import ui


class params:
    """Static class for handling cli parameters validation
    """

    @staticmethod
    def validate(value: str,
                 message: str,
                 default_value: str = "",
                 print_old: bool = False,
                 old_value: str = "") -> str:
        """Generic string parameter validation

        Args:
            value (str): parameter value
            message (str): cli message for input
            default_value (str, optional): default value if cli input. Defaults to "".
            print_old (bool, optional): if True prints the existing value. Defaults to False.
            old_value (str, optional): existing value. Defaults to "".

        Returns:
            str: validated value
        """
        new_value = value.strip()
        if new_value == "":
            if print_old:
                print(f"Current value: {old_value}")
            if default_value == "":
                new_value = Prompt.ask(message)
            else:
                new_value = Prompt.ask(message, default=default_value)
            assert (new_value.strip() != ""), f"Incorrect <{message}> value"
        return new_value

    @staticmethod
    def validate_path(value: str, message: str) -> str:
        """Path parameter validation

        Args:
            value (str): parameter value
            message (str): cli message for input

        Returns:
            str: validated value
        """
        new_value = params.validate(value, message)
        if not os.path.exists(new_value):
            os.makedirs(new_value)
        return new_value

    @staticmethod
    def validate_command(items: list[CommandFile]) -> CommandFile:
        """Command file paramater validation

        Args:
            items (list[CommandFile]): list of command files

        Returns:
            CommandFile: validated command file
        """
        assert (len(items) != 0), "No command"
        if len(items) != 1:
            return ui.select_command(items)
        else:
            return items[0]
