
# SimpleConfig

A confiuration base class for Python projects that tries to be simple, flexible, and just opinionated enough. The point of SimpleConfig is really the conventions that it enforces, not the code itself (which is minimal, just about 70 lines).

Though this can be used in any project, it was originally abstracted out of a series of data wrangling projects at the Stanford Literary Lab and the Open Syllabus Project, many of them using MPI or Spark to run compute jobs on big data sets. There aren't really "frameworks" for these types of projects that enforce specific configuration conventions, I found myself writing slightly different versions of the same bespoke `Config` class over and over again. SimpleConfig merges all of these together.

## Basic Usage

Inherit from SimpleConfig and provide:

- `slug` - A string used to automatically build file paths and ENV variables.
- `config_dirs` - A list of directories where SimpleConfig will looks for config files, from lowest to highest priority.
- `schema` - A Voluptuous schema that specifies the structure of the final dictionary that should get parsed out of the config files. This serves as a canonical reference for what config values the project can use, and ensures that errors in incomplete / out-of-date config files get raised in an explicit way.

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
        Required('key2'): int,
    })
```

Then, use the `.read()` classmethod to parse the files and build the merged dictionary:

```python
config = Config.read()
```

Or, to get a cached singleton instance, use `.get()`:

```python
config = Config.get()
```

The first time this is called, SimpleConfig will read the files from disk and store the instance. Subsequent calls will just return this instance, without re-reading the source files.

# TODO
- environments (separate files, or YAML keys?)
- lock files
- tests
