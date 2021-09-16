import pycparser.c_ast
import pycparser
import pycparser.c_generator
import pathlib
import cffi
import sys
import uuid
import re
import inspect
import glob
import os
import subprocess
import importlib
from typing import List
import warnings
from ctestpy.test import fail
from logging import getLogger


LOGGER = getLogger("builder")


def preprocess(source, include_dirs):
    """
    Run the preprocessor and return the stdout result.
    """
    cmd_includes = [f"-I{inc}" for inc in include_dirs]
    process = \
        subprocess.run(
            ['gcc', '-E', '-P', '-'] + cmd_includes,
            input=source,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            check=True)
    return process.stdout


class Function:
    """
    """
    def __init__(self, name, args):
        self.name = name
        self.args = args


class FunctionList(pycparser.c_ast.NodeVisitor):
    """
    Discover all methods required by the tests.

    Parses the source files of the code under test, and looks at the includes
    to discover lists of functions that are:

        1. local to the code under test (i.e. callable/testable methods)
        2. external to the code under test (i.e. mockable methods)
    """

    def __init__(self, source):
        self._local_functions = set()
        self._all_functions = set()
        self._external_functions = set()
        self.visit(pycparser.CParser().parse(source))
        self._verify()

    @property
    def locals(self):
        """
        set: names for each local function defined within the code under test.
        """
        return self._local_functions
        return {fn.name for fn in self._local_functions}

    @property
    def externs(self):
        """
        set: names for each external function required by the code under test.
        """
        return self._external_functions
        return {fn.name for fn in self._external_functions}

    def visit_FuncDef(self, node):
        # Only local functions (i.e. those that exist in the source code file)
        # are considered locally defined.
        self._add_local_function(node.decl)

    def visit_Decl(self, node):
        if isinstance(node.type, pycparser.c_ast.FuncDecl):
            self._add_function(node)

    def _add_local_function(self, node):
        self._local_functions.add(node)

    def _add_function(self, node):
        self._all_functions.add(node)

    def _parse_FuncDef(self, node):
        return Function(node.name, [arg.name for arg in node.type.args])

    def _get_external_functions(self):
        """
        Annoyingly, because the nodes are unique objects and ast node class
        does not appear to have an __eq__ method to verify if the node data
        matches. This method is required to find nodes that do not exist in
        `self._local_functions` but do exist in `self._all_functions`.
        """
        externs = set()
        for function in self._all_functions:
            is_local = False
            for local_function in self._local_functions:
                if function.name == local_function.name:
                    is_local = True
                    break
            if not is_local:
                externs.add(function)
        return externs

    def _verify(self):
        externs = self._get_external_functions()
        self._external_functions = \
            [self._parse_FuncDef(node) for node in externs]
        self._local_functions = \
            [self._parse_FuncDef(node) for node in self._local_functions]


class CodeUnderTest:
    """
    Represents the Code Under Test.

    :param: source - file path for the CUT source file
    :param: header - file path for the CUT header file
    """

    def __init__(self, source, header):
        self._source = source
        self._header = header
        self._unique_name = f"__{self._source.stem}__{uuid.uuid4().hex}"

    @property
    def unique_name(self):
        """
        str: Unique name given to the current build (to ensure rebuilds always
            forced.
        """
        return self._unique_name

    def _get_method_declarations(self, source, local_methods):
        """
        Generate a list of method declarations that can be passed to CFFI.
        """

        class CFFIGenerator(pycparser.c_generator.CGenerator):
            """
            Class to visit all declared methods. For methods that do not exist
            "locally" to the code under test (i.e. mocked methods), CFFI must
            be instructed to create bindings to allow those methods to be
            invoked from the code under test.

            Functions declared with extern "Python+C" are generated as
            non-static, as they must be directly callable from other C source
            files.

            Args: local_methods: list of method names that are local to the
                code under test (i.e. not mocked methods).

            .. _CFFI documentation:
                https://cffi.readthedocs.io/en/latest/using.html#extern-python-c
            """

            def __init__(self, local_methods):
                super().__init__()
                self._local_methods = local_methods

            def visit_Decl(self, decl, *args, **kwargs):
                result = super().visit_Decl(decl, *args, **kwargs)
                if isinstance(decl.type, pycparser.c_ast.FuncDecl):
                    if decl.name not in self._local_methods:
                        return 'extern "Python+C" ' + result
                return result

        generator = CFFIGenerator(local_methods)
        return generator.visit(pycparser.CParser().parse(source))

    def generate(self, mock_headers):
        source = self._source.read_text()

        # preprocess all required header files for CFFI
        headers = mock_headers.copy()
        headers.append(self._header)
        include_dirs = []
        for header in headers:
            include_dir = str(header.parents[0])
            if include_dir not in include_dirs:
                include_dirs.append(include_dir)
        inc_directives = "\n".join([f'#include "{inc}"' for inc in headers])
        includes = preprocess(inc_directives, include_dirs)
        function_list = FunctionList(preprocess(source, include_dirs))
        local_function_names = {fn.name for fn in function_list.locals}
        includes = self._get_method_declarations(includes, local_function_names)

        # Compile:
        ffibuilder = cffi.FFI()
        ffibuilder.cdef(includes)
        ffibuilder.set_source(self.unique_name, source, include_dirs=["src/"])
        ffibuilder.compile()

        # Generate the mocked methods and return the bindings:
        module = importlib.import_module(self.unique_name)
        mocked_methods = MockedMethods(module.ffi, function_list.externs)
        return module.lib, mocked_methods


class MockFunction:
    """
    Represents a mockable function.

    :param: name of this function
    :param: args parameter names for this function
    """

    def __init__(self, name, args):
        self._name = name
        self._args = args
        self._call_args = []
        self._call_retvals = []

    def expect_and_return(self, *args, retval=None):
        """
        Allow unit test to set an expectation the method was invoked.

        Args:
            args: comma separated list of argument values; denotes the
                expected values of each argument that is passed to the mock
                function by the code under test.
            retval: the value which this mocked method shall return to the
                code under test when it is called.

        Note:
            This method can be called multiple times to setup an ordered list
            of expectations.
        """
        LOGGER.debug(
            "%s: Expectation registered, args=%s, retval=%s",
            self._name,
            args,
            retval)
        self._call_retvals.append(retval)
        self._call_args.append(args)

    def _validate_call(self, *args, **kwargs):
        if not self._call_args:
            argstr = ",".join((str(arg) for arg in args))
            fail(
                f"Mocked method `{self._name}({argstr})` "
                "was called without any expectations")
        expected_args = self._call_args[0]
        self._call_args = self._call_args[1:]
        for name, expected, actual \
                in zip(list(self._args), list(expected_args), list(args)):
            if expected != actual:
                fail(
                    f"method={self._name}, "
                    f"arg={name}: "
                    f"{actual=} but "
                    f"{expected=}")

    def _get_retval(self):
        retval = self._call_retvals[0]
        self._call_retvals = self._call_retvals[1:]
        return retval

    def __call__(self, *args, **kwargs):
        LOGGER.debug("%s: Called, args=%s, kwargs=%s", self._name, args, kwargs)
        self._validate_call(*args, **kwargs)
        retval = self._get_retval()
        LOGGER.debug("%s: Returning: %s", self._name, retval)
        return retval

    def verify(self):
        """
        Verify the mock has no unsatisfied expectations.

        Note: this should only be utilised by the Builder class at the end
        of each test (from the context manager cleanup stage).
        """
        if self._call_args:
            fail(
                f"unsatisfied exceptions exist for mocked method: {self._name}")


class MockedMethods:
    """
    Public methods from the `mocking` headers shall all be "mocked"; this
    class shall represent a public list of all available mocked methods.
    """

    def __init__(self, ffi, mocked_methods):
        for method in mocked_methods:
            setattr(self, method.name, MockFunction(method.name, method.args))
            ffi.def_extern(method.name)(getattr(self, method.name))

    def verify(self):
        mocked_methods = \
            (method[1] for method in inspect.getmembers(
                self,
                lambda member: isinstance(member, MockFunction)))
        for method in mocked_methods:
            method.verify()


class Builder:
    """
    The main interface for test scripts.

    This class takes a list of code under test (.h and .c) files,
    and a list of dependencies that need to be mocked (.h files).

    This class can then be used as a context manager to build the cffi
    module including code under test and mock stubs. The ``testing`` and
    ``mocking`` members of this class provide access to the CodeUnderTest
    and MockedMethod instances for this test.

    :param testing: instance of ``CodeUnderTest`` - the code that is being tested
    :param mocking: list of ``pathlib.Path`` of the header files for the dependencies
        that are being mocked.

    :example:
        >>> with Builder(CodeUnderTest('a.c', 'a.h'), ['mock.h']) as builder:
        >>>     builder.mocking.mock_expect_and_return(1985, retval=88)
        >>>     builder.testing.call()
    """

    def __init__(
            self,
            testing: CodeUnderTest,
            mocking: List[pathlib.Path] = None):
        self._testing = testing
        self._mock_headers = mocking if mocking else []

    def __enter__(self):
        testing, mocking = self._testing.generate(self._mock_headers)
        setattr(self, "testing", testing)
        setattr(self, "mocking", mocking)
        return self

    def __exit__(self, type, value, traceback):
        LOGGER.debug("Starting test cleanup")
        for this_file in glob.glob(f"{self._testing.unique_name}*"):
            LOGGER.debug(f"Removing temporary file: {this_file}")
            os.remove(this_file)
        # Enusre all expectations have been satisfied for each mock
        self.mocking.verify()
