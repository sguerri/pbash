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

"""Utils for application configuration
"""

import os
import configparser
import pkg_resources

from pathlib import Path

import click


class AppConfig:
    """Base application configuration class
    """
    __filepath__: str = ''

    def __init__(self, filepath: str):
        """Init class

        Args:
            filepath (str): config file path
        """
        self.__filepath__ = filepath

    def load(self, section: str) -> bool:
        """Load config file

        Args:
            section (str): section of config file

        Returns:
            bool: is loaded
        """
        try:
            if not os.path.exists(self.__filepath__):
                return False
            cfg = configparser.ConfigParser()
            cfg.read(self.__filepath__)
            if (section not in cfg.sections()) and (section != cfg.default_section):
                return False
            members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
            for member in members:
                if isinstance(getattr(self, member), str):
                    setattr(self, member, cfg[section][member])
                elif isinstance(getattr(self, member), bool):
                    setattr(self, member, cfg[section][member] == 'True')
            return True
        except Exception:
            return False

    def create(self, section: str = "DEFAULT"):
        """Create the config file

        Args:
            section (str, optional): section of config file. Defaults to "DEFAULT".
        """
        cfg = configparser.ConfigParser()
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for member in members:
            cfg[section][member] = str(getattr(self, member))
        with open(self.__filepath__, "w") as configfile:
            cfg.write(configfile)
            configfile.close()

    def save(self, section: str):
        """Save config file

        Args:
            section (str): section of config file
        """
        cfg = configparser.ConfigParser()
        cfg.read(self.__filepath__)
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for member in members:
            cfg[section][member] = str(getattr(self, member))
        with open(self.__filepath__, "w") as configfile:
            cfg.write(configfile)
            configfile.close()

    @staticmethod
    def add_section(filepath: str, section: str, item):
        """Add section to config file
        Static

        Args:
            filepath (str): config file path
            section (str): section of config file
            item: AppConfig extended class
        """
        cfg = configparser.ConfigParser()
        cfg.read(filepath)
        assert (section not in cfg.sections()), f"Section <{section}> already exists"
        cfg.add_section(section)
        members = [attr for attr in dir(item) if not callable(getattr(item, attr)) and not attr.startswith("__")]
        for member in members:
            cfg[section][member] = str(getattr(item, member))
        with open(filepath, "w") as configfile:
            cfg.write(configfile)
            configfile.close()

    @staticmethod
    def get_sections(filepath: str) -> list[str]:
        """Return the list of sections in config file

        Args:
            filepath (str): config file path

        Returns:
            list(str): List of section names
        """
        cfg = configparser.ConfigParser()
        cfg.read(filepath)
        return cfg.sections()


class AliasedGroup(click.Group):
    """Class used by click groups to create aliases for each function
    See click documentation
    """
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


class app:
    """Static class for handling application
    """

    @staticmethod
    def name() -> str:
        """Get application name

        Returns:
            str: application name
        """
        return "pbash"

    @staticmethod
    def version() -> str:
        """Get application version

        Returns:
            str: application version
        """
        return pkg_resources.get_distribution(app.name()).version

    @staticmethod
    def default_path() -> str:
        """Get application data path

        Returns:
            str: application data path
        """
        return os.path.join(Path.home(), "." + app.name() + "/")

    @staticmethod
    def default_rcpath() -> str:
        """Get application config file path

        Returns:
            str: application config file path
        """
        return os.path.join(Path.home(), "." + app.name() + "rc")

    @staticmethod
    def sections() -> list[str]:
        """Get list of config sections

        Returns:
            list[str]: list of config sections
        """
        return AppConfig.get_sections(app.default_rcpath())
