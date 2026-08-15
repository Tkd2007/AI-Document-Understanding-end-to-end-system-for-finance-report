import pytest

from extract_baseline import parse_number


def test_parse_number_thuong():
    assert parse_number("13.217.639.635.987") == 13217639635987


def test_parse_number_am_trong_ngoac():
    assert parse_number("(1.234.567)") == -1234567


def test_parse_number_dau_tru():
    assert parse_number("  -1.234.567  ") == -1234567


def test_parse_number_khong_co_chu_so():
    with pytest.raises(ValueError):
        parse_number("abc")