def set_global_config(parser):
    parser.add_argument('--global_config1')
    parser.add_argument('--global_config2')
    return parser


def set_args(parser):
    parser.add_argument('main_arg1')
    parser.add_argument('main_arg2')


def set_config(parser):
    parser.add_argument('--main_config1')
    parser.add_argument('--main_config2', '-m')
