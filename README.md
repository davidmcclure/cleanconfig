
# CleanConfig

CleanConfig is confiuration system for Python projects that tries to be simple, flexible, and just opinionated enough. The point of CleanConfig is mostly the conventions that it enforces, not the code itself, which is tiny.

CleanConfig was originally abstracted out of a series of data engineering projects at the [Stanford Literary Lab](http://litlab.stanford.edu/) and the [Open Syllabus Project](http://explorer.opensyllabusproject.org/), many of them using MPI or Spark to run compute jobs on large clusters. Since there aren't really "frameworks" that enforce specific conventions for these types of projects - and since they can sometimes have sort of weird, tricky requirements - I found myself writing custom `Config` classes over and over again. CleanConfig combines the stuff that worked from these projects.

CleanConfig might be a good fit it:

- You want to explicitly define and validate the format of the config object.

- You're working outside the context of a framework like Django that have built-in configuration conventions, and don't want to reinvent the wheel. If you're in Django - just use `settings.py`.

- You want to be able to easily add "business logic" to config values, in the way that you might add methods to a database model. Eg - you might want to encapsulate the logic needed to convert some database connection parameters into an actual connection instance.

- You need to be able to override config values in fine-grained, complex ways. CleanConfig has robust support for arbitrary environments (`test`, `dev`, `prod`, etc), and also makes it possible to temporarily change values and "lock" them to the file system so that they get picked up by other processes.

- You deploy projects automation with frameworks like [Ansible](https://www.ansible.com/) and want an easy way to patch in configuration values at deploy-time, without using weird Python import tricks.

## Basic Usage

Inherit from `CleanConfig` and provide:

- `name` - A string used to automatically build file paths and ENV variables. For example, if this is `myproject`, then CleanConfig will assume that all config files for this class will be called `myproject.yml`.

- `config_dirs` - A list of directories where CleanConfig will looks for config files, from lowest to highest priority.

- `schema` - A [Voluptuous](https://github.com/alecthomas/voluptuous) schema that specifies the structure of the final dictionary that should get parsed out of the config files. This serves as a canonical reference for what config values the project can use, and ensures that errors in config files get surfaced in an explicit way.

```python
from cleanconfig import CleanConfig
from voluptuous import Schema, Required

class Config(CleanConfig):

    name = 'myproject'

    config_dirs = [
        os.path.dirname(__file__),
        '~/.myproject',
        '/etc/myproject',
    ]

    schema = Schema({

        Required('key1'): str,
        Required('key2'): str,

        'outer': {
          Required('inner'): str,
        }

    })
```

In this case, per `config_files`, CleanConfig will first look for a file called `myproject.yml` in the same directory as the Python file that contains the class, then in `~/.myproject`, and then in `/etc/myproject`.

To match the schema, the config file would look like:

```yaml
key1: val1
key2: val2

outer:
  inner: val3
```

(Or, at least, keys + values in all the files have to collectively merge together into that structure. Theoretically you could have `key1` in one file and `key2` in another, if you wanted.)

Then, use the `.read()` classmethod to parse the files and build the merged dictionary:

```python
config = Config.read()
```

`CleanConfig` inherits from `dict`, so values can be looked up just like on regular dictionaries:

```python
config['key1']
>> val1

config['outer']['inner']
>> val3
```

## Environments

Often, you need to change config values based on an "environment" - `test`, `dev`, `prod`, etc. When CleanConfig loads files, it will automatically try to read an environment from an ENV variable named `{uppercase name}_ENV`. For example, in this case, since `name` is `myproject`, CleanConfig will look up the value of `MYPROJECT_ENV`. If this is defined, files with names like `{name}.{env}.yml` will be loaded immediately after the "default" file in each directory, so that the ENV-specific values take precedence. In this case, if `MYPROJECT_ENV=test`, then CleanConfig will load:

- `[Directory of Python file]/myproject.yml`
- `[Directory of Python file]/myproject.test.yml`
- `~/.myproject/myproject.yml`
- `~/.myproject/myproject.test.yml`
- `/etc/myproject/myproject.yml`
- `/etc/myproject/myproject.test.yml`

(If a file is missing, CleanConfig just ignores it and moves on.)

So, if `/etc/myproject/myproject.test.yml` contains:

```yaml
outer:
  inner: override
```

Then, when `MYPROJECT_ENV=test`, this key will be overridden:

```python
config['outer']['inner']
>> override
```

This makes it easy to automatically patch in global configuration changes in certain contexts - for example, when tests are running. For instance, say the default `myproject.yml` config looks like:

```yaml
database: /var/myproject.db
```

Then a `myproject.test.yaml` file could clobber this key:

```yaml
database: /tmp/myproject.db
```

And then, depending on the tooling, the test suite can often be configured to automatically set the ENV variable. For example, using [pytest](https://docs.pytest.org/en/latest/) along with the [pytest-env](https://github.com/MobileDynasty/pytest-env) package, you could create a `pytest.ini` with:

```ini
[pytest]

env =
  MYPROJECT_ENV=test
```

And then, whenver code runs under `pytest`, CleanConfig will automatically read from the `.test.yml` files.

## Business logic

Presumably, you want to do something with the config values. This often involves piping them into Python class instances. For example, say your project uses Redis. In a config file, you might have:

```yaml
redis:
  host: localhost
  port: 6379
  db: 0
```

And a config class like:

```python
from cleanconfig import CleanConfig
from voluptuous import Schema, Required

class Config(CleanConfig):

    ...

    schema = Schema({
        'redis': {
            Required('host'): str,
            Required('port'): int,
            Required('db'): int,
        }
    })
```

But where to put the code that actually spins up the Redis connection object? One approach is to just encapsulate this inside of the config class itself:

```python
from redis import StrictRedis

class Config(CleanConfig):

    ...

    def redis_conn(self):
        """Build a Redis connection from config parameters."""
        return StrictRedis(**self['redis'])
```

This way, the config class "owns" the whole process of getting configuration constants for Redis and providing a live connection instance to the application:

```python
config = Config.read()
redis_conn = config.redis_conn()
redis_conn.get('foo')
```

Even better - in many cases, it makes sense for these connection instances to be application globals, essentially. One nice pattern is to use the [`cached_property`](https://github.com/pydanny/cached-property) library to store a shared instance on the config class:

```python
from redis import StrictRedis
from cached_property import cached_property

class Config(CleanConfig):

    ...

    @cached_property
    def redis_conn(self):
        """Build a Redis connection from config parameters."""
        return StrictRedis(**self['redis'])
```

This avoids unnecessarily spinning up multiple connections, and also means that the instance can be looked up directly as a property on the class:

```python
config = Config.read()
config.redis_conn.get('foo')
```

## Extra config directories

Sometimes, you need to specify an extra directory for configuration files, but it doesn't make sense to hardcode it into the class definition. For example, if you're deploying a project with something like Ansible, it might make more sense for the location of the config directory to be controlled by the automation framework, not the Python source code.

To make this easy, CleanConfig will automatically read a comma-delimited list of additional config directories from a `{SLUG}_CONFIG_DIRS` environment variable. For example, if `config_dirs` looks like this:

```python
class Config(CleanConfig):

    name = 'myproject'

    config_dirs = ['~/.myproject']
```

And `MYPROJECT_CONFIG_DIRS` is set:

`MYPROJECT_CONFIG_DIRS=/etc/myproject,/share/user/config/myproject`

Then CleanConfig will append these directories to the list provided by the class. So, the final directory hierarchy would be:

- ~/.myproject
- /etc/myproject
- /share/user/config/myproject

## Lock files

Ok, this is a bit more obscure, but indulge me - now and then there are situations where you want to change a config value and "communicate" the change to another process, usually in the context of testing.

It's often enough just to use a `test` environment, but sometimes it's necessary to swap config values on a per-test basis. For example, imagine you're testing an MPI executable that, internally, uses config values. By default, say the value of `config['key']` is `1`, and you want to do something like this:

```python
from subprocess import call

config['key'] = 5
call(['mpirun', 'bin/program.py'])

# assert something that changes based on the value of `key`
```

This won't work, though, because, since `call` spawns off a fresh Python interpreter, `config['key']` will be `1` inside of `bin/program.py`, not `5`. To get around this, CleanConfig makes it possible to temporarily "lock" the current state of a configuration object to the filesystem:

```python
config['key'] = 5

config.lock()
call(['mpirun', 'bin/program.py'])
config.unlock()
```

When `.lock()` is called, CleanConfig dumps the current config dictionary as a YAML file to `/tmp/{slug}.yml` (the root directory for the lock file can be overridden with the `lock_dir` class property). And, whenever CleanConfig reads config files, it automatically appends this directory as the last, highest-priority directory, so the locked values are always guaranteed to make it through to the final config object.

This could also be accomplished by turning the executable into a fully-fledged CLI program that takes arguments / flags, maybe with something like [click](http://click.pocoo.org/). But, if you don't ever intend to actually use it as a CLI program, it can feel sort of janky to bolt on the argument parsing just for the purpose of the tests suite - this can be a cleaner way.

Be careful with this, though, since it can become sort of a footgun if not used properly. Eg, if you forget to call `.unlock()`, you'll end up with a marooned lock file in `/tmp`, which could produce confusing behavior.

## Patterns

- **Where, and how often, should I read the configuration?** As a rule of thumb, it's usually best just to use a global singleton, since it's wasteful to re-parse the config files over and over again. For example, if you've got a module called `myproject`, the directory layout might look like:

  ```
  myproject
  ├── __init__.py
  ├── config.py
  └── myproject.yml
  ```

  Where `config.py` contains the config class definition and `myproject.yml` is a generic config file that ships with the project. Then, the config object can live in `__init__.py`:

  ```python
  from myproject.config import Config

  config = Config.read()
  ```

  And then, elsewhere in the project, you can do:

  ```python
  from myproject import config

  # Use config..
  ```
