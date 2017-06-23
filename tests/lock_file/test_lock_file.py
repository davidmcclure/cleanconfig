

import os

from subprocess import check_output

from cleanconfig import CleanConfig
from voluptuous import Schema, Required

from tests.utils import fixture_path


class Config(CleanConfig):

    name = 'project'

    config_dirs = [
        fixture_path(__file__),
    ]

    schema = Schema({
        Required('key'): int,
    })


def test_lock_file():

    config = Config.read()
    config['key'] = 2

    config.lock()
    res = check_output([fixture_path(__file__, 'program.py')])
    config.unlock()

    assert res.decode().strip() == '2'
