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

"""Utils for handling cli ui display
"""

import json

from rich import print
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table


class ui:
    """Static class for handling cli ui
    """

    @staticmethod
    def print_info(message: str):
        """Print information

        Args:
            message (str): message to display
        """
        print(f"[bright_black]{message}[/]")

    @staticmethod
    def print_error(*messages, must_exit: bool = True):
        """Print error

        Args:
            messages (str...): messages to display
            must_exit (bool, optional): if True, exit application. Defaults to True.
        """
        print("[red]ERROR:[/]", *messages)
        if must_exit:
            exit(2)

    @staticmethod
    def ask(message: str, default: str = "") -> str:
        """Prompt a value

        Args:
            message (str): prompt question
            default (str, optional): default value. Defaults to "".

        Returns:
            str: response
        """
        if default == "":
            return Prompt.ask(f"[spring_green4]{message}[/]")
        else:
            return Prompt.ask(f"[spring_green4]{message}[/]", default=default)

    @staticmethod
    def confirm(message: str, default_value: bool = False) -> bool:
        """Ask for confirmation

        Args:
            message (str): message to display
            default_value (bool, optional): default value. Defaults to False.

        Returns:
            bool: confirmation value
        """
        response = Confirm.ask(message, default=default_value)
        return response

    @staticmethod
    def show_table(json_content: json, show_unique: bool = False, show_index: bool = True):
        """Default function to display a table

        Args:
            json_content (json): content to display
            show_unique (bool, optional): if True show table when there is only one value. Defaults to False.
            show_index (bool, optional): if True show a column with autoindex. Defaults to True.
        """
        if len(json_content["rows"]) == 0:
            print("[italic]No data available[/]")
            return
        if not show_unique and len(json_content["rows"]) == 1:
            return

        console = Console()
        table = Table(show_header=True,
                      header_style="bold magenta underline",
                      box=None,
                      expand=True,
                      show_edge=False,
                      row_styles=["bright_white on grey7", ""])
        if show_index:
            table.add_column("N.", width=3)
        for header in json_content["headers"]:
            if "ratio" not in header:
                header["ratio"] = 1
            table.add_column(header["name"], ratio=header["ratio"])
        index = 1
        for line in json_content["rows"]:
            if show_index:
                table.add_row(str(index), *line)
            else:
                table.add_row(*line)
            index += 1
        console.print(table)

    @staticmethod
    def select_table(json_content: json) -> json:
        """Default function to select an entry from a table

        Args:
            json_content (json): table

        Returns:
            json: selected entry
        """
        if json_content is None:
            return None

        selected_index = 1
        if len(json_content["rows"]) > 1:
            list_index = list(range(1, len(json_content["rows"]) + 1))
            list_index_str = list(map(str, list_index))
            selected_index = IntPrompt.ask("[yellow italic]Select line[/]", choices=list_index_str, show_choices=False)
            print("")

        return json_content["content"][selected_index - 1]

    @staticmethod
    def show_commands(data) -> json:
        """Show the list of command files

        Args:
            data: list of command files

        Returns:
            json: list of command files in JSON format
        """
        json_items = list(map(lambda p: [p.root_name, p.f_name, p.desc], data))
        json_content = {}
        json_content["headers"] = [{"name": "Folder"}, {"name": "File"}, {"name": "Description"}]
        json_content["rows"] = json_items
        json_content["content"] = data
        ui.show_table(json_content, show_unique=True)
        return json_content

    @staticmethod
    def select_command(data) -> json:
        """Select a command file

        Args:
            data: list of command files

        Returns:
            json: selected command file
        """
        json_content = ui.show_commands(data)
        return ui.select_table(json_content)
