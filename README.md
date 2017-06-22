
# SimpleConfig

SimpleConfig is confiuration system for Python projects that tries to be simple, flexible, and just opinionated enough. The point of SimpleConfig is mostly the conventions that it enforces, not the code itself - which is minimal, just about 100 lines.

Though it can be used in any project, SimpleConfig was originally abstracted out of a series of data wrangling projects at the Stanford Literary Lab and the Open Syllabus Project, many of them using MPI or Spark. Since there aren't really "frameworks" for these types of projects that enforce specific configuration conventions, I found myself writing slightly different versions of the same bespoke `Config` class over and over again. SimpleConfig merges all of these together.

Under the hood, SimpleConfig uses the excellent [anyconfig](https://github.com/ssato/python-anyconfig) package to do the core work of reading and merging config files.

## Basic Usage

Inherit from `SimpleConfig` and provide:

- `slug` - A string used to automatically build file paths and ENV variables.
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
