

import pytest
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
        Required('key'): int,
    })


@pytest.mark.parametrize('env,val', [
    ('', 0),
    ('env1', 1),
    ('env2', 2),
])
def test_environment(monkeypatch, env, val):

    monkeypatch.setenv('PROJECT_ENV', env)
    config = Config.read()

    assert config['key'] == val
