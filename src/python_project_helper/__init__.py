r"""PPH: Python Project Helper"""

import argparse
import dataclasses
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
import traceback
import venv
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from enum import Enum, auto
from hashlib import sha1
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Self, TypeAlias

__version__: str | None
__version_tuple__: tuple[int | str, ...] | None
try:
    from ._version import __version__
except ImportError:
    __version__ = None
    __version_tuple__ = None


TOML_ro: TypeAlias = int | float | str | None | list['TOML_ro'] | dict[str, 'TOML_ro']


# def _getenv__xdg_config_home() -> Path:
#     result = os.environ.get("XDG_DATA_HOME")
#     return (
#         Path.home().joinpath(".local/share")
#         if result is None
#         else Path(result)
#     )


# def _getenv__xdg_data_home() -> Path:
#     result = os.environ.get("XDG_DATA_HOME")
#     return (
#         Path.home().joinpath(".local/share")
#         if result is None
#         else Path(result)
#     )


def _getenv__xdg_state_home() -> Path:
    result = os.environ.get("XDG_STATE_HOME")
    return (
        Path.home().joinpath(".local/state")
        if result is None
        else Path(result)
    )


# def _getenv__pph_home() -> Path:
#     result = os.environ.get("PPH_HOME")
#     return (
#         _getenv__xdg_data_home().joinpath("python-project-helper")
#         if result is None
#         else Path(result)
#     )


class InvalidSettings(ValueError):
    def __init__(self, field: dataclasses.Field, message: str) -> None:
        self.field = field
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.field!r}, {self.message!r})"

    def __str__(self) -> str:
        return f"ERROR, invalid settings! {self.message}"


class UserError(ValueError):
    pass

# class OutputFormat(Enum):
#     simple = auto()
#     json = auto()
#     
#     @classmethod
#     def choices(cls) -> Sequence[str]:
#         return [val._name_ for val in cls]


class JSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Path):
            return str(obj.resolve())
        return super().default(obj)


@dataclasses.dataclass
class Settings:
    # pph_home: Path
    project_root: Path
    envs: Sequence[Mapping[str, TOML_ro]]
    # output_format: OutputFormat

    def validate(self) -> None:
        if not self.project_root.exists():
            raise InvalidSettings(f"Project root directory does not exist: {self.project_root}")

    def get_project_id(self) -> Path:
        return sha1(bytes(self.project_root)).hexdigest()

    def get_venv_dir(self, name: str) -> Path:
        return _getenv__xdg_state_home().joinpath(
            "python-project-helper", "projects", self.get_project_id(), "envs", name
        )

    _format_spec_pattern = re.compile(r"^json(?::(?P<indent>\d*))?$")

    def __format__(self, format_spec: str) -> str:
        match = self._format_spec_pattern.search(format_spec or "json")
        if match is None:
            raise ValueError("Invalid format_spec: {spec!r}")

        indent_str = match.group("indent")
        indent = int(indent_str) if indent_str else None

        return json.dumps(dataclasses.asdict(self), cls=JSONEncoder, indent=indent)



@dataclasses.dataclass
class CmdBase(ABC):
    settings: Settings

    @abstractmethod
    def run(self) -> int | None:
        ...


@dataclasses.dataclass
class Cmd_Project_Inspect(CmdBase):
    def run(self) -> None:
        print(format(self.settings, "json:2"))
        return None

@dataclasses.dataclass
class Cmd_Env_Create(CmdBase):
    name: str

    def run(self) -> None:
        # TODO: Use a class instead of a dict
        try:
            project_env: Mapping[str, TOML_ro] = self.settings.envs[self.name]
        except KeyError:
            raise UserError(f"Not a project environment: {self.name!r}")

        extras: Sequence[str] = project_env.get("extras", [])
        if not isinstance(extras, Sequence) and not all(isinstance(e, str) for e in extras):
            raise UserError(f"Invalid env.extras: {extras!r}")

        # Create venv

        venv_dir = self.settings.get_venv_dir(self.name)
        print(f"Creating environment: {venv_dir}")

        print(f"{sys.executable} -m venv {venv_dir}")
        builder = venv.EnvBuilder(
            # TODO: Is there ever a reason not to use this?
            # We can add a separate "update" command that doesn't clear.
            clear=True,
            symlinks=os.name != "nt",  # https://github.com/python/cpython/blob/0fb18b02c8ad56299d6a2910be0bab8ad601ef24/Lib/venv/__init__.py#L491-L494
            upgrade=False,
            with_pip=True,
            upgrade_deps=True,
        )
        builder.create(venv_dir)
        context = builder.ensure_directories(venv_dir)  # There's no other way to get this!
        venv_python: str = context.env_exec_cmd

        # Install

        # If this fails, we don't need to delete the environemtn, we cause we use
        # `clear=True`, so the next (successful) run will discard the failed artifacts.

        this = "."
        if extras:
            this += "[ " + ",".join(extras) + " ]"
        # TODO: Support passing extra Pip options from Pyproject, CLI flags, and/or env var
        cmd = [venv_python, "-m", "pip", "install", "--editable", this]
        print(shlex.join(cmd))
        sys.stdout.flush()
        subprocess.run(cmd)


@dataclasses.dataclass
class Cmd_Env_Delete(CmdBase):
    name: str

    def run(self) -> None:
        venv_dir = self.settings.get_venv_dir(self.name)
        print(f"Deleting environment: {venv_dir}")

        shutil.rmtree(venv_dir)


main_parser = argparse.ArgumentParser()
main_parser.add_argument("--version", action="version", version=f"Python Project Helper {__version__ or '<unknown>'}")
# main_parser.add_argument("--output", default=OutputFormat.simple, choices=OutputFormat.choices())
main_subparsers = main_parser.add_subparsers(title="subcommands")

env_parser = main_subparsers.add_parser("env")
env_subparsers = env_parser.add_subparsers(title="subcommands")

env_create_parser = env_subparsers.add_parser("create")
env_create_parser.set_defaults(cls=Cmd_Env_Create)
env_create_parser.add_argument("name", help="Environment name.")

env_delete_parser = env_subparsers.add_parser("delete")
env_delete_parser.set_defaults(cls=Cmd_Env_Delete)
env_delete_parser.add_argument("name", help="Environment name.")

project_parser = main_subparsers.add_parser("project")
project_subparsers = project_parser.add_subparsers(title="subcommands")

project_inspect_parser = project_subparsers.add_parser("inspect")
project_inspect_parser.set_defaults(cls=Cmd_Project_Inspect)


def find_pyproject() -> Path | None:
    fs_root = Path(os.sep)
    pwd = Path().resolve()
    result: Path | None = None
    while result is None:
        candidate = pwd.joinpath("pyproject.toml")
        if candidate.exists():
            # # TODO: Do we actually want this?
            # if candidate.is_symlink():
            #     candidate = pyproject_maybe.readlink()
            if candidate.is_file():
                result = candidate
        pwd = pwd.parent
    return result


def error(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def main() -> int | None:

    args = main_parser.parse_args()

    pyproject_file = find_pyproject()
    if pyproject_file is None:
        error("Could not find any pyproject.toml file!")
        return 1

    with pyproject_file.open("rb") as fp:
        pyproject_data: dict[str, TOML_ro] = tomllib.load(fp)

    pph_envs = pyproject_data.get("tool", {}).get("pph", {}).get("env", {"default": {}})

    settings = Settings(
        project_root=pyproject_file.parent,
        envs = pph_envs,
        # output_format=...,
    )

    retval = None

    cls: CmdBase = getattr(args, "cls", None)
    if cls:
        del args.cls
        cmd = cls(settings=settings, **args.__dict__)
        try:
            cmd.run()
        except UserError as exc:
            print(exc)
            retval = 1
    else:
        main_parser.parse_args(sys.argv[1:] + ["--help"])

    return retval

