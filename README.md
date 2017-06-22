
```
███████╗██╗███╗   ███╗██████╗ ██╗     ███████╗ ██████╗ ██████╗ ███╗   ██╗███████╗██╗ ██████╗
██╔════╝██║████╗ ████║██╔══██╗██║     ██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔════╝
███████╗██║██╔████╔██║██████╔╝██║     █████╗  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██║  ███╗
╚════██║██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██║   ██║
███████║██║██║ ╚═╝ ██║██║     ███████╗███████╗╚██████╗╚██████╔╝██║ ╚████║██║     ██║╚██████╔╝
╚══════╝╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝
```

SimpleConfig is confiuration system for Python projects that tries to be simple, flexible, and just opinionated enough. The point of SimpleConfig is mostly the conventions that it enforces, not the code itself, which is minimal.

SimpleConfig was originally abstracted out of a series of data wrangling projects at the Stanford Literary Lab and the Open Syllabus Project, many of them using MPI or Spark to run compute jobs on large clusters. Since there aren't really "frameworks" that enforce specific conventions for these types of projects - and since they can sometimes have weird, tricky requirements vis-a-vis configuration - I found myself writing slightly different versions of the same bespoke `Config` class over and over again. SimpleConfig merges all of these together.

Under the hood, SimpleConfig uses the excellent [anyconfig](https://github.com/ssato/python-anyconfig) package to do the core work of reading and merging config files.


And since these projects can sometimes have sort of weird, tricky requirements vis-a-vis configuration

## Basic Usage

Inherit from `SimpleConfig` and provide:

- `slug` - A string used to automatically build file paths and ENV variables. For example, if this is `myproject`, then SimpleConfig will assume that all config files for this class will be called `myproject.yml`.

- `config_dirs` - A list of directories where SimpleConfig will looks for config files, from lowest to highest priority.

- `schema` - A [Voluptuous](https://github.com/alecthomas/voluptuous) schema that specifies the structure of the final dictionary that should get parsed out of the config files. This serves as a canonical reference for what config values the project can use, and ensures that errors in incomplete / out-of-date config files get raised in an explicit way.

```python
from simpleconfig import SimpleConfig
from voluptuous import Schema, Required

class Config(SimpleConfig):

    slug = 'myproject'

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

In this case, since `config_files` starts with `os.path.dirname(__file__)`, SimpleConfig will first look for a file called `myproject.yml` in the same directory as the Python file that contains the class, then in `~/.myproject`, and then in `/etc/myproject`.

Per the schema, the config files would look like:

```yaml
key1: val1
key2: val2

outer:
  inner: val3
```

(Or, at least, keys + values in all the files have to collectively merge together into that structure. Theoretically you could have `key1` in one file, `key2` in another, etc., if you so wish.)

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

Often, you need to change config values based on an "environment" - `test`, `dev`, `prod`, etc. When SimpleConfig loads files, it will automatically try to read an environment from an ENV variable named `{uppercase slug}_ENV`. For example, in this case, since `slug` is `myproject`, SimpleConfig will look up the value of `MYPROJECT_ENV`. If this is defined, files with names like `{slug}.{env}.yml` will be loaded immediately after the "default" file in the directory, so that the ENV-specific values take precedence. In this case, if `MYPROJECT_ENV=test`, then SimpleConfig will try to load:

- `[Directory of Python file]/myproject.yml`
- `[Directory of Python file]/myproject.test.yml`
- `~/.myproject/myproject.yml`
- `~/.myproject/myproject.test.yml`
- `/etc/myproject/myproject.yml`
- `/etc/myproject/myproject.test.yml`

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

## Lock files

## Extra config directories
