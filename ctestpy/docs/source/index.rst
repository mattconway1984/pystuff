CTestPy
=======

*Write Unit tests for C code in Python*

CTestPy allows developers to write unit tests for C code in Python.
In additional to the usual features offered by C/C++ test frameworks (test fixtures, setup/teardown, etc.),
CTestPy supports **mocking C dependencies** in Python.
In most cases, no changes are required to the Code Under Test (CUT), and all of the 
test cases and configuration can be written in Python.

Features
--------

* Test C CUT from Python test scripts

* Write mock C functions in Python to test individual C modules in isolation

* Simple user-interface, no advanced features of Python required

Planned Features (not yet implemented)
--------------------------------------

* Support for mocking system functions - e.g., ``malloc`` and ``free``. Currently,
  CUT cannot call any system functions, including ``printf``.

* Support for multi-threaded CUT

* Support for derived types - opinters, arrays, structs, unions, and function pointers

* Support for C++

* Support for running ``ctestpy`` on h

Example
-------

Here is a basic example of CTestPy in action. This includes a dependency we'd like
to mock (``my_dependency(char)``) declared by a header file ``include/example_header.h``;
and C CUT we'd like to test (``my_cut()``), defined in ``source/example_cut.c``.

.. code-block:: C
   :linenos:
   :caption: C Header file we'd like to mock
   
   // include/example_header.h
   int my_dependency(char a);

.. code-block:: C
   :linenos:
   :caption: C Header file for code we'd like to test

   //include/example_cut.h
   int my_cut();

.. code-block:: C
   :linenos:
   :caption: C CUT we'd like to test

   // source/example_cut.c
   #include "include/example_header.hh
   int my_cut()
   {
      return my_dependency('b') + 1;
   }

Here's the CTestPy test case for this test:

.. code-block:: python
   :linenos:
   :caption: CTestPy test script

   # test.py
   import ctestpy, contextlibh
   @contextlib.contextmanager
   def builder():
      with ctestpy.Builder(
         testing=CodeUnderTest(
            source=pathlib.Path('source/example_cut.c'),
            header=pathlib.Path('include/example_cut.h')
         ),
         mocking=[
            pathlib.Path('include/example_header.h')
         ]) as builder:
            yield builder

   def test_mock():
      with builder() as build:
         build.mocking.my_dependency.expect_and_return(ord('b'), retval=2)
         actual = build.testing.my_cut()
         assert actual == 3

All of the test code in this example is in Python. The CUT and the mock
interface are unchanged, and the CUT can be developed without any consideration for 
how the unit tests run.

We can run the unit tests as follows:

.. code-block:: shell
   
   bash$ ctestpy  test.py

.. toctree::
   :maxdepth: 2
   :hidden:
   :glob:

   usage
   design
   examples
   faq
   api
