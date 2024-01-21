# SPDX-FileCopyrightText: 2024-present Sam Boysel <sboysel@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest
import datetime
from retrograde.repo import (
    _datetime2unix,
    _unix2datetime,
    _rand_string
)

def test_utils_date_conversions():
    date_time = datetime.datetime(1969, 12, 31, 19, 0)
    assert _datetime2unix(date_time) == 0
    assert _unix2datetime(0) == date_time

def test_utils_rand_string():
    assert isinstance(_rand_string(5), str)
    assert _rand_string(5) != _rand_string(5)
    assert len(_rand_string(5)) == 5



