

import os

from cleanconfig import CleanConfig
from voluptuous import Schema, Required

from tests.utils import fixture_path


class Config(CleanConfig):

    name = 'project'

    config_dirs = [
        fixture_path(__file__, 'dir1'),
        fixture_path(__file__, 'dir2'),
        fixture_path(__file__, 'dir3'),
    ]

    schema = Schema({
        Required('key1'): int,
        Required('key2'): int,
        Required('key3'): int,
    })


def test_multiple_dirs():

    config = Config.read()

    assert config['key1'] == 1
    assert config['key2'] == 2
    assert config['key3'] == 3
