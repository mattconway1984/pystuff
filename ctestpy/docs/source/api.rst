API
===

Builder
-------

The ``Builder`` class is used to generate a temporary CPython module using *cffi*,
that includes the compiled CUT and mock stubs. This can then be loaded into the
CPython environment by ``ctestpy``. The ``Builder`` class handles all of this and provides
a simple interface for interfacing with test scripts.

.. automodule:: ctestpy.builder
   :members: Builder, CodeUnderTest, MockFunction

Test
----

``ctestpy`` provides its own test framework, responsible for running tests, handling
test setup/teardown, and reporting the results. To run the test framework, type the command
``ctestpy`` into your terminal.

.. automodule:: ctestpy.test
   :members:
