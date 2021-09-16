import pathlib
from contextlib import contextmanager
from ctestpy.builder import Builder, CodeUnderTest
from ctestpy.test import fail


# CTestPy does not support pulling #define derivitives from the source code.
# To make the tests easier to read, they have been re-defined manually:
POWER_GPIO = 0x1a
LED_GPIO = 0x2b
SUCCESS = 0x0
FAILURE = 0xFF
HIGH = 0xFF
LOW = 0x00


@contextmanager
def builder():
    """
    This fixture will invoke CTestPy to build the code under test (note, this
    will rebuild the code-under-test for every test that depends on this
    fixture. Use of a session fixture could be better suited as build-time
    might have a significant effect on the speed of test suite execution.

    However, that's the choice of the user, and not a design consideration
    for CTestPy, an example of how to do that could be very useful to add to
    the CTestPy documentation.

    Yields:
        ctestpy.builder.Builder: An instance of the ctestpy Builder class.

    Example:
        ::python

            def test_something():
                with builder as build:
                    # Object containing Python bindings that allow the unittest
                    # to call the methods defined in the 'code under test':
                    code_under_test = build.testing

                    # Object containing mock implementations of each method
                    # defined in the `mocking` header(s) supplied to Builder.
                    # Note, these instances of `ctestpy.builder.MockedMethod`.
                    mocks = build.mocking

                    # Assuming the code under test has a method `call_me`, it
                    # can be invoked by the unittest using:
                    code_under_test.call_me()

                    # Assuming the mocked headers contain the declaration of a
                    # method `int squared(int);` (which squares an int and
                    # returns the result), it can be controlled by the test.
                    # For example, if the code under test has a method
                    # `void do_stuff(void);` which calls `squared` with some
                    # value, expectations can be created. For example, if it
                    # is expected to call `squared` with an argument value of
                    # `10` and get back a return value of `100`, the test would
                    # setup the following expectation:
                    mocks.squared.expect_and_return(10, retval=100)

                    # Call the code under test, the expectation that was set in
                    # the line above will ensure the code under test calls the
                    # mocked method `squared`, and when it does, that it calls
                    # it with a value of `10` and the method shall return the
                    # value of `100` back to the code under test:
                    code_under_test.do_stuff()
    """
    with Builder(
            testing=CodeUnderTest(
                source=pathlib.Path('src/controller.c'),
                header=pathlib.Path('src/controller.h')
            ),
            mocking=[
                pathlib.Path('src/gpio_driver.h'),
                pathlib.Path('src/gpio_driver_new.h'),
            ]) as builder:
        yield builder


def test_power_on_when_power_gpio_is_low():
    with builder() as build:
        # Expect code under test to get the current direction for POWER_GPIO.
        # This pretends that POWER_GPIO is held low:
        build.mocking.get_gpio.expect_and_return(POWER_GPIO, retval=SUCCESS)
        # Expect code under test to set the current direction for POWER_GPIO.
        # The expects that POWER_GPIO is going to the be driven high:
        build.mocking.set_gpio.expect_and_return(POWER_GPIO, HIGH, retval=SUCCESS)
        # Call the code under test:
        actual = build.testing.power_on()
        # Ensure return value is as expected:
        assert actual == SUCCESS, "Power on failed, expected it to succeed"


def test_power_on_expect_failure_due_to_missing_expectation():
    with builder() as build:
        # Expect code under test to get the current direction for POWER_GPIO.
        # This pretends that POWER_GPIO is held low:
        build.mocking.get_gpio.expect_and_return(POWER_GPIO, retval=SUCCESS)
        # The following expectation is missing, and should cause the test to fail:
        # build.mocking.set_gpio.expect_and_return(POWER_GPIO, HIGH, retval=SUCCESS)
        # Call the code under test:
        actual = build.testing.power_on()
        # Sould never get this far...
        print("yeah we are here")
        fail("Expected mock `set_gpio` to fail this test (missing expectation)")


def test_power_on_expect_failure_due_to_unsatisfied_expectation():
    with builder() as build:
        # Expect code under test to get the current direction for POWER_GPIO.
        # This pretends that POWER_GPIO is held low:
        build.mocking.get_gpio.expect_and_return(POWER_GPIO, retval=SUCCESS)
        # Expect code under test to set the current direction for POWER_GPIO.
        # The expects that POWER_GPIO is going to the be driven high:
        build.mocking.set_gpio.expect_and_return(POWER_GPIO, HIGH, retval=SUCCESS)
        # The following expectation is superflous (i.e. the code under test is not
        # expected to satisfy this expectation); this should cause the test to fail.
        build.mocking.set_gpio.expect_and_return(POWER_GPIO, HIGH, retval=SUCCESS)
        # Call the code under test:
        actual = build.testing.power_on()
        assert False, \
            "Expected mock `set_gpio` to fail this test (unsatisfied expectation)"


def test_power_on_expect_failure_due_to_unexpected_arg_value():
    with builder() as build:
        # Code under test should try to get the current direction for
        # POWER_GPIO. The following expectation is intentionally wrong as it
        # expects code under test to get the current direction for LED_GPIO.
        # This should cause the test to fail.
        build.mocking.get_gpio.expect_and_return(LED_GPIO, retval=SUCCESS)
        # Call the code under test:
        actual = build.testing.power_on()
        assert False, \
            "Expected mock `get_gpio` to fail this test (unexpected arg value)"


def test_power_on_when_power_gpio_is_high():
    with builder() as build:
        build.mocking.get_gpio.expect_and_return(POWER_GPIO, retval=HIGH)
        # Call the code under test:
        actual = build.testing.power_on()
        assert actual == SUCCESS, "Power on failed, expected it to succeed"


def test_power_on_when_power_gpio_is_low_but_fails_to_drive_high():
    with builder() as build:
        # Expect code under test to get the current direction for POWER_GPIO.
        # This pretends that POWER_GPIO is held high:
        build.mocking.get_gpio.expect_and_return(POWER_GPIO, retval=SUCCESS)
        # Expect code under test to set the current direction for POWER_GPIO.
        # The expects that POWER_GPIO is going to the be driven high:
        build.mocking.set_gpio.expect_and_return(POWER_GPIO, HIGH, retval=FAILURE)
        # Call the code under test:
        actual = build.testing.power_on()
        # Ensure return value is as expected:
        assert actual == FAILURE, "Power on succeeded, expected it to fail"
