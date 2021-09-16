Basic Example
=============

This provides the most basic example of testing a C library using ctestpy, where
the C library under test does not rely on any external libraries, merely the 
computational power of the underlying machine. 

Basic APIs
----------

The code under test implements the APIs as declared in in ``src/calculator.h``.
It is the implementation of these APIs that shall be compiled and called from
the unit tests.

Add
"""

The calculator supports an API to add two integers, for example, as shown in
the following sequence diagram:

.. uml::

   client -> calculator : add(3,4)
   activate calculator

   calculator -> client : 7
   deactivate calculator

Subtract
""""""""

The calculator supports an API to subtract one integer from another, for 
example, as shown in the following sequence diagram:

.. uml::

   client -> calculator : sub(3,8)
   activate calculator

   calculator -> client : 5
   deactivate calculator

Unit Testing
------------

To unit test the APIs of the calculator "library", Python shall be used, and it
shall leverage features provided by CTestPy. To achieve this, the following
files are required:

#. main.py
#. tests/test_calculator.py

main.py
"""""""

This is simply a wrapper that uses the CTestPy context manager to:

#. Compile the source code under test.
#. Generates Python bindings allowing that compiled unit to be called from 
   Python scripts.
#. Provides a simple object with a well defined interface allowing the Python
   unit tests to call APIs of the code under test. 
#. Tidies up generated files when the context manager exits.

The following example:

.. code-block:: python3

   from ctestpy.builder import Builder, CodeModule
   import pytest

   if __name__ == "__main__":
      with Builder(testing=[CodeModule('src/calculator.c', 'src/calculator.h')]):
         pytest.main(['-x', 'tests', '-s'])

tests/test_calculator.py
""""""""""""""""""""""""

This script contains unit tests for the code under test:

.. code-block:: python3

   import pytest
   from _calculator.lib import add

   def test_one():
      # Call the code under test
      actual = add(5,6)
      # Verify the result is as expected
      assert actual == 11, f"Got: add(5, 6) = {actual}, expected 11"

The test script has to assume the Python bindings to interface with the built
object (i.e. the source code under test) will be generated and must import the
generated bindings. In this case, the code under test is ``src/calculator.h`` and
therefore, the code must import any bindings for each method that exists within
that library, for example:

.. code-block:: python3

   from _calculator.lib import add # Bindings to call the ``add`` method under test 
   from _calculator.lib import sub # Bindings to call the ``sub`` method under test
