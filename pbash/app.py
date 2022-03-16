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

"""Main application file
"""

import os
import sys
import json
import select

import click
from rich import print

from .modules.ui import ui
from .modules.git import git
from .modules.params import params
from .modules.commands import commands, CommandFile

from .appConfig import app, AppConfig


class Config(AppConfig):
    """Specific application config class
    """
    path: str = ""
    usegit: bool = False
    gitrepo: str = ""
    gituser: str = ""
    gitmail: str = ""
    gitbranch: str = "main"


# RUN #################################################################################################################

def create_config_file(path: str) -> Config:
    """Create config file

    Args:
        path (str): config file path

    Returns:
        Config: config object
    """
    config = Config(path)
    config.create()
    return config


def load_config(section: str, new_section: bool = False) -> Config:
    """Load config file

    Args:
        section (str): config section
        new_section (bool, optional): if True, creates a new section. Defaults to False.

    Returns:
        Config: config object
    """
    config_file = app.default_rcpath()
    if not os.path.exists(config_file):
        config = create_config_file(config_file)
    else:
        config = Config(config_file)
    if new_section:
        AppConfig.add_section(config_file, section, Config(config_file))
    if not config.load(section):
        handle_error("Application cannot load config file")
    return config


def init_context(section: str) -> Config:
    """Initialise the context

    Args:
        section (str): config section

    Returns:
        Config: config object
    """
    config = load_config(section)
    if (not os.path.exists(config.path)):
        handle_error(f"Application is not initialized. Please run [code] {app.name()} init [/]")
    return config


def recup_context(ctx) -> str:
    """Get context elements from global

    Args:
        ctx: cli context

    Returns:
        str: context name
    """
    context: str = ctx.obj["context"]
    return context


def init_command(ctx, print_ui: bool = True) -> Config:
    """Initialise a command

    Args:
        ctx: cli context

    Returns:
        Config: config object
    """
    context = recup_context(ctx)
    config: Config = init_context(context)
    if print_ui and not config.usegit:
        print("[yellow italic]WARNING: Git is not configured[/]\n")
    return config


# GLOBAL ##############################################################################################################

def handle_success(message: str):
    """Handle success return

    Args:
        message (str): message
    """
    ui.print_info(message)


def handle_data(data: json, fn):
    """Handle success return (with data)

    Args:
        data (json): data
        fn (function): message
    """
    fn(data)


def handle_error(error):
    """Handle error return

    Args:
        error (_type_): error message
    """
    ui.print_error(error)
    exit(2)


# COMPLETION ##########################################################################################################

def complete_store(ctx, param, incomplete):
    items = app.sections()
    return list(filter(lambda i: incomplete.lower() in i.lower(), items))


def complete_filter(ctx, param, incomplete):
    store = ctx.parent.params["context"]
    config: Config = init_context(store)
    items = commands.get_list(config.path, incomplete)
    return list(map(lambda i: f"\"{i.f_name}\"", items))


# CLI #################################################################################################################

@click.pass_context
def run_command(ctx, cmd: CommandFile, **kwargs):
    """Run a specific command

    Args:
        ctx (_type_): context
        cmd (CommandFile): command details
    """
    stdin_values = []
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        for line in sys.stdin:
            stdin_values.append(line.removesuffix("\n"))

    try:
        if len(cmd.params) == 0:
            values_str = ""
        else:
            values_str = "("
            index = 0
            for param in cmd.params:
                value = ""
                if index < len(stdin_values):
                    value = stdin_values[index]
                index += 1
                if value == "" and param.name in kwargs.keys():
                    value = kwargs[param.name]
                    if value == param.default and param.ask_always:
                        value = ui.ask(param.message, param.default)
                if value == "":
                    value = ui.ask(param.message, param.default)
                assert (value != ""), f"Value for <{param.name}> must not be empty"
                values_str += f"echo \"{value}\"; "
            values_str = values_str.removesuffix("; ")
            values_str += ") | "
        os.system(f"{values_str}{cmd.path}")
    except Exception as error:
        handle_error(error)


def run(cmd: CommandFile):
    """Helper to run a command

    Args:
        cmd (CommandFile): command

    Returns:
        lambda: callback function for command
    """
    return lambda **kwargs: run_command(cmd, **kwargs)


@click.group()
@click.pass_context
@click.version_option(app.version())
@click.option("-c", "--context", default="DEFAULT", help="Section of config file to load (default is DEFAULT)",
              shell_complete=complete_store)
def cli(ctx, context):
    """Bash Script Manager
    """
    ctx.obj["context"] = context
    config: Config = init_command(ctx, False)
    cmds = commands.get_list(config.path)
    for cmd in cmds:
        params = []
        for param in cmd.params:
            params.append(click.Option([f"--{param.name}"], help=param.message, default=param.default))
        cli_run.add_command(click.Command(cmd.f_name, params=params, callback=run(cmd), help=cmd.desc))
    pass


@cli.group("run")
@click.pass_context
def cli_run(ctx: click.Context):
    """Run command
    """
    pass


# INITIALISATION ######################################################################################################

@cli.command("init")
@click.pass_context
@click.option("--new-section", is_flag=True, help="Create a new section for selected context")
@click.option("--path", default=app.default_path(), help="Path where the files are stored")
@click.option("--edit", is_flag=True, help="Edit configuration file")
def cli_init(ctx, new_section: bool, path: str, edit: bool):
    """Initialize the application for the current context
    """
    context = recup_context(ctx)
    try:
        if edit:
            click.edit(filename=app.default_rcpath())
        else:
            config = load_config(context, new_section)
            if path == app.default_path() and new_section:
                path = path[:len(path)-1] + "-" + context.lower()
            config.path = params.validate_path(path, "Path")
            config.save(context)
            handle_success("Application initialized")
    except Exception as error:
        handle_error(error)


@cli.command("init-git")
@click.pass_context
@click.option("--repo", default="", help="Git repository")
@click.option("--user", default="", help="Git username")
@click.option("--mail", default="", help="Git email")
@click.option("--branch", default="", help="Git branch")
@click.option("--pull", is_flag=True, help="Pull existing git repository")
def cli_init_git(ctx, repo: str, user: str, mail: str, branch: str, pull: bool):
    """Initialize git
    """
    context = recup_context(ctx)
    try:
        config = load_config(context)
        config.usegit = True
        config.gitrepo = params.validate(repo, "Git repository")
        config.gituser = params.validate(user, "Git username")
        config.gitmail = params.validate(mail, "Git email")
        config.gitbranch = params.validate(branch, "Git branch", "main")
        config.save(context)
        if not pull:
            # Write default files
            f = open(os.path.join(config.path, ".gitattributes"), "w")
            f.write("*.sh diff=sh")
            f.close()
        git.init(config.path, config.gitrepo, config.gitbranch, config.gituser, config.gitmail, pull)
        handle_success("Git initialized")
    except Exception as error:
        handle_error(error)


# COMMANDS ############################################################################################################

@cli.command("list")
@click.pass_context
@click.argument("filter", default="", shell_complete=complete_filter)
def cli_list(ctx, filter: str):
    """List commands
    """
    config: Config = init_command(ctx)
    try:
        items = commands.get_list(config.path, filter)
        handle_data(items, ui.show_commands)
        handle_success(config.path)
    except Exception as error:
        handle_error(error)


@cli.command("edit")
@click.pass_context
@click.argument("filter", default="", shell_complete=complete_filter)
def cli_edit(ctx, filter: str):
    """Edit command
    """
    config: Config = init_command(ctx)
    try:
        items = commands.get_list(config.path, filter)
        cmd = params.validate_command(items)
        click.edit(filename=cmd.path)
        if config.usegit:
            git.commit(config.path, f"Update command file <{cmd.f_name}>", config.gitbranch)
        handle_success("File edited")
    except Exception as error:
        handle_error(error)


@cli.command("new")
@click.pass_context
@click.option("--name", default="", help="Command name")
@click.option("--desc", default="", help="Command description")
@click.option("--param", help="Command param", multiple=True)
def cli_new(ctx, name: str, desc: str, param: list[str]):
    """New command
    """
    config: Config = init_command(ctx)
    try:
        name = params.validate(name, "Command name")
        new_path = os.path.join(config.path, f"{name}.sh")
        assert (not os.path.exists(new_path)), "File already exists"
        desc = params.validate(desc, "Command description")
        commands.create(new_path, desc, param)
        if config.usegit:
            git.commit(config.path, f"Create command file <{name}>", config.gitbranch)
        handle_success("File created")
    except Exception as error:
        handle_error(error)


@cli.command("delete")
@click.pass_context
@click.argument("filter", default="", shell_complete=complete_filter)
def cli_delete(ctx, filter: str):
    """Delete command
    """
    config: Config = init_command(ctx)
    try:
        items = commands.get_list(config.path, filter)
        cmd = params.validate_command(items)
        # CONFIRM DELETION
        confirmed = ui.confirm("Delete command file")
        assert (confirmed), "Command deletion has been cancelled"
        # DELETE
        os.remove(cmd.path)
        if config.usegit:
            git.commit(config.path, f"Delete command file <{cmd.f_name}>", config.gitbranch)
        handle_success("File deleted")
    except Exception as error:
        handle_error(error)


# GIT #################################################################################################################

@cli.group("git")
@click.pass_context
def cli_git(ctx: click.Context):
    """Git commands
    """
    pass


@cli_git.command("status")
@click.pass_context
def cli_git_status(ctx: click.Context):
    """Git status
    """
    config = init_command(ctx)
    try:
        git.status(config.path)
    except Exception as error:
        handle_error(error)


@cli_git.command("pull")
@click.pass_context
def cli_git_pull(ctx: click.Context):
    """Git pull
    """
    config = init_command(ctx)
    try:
        git.pull(config.path, config.gitbranch)
    except Exception as error:
        handle_error(error)


@cli_git.command("push")
@click.pass_context
def cli_git_push(ctx: click.Context):
    """Git push
    """
    config = init_command(ctx)
    try:
        git.push(config.path, config.gitbranch)
    except Exception as error:
        handle_error(error)


@cli_git.command("sync")
@click.pass_context
def cli_git_sync(ctx: click.Context):
    """Git pull then Git push
    """
    config = init_command(ctx)
    try:
        git.sync(config.path, config.gitbranch)
    except Exception as error:
        handle_error(error)
