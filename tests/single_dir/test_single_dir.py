

import os

from cleanconfig import CleanConfig
from voluptuous import Schema, Required

from tests.utils import fixture_path


class Config(CleanConfig):

    name = 'project'

    config_dirs = [
        fixture_path(__file__),
    ]

    schema = Schema({
        Required('key1'): str,
        Required('key2'): int,
    })


def test_single_dir():

    config = Config.read()

    assert config['key1'] == 'one'
    assert config['key2'] == 2
