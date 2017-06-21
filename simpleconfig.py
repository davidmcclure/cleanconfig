

import os
import anyconfig
import yaml

from voluptuous import Schema, Required


class SimpleConfig(dict):

    slug = 'config'

    config_dirs = ['/etc']

    lock_dir = '/tmp'

    schema = Schema({})

    @classmethod
    def _lock_path(cls):
        """Form the lock file path.

        Returns: str
        """
        return os.path.join(cls.lock_dir, '%s.lock.yml' % cls.slug)

    @classmethod
    def read(cls):
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

        paths.append(cls._lock_path())

        return cls(paths)

    def __init__(self, paths):
        """Read config files, validate schema, build dictionary.

        Args:
            paths (str): Config paths, from lowest to highest priority.
        """
        config = anyconfig.load(paths, ignore_missing=True)

        return super().__init__(self.schema(config))

    def lock(self):
        """Dump current values into lock file.
        """
        with open(self._lock_path(), 'w') as fh:
            fh.write(yaml.dump(dict(self)))

    def unlock(self):
        """Clear the /tmp file.
        """
        os.remove(self._lock_path())


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
