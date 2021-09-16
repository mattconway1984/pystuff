import multiprocessing
import contextlib
import functools
import importlib
import inspect
import pathlib
import sys
import traceback
import io
import os

from logging import getLogger

LOGGER = getLogger("test")


def fixture(func):
    """
    Decorator used within test suites to define a CTestPy Fixture.

    :example:
        >>> import ctestpy
        >>>
        >>> @ctestpy.fixture
        >>> def my_fixture():
        >>>     yield 1234
        >>>
        >>> def my_test(my_fixture):
        >>>     # The following should print `my test 1234`
        >>>     print("my test", my_fixture)
    """
    @contextlib.contextmanager
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.__ctestpy_fixture__ = True
    return wrapper


def fail(message):
    """
    fail method to be called by anything that raises a ctestpy failure.
    """
    LOGGER.error(message)
    os._exit(1)


class TestMethod:
    """
    Represents a ctestpy unittest.

    Each unit test method (a method prefixed with `test_`) can request fixtures
    which allow the test to depend on common functionality as defined by the
    test suite developer. It is important when running the test, that these
    requested fixtures are first called (in the order they are defined).
    """

    def __init__(self, name, reference, requests):
        self._name = name
        self._reference = reference
        self._requests = requests

    @property
    def name(self):
        """
        Name of the unittest.
        """
        return self._name

    def __call__(self, *args, **kwargs):
        with contextlib.redirect_stderr(io.StringIO()):
            LOGGER.running(f"{self.name}")
            try:
                with contextlib.ExitStack() as stack:
                    args = [stack.enter_context(req()) for req in self._requests]
                    self._reference(*args)
            except Exception as error:
                LOGGER.failed("%s: %s", self.name, str(error))
            else:
                LOGGER.passed("%s", self.name)


class TestSuite:
    """
    Represents a ctestpy test suite.

    A test suite is simply a Python file that contains a collection of methods,
    tests are defined by the name of the method and must have `test_` prefix.
    """

    def __init__(self, path):
        self._path = pathlib.Path(path)
        module_path = self._path.as_posix().replace("/", ".").strip(".py")
        self._module = importlib.import_module(module_path)
        self._methods = self._find_test_methods(self._module)

    @staticmethod
    def _discover_test_methods(module):
        """
        This helper method discovers all the ctestpy test methods defined within
        a test suite (i.e. a Python module).
        """
        return {
            name: ref for name, ref in module.__dict__.items()
            if callable(ref) and ref.__name__.startswith("test_")
        }

    @staticmethod
    def _discover_fixtures(module):
        """
        This helper method discovers all the ctestpy fixtures defined within a
        test suite (i.e. a Python module).
        """
        return {
            name: ref for name, ref in module.__dict__.items()
            if hasattr(ref, "__ctestpy_fixture__")
        }

    @staticmethod
    def _create_test_methods(test_methods, fixtures):
        """
        Each test method may request a number of fixtures. This helper method
        discovers which fixtures are being requested by the test method, and
        verifies all requested fixtures exist.
        """
        result = []
        for test_method, reference in test_methods.items():
            requests = inspect.signature(reference).parameters
            if not all(arg in fixtures.keys() for arg in requests):
                raise Exception(
                    f"Test method `{test_method}` is attempting to request "
                    f"fixture `{arg}` that does not exist")
            result.append(
                TestMethod(
                    test_method,
                    reference,
                    [fixtures[req] for req in requests]))
        return result

    @staticmethod
    def _find_test_methods(module):
        """
        Find all methods in a python module whose name has the `test_` prefix.
        """
        test_methods = TestSuite._discover_test_methods(module)
        fixtures = TestSuite._discover_fixtures(module)
        return TestSuite._create_test_methods(test_methods, fixtures)

    @property
    def name(self):
        """
        Name of the test suite.
        """
        return self._path.stem

    def run(self):
        """
        Method to run the test suite.
        """
        LOGGER.running(f"{self.name}")
        for method in self._methods:
            test_process = multiprocessing.Process(target=method)
            test_process.start()
            test_process.join()
            if test_process.exitcode != 0:
                LOGGER.failed("%s", self.name)
