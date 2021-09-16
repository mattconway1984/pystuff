from contextlib import contextmanager
import pathlib

from ctestpy.builder import Builder, CodeUnderTest


@contextmanager
def builder():
    with Builder(
            testing=CodeUnderTest(
                source=pathlib.Path('src/calculator.c'),
                header=pathlib.Path('src/calculator.h'))) as builder:
        yield builder


def test_one():
    with builder() as build:
        actual = build.testing.add(5, 6)
        assert actual == 11, f"Got: add(5, 6) = {actual}, expected 11"


def test_two():
    with builder() as build:
        actual = build.testing.sub(8, 6)
        assert actual == -2, "failed"
