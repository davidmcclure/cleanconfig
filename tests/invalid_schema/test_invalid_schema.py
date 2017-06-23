

import pytest
import os

from cleanconfig import CleanConfig
from voluptuous import Schema, Required
from voluptuous.error import MultipleInvalid

from tests.utils import fixture_path


class Config(CleanConfig):

    name = 'project'

    config_dirs = [
        fixture_path(__file__),
    ]

    schema = Schema({
        Required('key'): int,
    })


def test_single_dir():
    with pytest.raises(MultipleInvalid):
        Config.read()
