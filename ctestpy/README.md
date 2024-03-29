# CTestPy

Write Unit tests for C code in Python with PyTest.

## Documentation

Sphinx documentation for CTestPy can be found in `docs/`. This includes
autogenerated API documentation, design information, and examples.
The HTML output can be viewed in Gitlab's CI.

## Contributing

Feature requests and bugs must be added to [Issues](https://gitlab.uk.cambridgeconsultants.com/ws/tools/ctestpy/-/issues).

Development must be done on a branch created from the issue ticket, once 
development to satisfy the issue has been completed a Merge Request must be 
created. Each merge request must be reviewed by a developer and/or maintainer 
of CTestPy, and once approved, the branch can be merged. There is no rule on
squashing commits (feel free to decide at the time of merge), but merged brances
must be deleted.

## Building

Install Python 3.9 and [tox](https://tox.readthedocs.io/), then just run `tox`
from the project directory. This will build CTestPy, run linting, and build the 
documentation. Alternatively, run it from Docker:

```bash
$ docker run -it --rm -v ${PWD}:/home/ python:9 bash  # Fire up Docker

$ pip install tox   # Install tox

$ tox  # Run the unit tests and build the release.
```

## References

* **PyTest** - Python unit test framework - https://pytest.org

* **unittest** - Another Python unit test framework (with built in support for creating mock objects) - https://docs.python.org/3/library/unittest.html

* **cffi** - Python module for interfacing with C code https://cffi.readthedocs.io

* **pycparser** - Python module for parsing C code -https://github.com/eliben/pycparser
