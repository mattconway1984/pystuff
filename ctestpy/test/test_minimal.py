import pytest

MOCK_MINIMAL_CUT_H = """
int test_cut_min();
"""

MOCK_MINIMAL_CUT = """
#include "cut.h"
int test_cut_min()
{
    return 180286;
}
"""


@pytest.fixture
def minimal_cut(tmp_path):
    with open(tmp_path / "cut.h") as chf:
        chf.write(MOCK_MINIMAL_CUT_H)
    with open(tmp_path / "cut.c") as cf:
        cf.write(MOCK_MINIMAL_CUT)

    yield tmp_path / "cut.h", tmp_path / "cut.c"


@pytest.mark.skip
def test_cut_no_mock(minimal_cut):
    test_builder = ctestpy.Builder()
    test_builder.add_cut(minimal_cut[0], minimal_cut[1])

    test = test_builder.build()
    assert test.test_cut_min() == 180286
