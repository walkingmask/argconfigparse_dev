def set_config(parser):
    parser.add_argument('--sub2_config1')
    parser.add_argument('--sub2_config2')


def set_args(parser):
    parser.add_argument('sub2_arg1')
    parser.add_argument('sub2_arg2')


def check_config(config):
    for required in ['sub2_config1']:
        if not getattr(config, required, None):
            raise ValueError("{name} require config {required}".format(
                name=__name__.split('.')[-1],
                required=required))


is_subcommand = True

__all__ = ['is_subcommand', 'set_config', 'set_args', 'check_config']
