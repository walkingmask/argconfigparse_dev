from pathlib import Path

from argconfigparse.parse import cli_parse, CLIParser, config_parse
from argconfigparse import subcommand1, subcommand2

print(cli_parse())

parser = CLIParser()
parser.register(subcommand1)
parser.register(subcommand2)
print(parser.parse())

print(config_parse(
        'subcommand1', Path(__file__).absolute().parent/'config.json'))
