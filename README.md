
```
███████╗██╗███╗   ███╗██████╗ ██╗     ███████╗ ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗
██╔════╝██║████╗ ████║██╔══██╗██║     ██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝
███████╗██║██╔████╔██║██████╔╝██║     █████╗  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
╚════██║██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
███████║██║██║ ╚═╝ ██║██║     ███████╗███████╗╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
╚══════╝╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝
```

SimpleConfig is confiuration system for Python projects that tries to be simple, flexible, and just opinionated enough. The point of SimpleConfig is mostly the conventions that it enforces, not the code itself, which is tiny.

SimpleConfig was originally abstracted out of a series of data wrangling projects at the Stanford Literary Lab and the Open Syllabus Project, many of them using MPI or Spark to run compute jobs on large clusters. Since there aren't really "frameworks" that enforce specific conventions for these types of projects - and since they can sometimes have weird, tricky requirements vis-a-vis configuration - I found myself writing bespoke `Config` classes over and over again. SimpleConfig picks out the best ideas from all of these.

SimpleConfig might be a good fit it:

- You're working outside the context of a framework like Django that have built-in configuration conventions, and don't want to reinvent the wheel. If you're in Django - just use `settings.py`.

- You want to be able to easily add "business logic" to config values. Eg - you might want to encapsulate the logic needed to convert some database connection parameters into an actual connection instance.

- You need to be able to selectively override config values in fine-grained, complex ways. SimpleConfig has robust support for arbitrary environments (`test`, `dev`, `prod`, etc), and also makes it possible to temporarily change values and "lock" them to the file system so that they get picked up by other processes.

## Basic Usage

Inherit from `SimpleConfig` and provide:

- `name` - A string used to automatically build file paths and ENV variables. For example, if this is `myproject`, then SimpleConfig will assume that all config files for this class will be called `myproject.yml`.

- `config_dirs` - A list of directories where SimpleConfig will looks for config files, from lowest to highest priority.

- `schema` - A [Voluptuous](https://github.com/alecthomas/voluptuous) schema that specifies the structure of the final dictionary that should get parsed out of the config files. This serves as a canonical reference for what config values the project can use, and ensures that errors in incomplete / out-of-date config files get raised in an explicit way.

```python
from simpleconfig import SimpleConfig
from voluptuous import Schema, Required

class Config(SimpleConfig):

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

In this case, per `config_files`, SimpleConfig will first look for a file called `myproject.yml` in the same directory as the Python file that contains the class, then in `~/.myproject`, and then in `/etc/myproject`.

To match the schema, the config files would look like:

```yaml
key1: val1
key2: val2

outer:
  inner: val3
```

(Or, at least, keys + values in all the files have to collectively merge together into that structure. Theoretically you could have `key1` in one file and `key2` in another, if you so wish.)

Then, use the `.read()` classmethod to parse the files and build the merged dictionary:

```python
config = Config.read()
```

`SimpleConfig` inherits from `dict`, so values can be looked up just like on regular dictionaries:

```python
config['key1']
>> val1

config['outer']['inner']
>> val3
```

## Environments

Often, you need to change config values based on an "environment" - `test`, `dev`, `prod`, etc. When SimpleConfig loads files, it will automatically try to read an environment from an ENV variable named `{uppercase name}_ENV`. For example, in this case, since `name` is `myproject`, SimpleConfig will look up the value of `MYPROJECT_ENV`. If this is defined, files with names like `{name}.{env}.yml` will be loaded immediately after the "default" file in each directory, so that the ENV-specific values take precedence. In this case, if `MYPROJECT_ENV=test`, then SimpleConfig will load:

- `[Directory of Python file]/myproject.yml`
- `[Directory of Python file]/myproject.test.yml`
- `~/.myproject/myproject.yml`
- `~/.myproject/myproject.test.yml`
- `/etc/myproject/myproject.yml`
- `/etc/myproject/myproject.test.yml`

(If a file is missing, SimpleConfig just ignores it and moves on.)

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

And then, depending on the tooling, the test suite can often be configured to automatically set the ENV variable. For example, using `pytest` along with the [`pytest-env`](https://github.com/MobileDynasty/pytest-env) package, you could create a `pytest.ini` with:

```ini
[pytest]

env =
  MYPROJECT_ENV=test
```

And then, whenver code runs under `pytest`, SimpleConfig will automatically read from the `.test.yml` files.

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
from simpleconfig import SimpleConfig
from voluptuous import Schema, Required

class Config(SimpleConfig):

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

class Config(SimpleConfig):

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

class Config(SimpleConfig):

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

## Lock files

## FAQ

- Why not settings.py?
- Where, and how often, should I read the configuration?
