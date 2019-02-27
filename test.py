from argconfigparse.parse import cli_parse, CLIParser
from argconfigparse import subcommand1, subcommand2

print(cli_parse())

parser = CLIParser()
parser.register(subcommand1)
parser.register(subcommand2)
print(parser.parse())
