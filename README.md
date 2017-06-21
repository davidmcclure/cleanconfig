
# SimpleConfig

SimpleConfig is a confiuration base class for Python projects that tries to be simple, flexible, and just opinionated enough. The point of SimpleConfig is really the conventions that it enforces, not the code itself (which is minimal, just about 70 lines).

Though this can be used in any project, it was originally abstracted out of a series of data wrangling projects at the Stanford Literary Lab and the Open Syllabus Project, many of them using MPI or Spark. Since there aren't really "frameworks" for these types of projects that enforce specific configuration conventions, I found myself writing slightly different versions of the same bespoke `Config` class over and over again. SimpleConfig merges all of these together.

## Usage

**Problem**: You need to read configuration files from a hierarchy of directories and merge together a single configuration dictionary. For example, you might want to put a default config file under source control alongside the application code. But, during development, you might want to put some local overrides in `~/.myproject`. And, when you deploy the code to a Spark cluster on EC2, you might want to deploy config files to `/etc/myproject`.

**Solution**: Inherit from SimpleConfig and provide:

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

---


These projects tend to take take place outside of frameworks like Django or Flask, which have well-established patterns for managing configuration. And, writing tests for these types of projects can get a bit weird, and can call for some configuration management patterns that are a bit more advanced than just parsing a YAML file into a dictionary.

simpleconfig assumes:

- **YAML** - Config values are stored as YAML files, which get loaded by the excellent anyconfig module. (SimpeConfig is basically just a wrapper around anyconfig.)

- **Merge files from different directories** - Config files need to get read from a hierarchy of directories. For example, a project might store a default config file in git alongside the application code. But, during development, you might want to put some local overrides in `~/.myproject`. And, when you run a job on a compute cluster, you might want to deploy config files to `/etc/myproject`.

- **Schemas** - Since it's easy to end up with config file that are out-of-date or incomplete, keys and values read from files should be validated against a schema in the code, which is always the canonical reference for what config values the project can use.

- environments - Sometimes config values need to be selectively changed based on

- lock files - sometimes, in tests, it's necesary to "lock" certain values into
  the configuration by way of the file system. eg, if you're integration testing
  an MPI program, and need to update a



The point of SimpleConfig is as much the conventions that it enforces as the code itself (which is minimal, just about 70 lines).

