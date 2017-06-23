

import os


def fixture_path(test_file, subdir=None):
    """Form a fixture config dir path.

    Args:
        test_file (str): Test file path.
        subdir (str): Name of subdirectory.

    Returns: str
    """
    base = os.path.dirname(test_file)

    return os.path.join(base, subdir) if subdir else base
