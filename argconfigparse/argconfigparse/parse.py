import argparse
from copy import deepcopy
from importlib import import_module
import json
from pathlib import Path
from setuptools import find_packages
from types import SimpleNamespace


"""
command.__init__.py:
    set_args(parser)
    set_config(parser)
    set_global_config(parser)
subcommand.__init__.py
    is_command = True
    set_args(parser)
    set_config(parser)
"""


def get_subcommands():
    command = import_module(__name__.split('.')[0])
    command_root = Path(command.__file__).parent.parent
    packages = find_packages(command_root)
    subcommands = []
    for package in packages:
        package = import_module(package)
        if hasattr(package, 'is_subcommand'):
            subcommands.append(package)
    return subcommands


def set_args(command, parser):
    if hasattr(command, 'set_args'):
        command.set_args(parser)


def set_config(command, parser):
    if hasattr(command, 'set_config'):
        command.set_config(parser)


def get_config(command):
    parser = argparse.ArgumentParser()
    set_config(command, parser)
    return parser.parse_args()


def set_global_config(command, parser):
    if hasattr(command, 'set_global_config'):
        command.set_global_config(parser)


def get_global_config(command):
    parser = argparse.ArgumentParser()
    set_global_config(command, parser)
    return parser.parse_args()


def get_subcommand_parser(parser, subcommand_name):
    for arg in parser._get_positional_actions():
        if arg.dest == 'subcommand':
            return arg.choices[subcommand_name]


def load_config(file_path, section):
    with open(file_path) as f:
        config_all = json.load(f)
    config = {}
    if 'main' in config_all:
        config.update(config_all['main'])
    if 'global' in config_all:
        config.update(config_all['global'])
    if section in config_all:
        config.update(config_all[section])
    return config


def override_argument_default(parser, arg, default):
    arg = vars(deepcopy(arg))
    arg['default'] = default
    option_strings = arg['option_strings']
    del arg['option_strings'], arg['container']
    parser.add_argument(*option_strings, **arg)


def set_file_config_as_default(parser, file_config, subcommand_name=None):
    for arg in parser._get_optional_actions():
        if arg.dest in ['help', 'config']: continue
        if arg.dest in file_config:
            new_default = file_config[arg.dest]
            override_argument_default(parser, arg, new_default)

    if subcommand_name:
        subcommand_parser = get_subcommand_parser(parser, subcommand_name)
        for arg in subcommand_parser._get_optional_actions():
            if arg.dest == 'help': continue
            if arg.dest in file_config:
                new_default = file_config[arg.dest]
                override_argument_default(subcommand_parser, arg, new_default)


def get_args(parser, cli_args, subcommand_name=None):
    args = {}
    for arg in parser._get_positional_actions():
        if arg.dest == 'subcommand': continue
        args[arg.dest] = getattr(cli_args, arg.dest)
        delattr(cli_args, arg.dest)

    subcommand_args = {}
    if subcommand_name:
        subcommand_parser = get_subcommand_parser(parser, subcommand_name)
        for arg in subcommand_parser._get_positional_actions():
            subcommand_args[arg.dest] = getattr(cli_args, arg.dest)
            delattr(cli_args, arg.dest)

    return SimpleNamespace(**args), SimpleNamespace(**subcommand_args)


def build_parser():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-c', '--config')
    command = import_module(__name__.split('.')[0])
    set_args(command, parser)
    set_config(command, parser)
    subcommand_parsers = parser.add_subparsers(dest='subcommand')
    subcommand_parsers.required = True
    for subcommand in get_subcommands():
        subcommand_parser = subcommand_parsers.add_parser(
            subcommand.__name__.split('.')[-1], conflict_handler='resolve')
        set_args(subcommand, subcommand_parser)
        set_config(subcommand, subcommand_parser)
        set_global_config(command, subcommand_parser)
    return parser


def cli_parse():
    parser = build_parser()
    cli_args = parser.parse_args()
    subcommand_name, config_file = cli_args.subcommand, cli_args.config

    if config_file:
        file_config = load_config(cli_args.config, cli_args.subcommand)
        set_file_config_as_default(parser, file_config, cli_args.subcommand)
        cli_args = parser.parse_args()

    args, subcommand_args = get_args(parser, cli_args, cli_args.subcommand)

    del cli_args.subcommand, cli_args.config
    config = cli_args

    return args, subcommand_name, subcommand_args, config, config_file
