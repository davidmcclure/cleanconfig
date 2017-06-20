

import os
import anyconfig

from voluptuous import Schema, Required


class SimpleConfig(dict):

    slug = 'config'

    config_dirs = []

    schema = Schema({})

    @classmethod
    def from_env(cls):
        """Get a config instance with the default files.
        """
        env = os.environ.get('%s_%s' % (cls.slug.upper(), 'ENV'))

        paths = []
        for d in cls.config_dirs:

            # {slug}.yml
            paths.append(os.path.join(d, '%s.yml' % cls.slug))

            # {slug}.{env}.yml
            if env:
                paths.append(os.path.join(d, '%s.%s.yml' % (cls.slug, env)))

        return cls(paths)

    def __init__(self, paths):
        """Read config files, validate schema, build dictionary.

        Args:
            paths (str): Config paths, from lowest to highest priority.
        """
        config = anyconfig.load(paths, ignore_missing=True)

        return super().__init__(self.schema(config))


# TODO|dev
class Config(SimpleConfig):

    slug = 'osp'

    config_dirs = [os.path.dirname(__file__), '~/.osp', '/etc/osp']

    schema = Schema({

        'buckets': {
            Required('v1_corpus'): str,
        },

    })
