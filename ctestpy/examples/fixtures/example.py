import ctestpy


@ctestpy.fixture
def first():
    """
    Demonstration of a fixture.
    """
    print("first called")
    yield 1
    print("first done")


@ctestpy.fixture
def second():
    """
    Demonstration of a fixture.
    """
    print("second called")
    yield 2
    print("second done")


def test_foo(first, second):
    """
    Demonstration of a test method that requests fixtures
    """
    print(first)
    print(second)
