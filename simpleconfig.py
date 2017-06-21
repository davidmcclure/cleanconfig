

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
    def _env_var(cls, suffix):
        """Form an ENV variable from the slug.

        Returns: str
        """
        return '%s_%s' % (cls.slug.upper(), suffix)

    @classmethod
    def _yml_path(cls, config_dir):
        """Given a config dir, form a file path:
        {slug}.yml

        Returns: str
        """
        return os.path.join(config_dir, '%s.yml' % cls.slug)

    @classmethod
    def _env_yml_path(cls, config_dir, env):
        """Given a config dir + env, form a file path:
        {slug}.{env}.yml

        Returns: str
        """
        return os.path.join(config_dir, '%s.%s.yml' % (cls.slug, env))

    @classmethod
    def _lock_yml_path(cls):
        """Form the lock file path.

        Returns: str
        """
        return os.path.join(cls.lock_dir, '%s.lock.yml' % cls.slug)

    @classmethod
    def paths(cls):
        """Build the complete path list.

        Returns: list of str
        """
        env = os.environ.get(cls._env_var('ENV'))

        paths = []
        for d in cls.config_dirs:

            # {slug}.yml
            paths.append(cls._yml_path(d))

            # {slug}.{env}.yml
            if env:
                paths.append(cls._env_yml_path(d, env))

        paths.append(cls._lock_yml_path())

        return paths

    @classmethod
    def read(cls):
        """Get a config instance with the default files.

        Returns: cls
        """
        return cls(cls.paths())

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
