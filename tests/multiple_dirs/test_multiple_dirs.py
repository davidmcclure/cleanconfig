

import os

from cleanconfig import CleanConfig
from voluptuous import Schema, Required

from tests.utils import fixture_path


class Config(CleanConfig):

    name = 'project'

    config_dirs = [
        fixture_path(__file__, 'dir1'),
        fixture_path(__file__, 'dir2'),
    ]

    schema = Schema({
        Required('key'): str,
    })


def test_multiple_dirs():
    config = Config.read()
    assert config['key'] == 'val2'
