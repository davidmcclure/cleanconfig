

import os
import pytest

from cleanconfig import CleanConfig
from voluptuous import Schema, Required

from tests.utils import fixture_path


class Config(CleanConfig):

    name = 'project'

    config_dirs = [
        fixture_path(__file__, 'dir1'),
    ]

    schema = Schema({
        Required('key'): int,
    })


@pytest.mark.parametrize('dirs,val', [
    ([], 1),
    (['dir2'], 2),
    (['dir2', 'dir3'], 3),
])
def test_multiple_dirs(monkeypatch, dirs, val):

    config_dirs = map(lambda d: fixture_path(__file__, d), dirs)

    monkeypatch.setenv('PROJECT_CONFIG_DIRS', ','.join(config_dirs))
    config = Config.read()

    assert config['key'] == val
