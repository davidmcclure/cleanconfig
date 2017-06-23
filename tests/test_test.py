

import os

from cleanconfig import CleanConfig
from voluptuous import Schema, Required


class Config(CleanConfig):

    name = 'project'

    config_dirs = [os.path.dirname(__file__)]

    schema = Schema({
        Required('key1'): str,
        Required('key2'): int,
    })


def test_read_config():

    config = Config.read()

    assert config['key1'] == 'one'
    assert config['key2'] == 2
