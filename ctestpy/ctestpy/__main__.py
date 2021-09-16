import os
import sys
import logging

from ctestpy.test import TestSuite
from ctestpy.logging import configure_logger


LOGGER = logging.getLogger()


def _add_cwd_to_pythonpath():
    """
    Add the current working directory to the system path, this ensures that
    ctestpy can import the unittest modules, which should be defined as relative
    to the current working directory. For example:

    .. code-block:: bash

        $ cd my_project
        $ ctestpy tests/test_foo.py

    ctestpy will need to import the module: `tests.test_foo`, but that won't be
    possible without adding the current working directory (my_project) to the
    pythonpath.
    """
    sys.path.append(os.getcwd())


def main():
    """
    arguments are path to Python test file(s) that contain ctestpy unittests.
    """
    if len(sys.argv) <= 1:
        LOGGER.error("ctestpy needs to know which test suites to run.")
        LOGGER.error("  Example usage:")
        LOGGER.error("    ctestpy my_tests/tests.py other_tests/tests.py")
        sys.exit(1)
    _add_cwd_to_pythonpath()
    configure_logger()
    args = sys.argv[1:]
    LOGGER.info("CTestPy: running tests")
    for suite in (TestSuite(arg) for arg in args):
        suite.run()


if __name__ == "__main__":
    main()
