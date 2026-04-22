import pytest

from domain.value_objects.rut import RUT
from domain.exceptions import InvalidRUTException


def test_validate_rut_valid():
    assert RUT.validate("12345678-9") is True


def test_validate_rut_invalid():
    with pytest.raises(InvalidRUTException):
        RUT.validate("12345678-0")
