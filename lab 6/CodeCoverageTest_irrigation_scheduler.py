"""Statement coverage suite: execute every application statement.

Run from lab6 with:
python -m coverage run --source=irrigation_scheduler -m pytest -q CodeCoverageTest_irrigation_scheduler.py
python -m coverage report -m
"""

import pytest

from irrigation_scheduler import schedule, should_irrigate, water_volume


@pytest.mark.parametrize(
    "moisture,rain,stage,expected",
    [
        (60, 0, "seedling", False),  # Wet-soil early return.
        (30, 10, "seedling", False),  # Heavy-rain early return.
        (44, 0, "seedling", True),
        (45, 0, "seedling", False),
        (54, 0, "flowering", True),
        (30, 5, "vegetative", False),
        (39, 0, "vegetative", True),
    ],
)
def test_irrigation_returns(moisture, rain, stage, expected):
    assert should_irrigate(moisture, rain, stage) is expected


@pytest.mark.parametrize(
    "area,stage,temp,expected",
    [(10, "seedling", 40, 30), (10, "flowering", 5, 25),
     (10, "vegetative", 40, 60)],
)
def test_volume_calculation(area, stage, temp, expected):
    assert water_volume(area, stage, temp) == expected


def test_invalid_area():
    with pytest.raises(ValueError, match="^invalid area$"):
        water_volume(0, "seedling", 20)


def test_schedule_skip_append_and_break():
    zones = [
        ("wet", 10, 60, 0, "seedling", 40),
        ("seedlings", 10, 30, 0, "seedling", 40),  # 30 L.
        ("flowers", 10, 30, 0, "flowering", 40),  # 75 L; only 5 L remain.
        ("later", 1, 30, 0, "seedling", 40),
    ]
    assert schedule(zones, 35) == ["seedlings"]
