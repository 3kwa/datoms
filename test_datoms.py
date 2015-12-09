import doctest

import datoms


def test_module_doctest():
    failure_count, _ = doctest.testmod(datoms)
    assert failure_count == 0
