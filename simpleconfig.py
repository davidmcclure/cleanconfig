

import os
import anyconfig

from voluptuous import Schema, Required


class SimpleConfig(dict):

    slug = 'config'

    config_dirs = []

    schema = Schema({})

    _instance = None

    @classmethod
    def from_env(cls):
        """Get a config instance with the default files.

        Returns: cls
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

    @classmethod
    def get(cls):
        """Provide a cached instance.

        Returns: cls
        """
        if not cls._instance:
            cls._instance = cls.from_env()

        return cls._instance

    @classmethod
    def reset(cls):
        """Clear the cached instance.
        """
        del cls._instance

    def __init__(self, paths):
        """Read config files, validate schema, build dictionary.

        Args:
            paths (str): Config paths, from lowest to highest priority.
        """
        config = anyconfig.load(paths, ignore_missing=True)

        return super().__init__(self.schema(config))


# TODO|dev
class Config1(SimpleConfig):

    slug = 'c1'

    config_dirs = [os.path.dirname(__file__), '~/.osp', '/etc/osp']

    schema = Schema({
        Required('key'): str,
    })


# TODO|dev
class Config2(SimpleConfig):

    slug = 'c2'

    config_dirs = [os.path.dirname(__file__), '~/.osp', '/etc/osp']

    schema = Schema({
        Required('key'): str,
    })
