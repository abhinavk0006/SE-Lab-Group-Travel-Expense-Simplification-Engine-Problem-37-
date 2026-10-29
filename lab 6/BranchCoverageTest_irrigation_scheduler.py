"""Exercise both outcomes of every decision plus exact threshold values.

Run explicitly with coverage run --branch; see COVERAGE_ANALYSIS.md.
"""

import pytest

from irrigation_scheduler import schedule, should_irrigate, water_volume


@pytest.mark.parametrize(
    "moisture,rain,stage,expected",
    [
        (60, 0, "seedling", False),
        (59, 0, "seedling", False),
        (30, 10, "seedling", False),
        (30, 9.9, "seedling", True),
        (44.9, 0, "seedling", True),
        (45, 0, "seedling", False),
        (54.9, 0, "flowering", True),
        (55, 0, "flowering", False),
        (39.9, 0, "vegetative", True),
        (40, 0, "vegetative", False),
        (30, 4.9, "vegetative", True),
        (30, 5, "vegetative", False),
        (30, 5, "seedling", True),  # Stage-specific logic precedes 5 mm check.
        (30, 5, "flowering", True),
        (30, 10, "flowering", False),
        (70, 20, "seedling", False),
    ],
)
def test_irrigation_decisions_and_boundaries(moisture, rain, stage, expected):
    assert should_irrigate(moisture, rain, stage) is expected


@pytest.mark.parametrize("area", [0, -1])
def test_nonpositive_area_raises(area):
    with pytest.raises(ValueError, match="^invalid area$"):
        water_volume(area, "seedling", 20)


@pytest.mark.parametrize(
    "area,stage,temp,expected",
    [
        (10, "seedling", 20, 20),
        (10, "flowering", 20, 50),
        (10, "vegetative", 20, 40),
        (10, "seedling", 35, 20),
        (10, "seedling", 35.1, 30),
        (10, "flowering", 10, 50),
        (10, "flowering", 9.9, 25),
        (2.5, "vegetative", 20, 10),
    ],
)
def test_volume_decisions_and_boundaries(area, stage, temp, expected):
    assert water_volume(area, stage, temp) == pytest.approx(expected)


def test_empty_schedule():
    assert schedule([], 100) == []


def test_skip_wet_zone_then_process_dry_zone():
    zones = [("wet", 10, 60, 0, "seedling", 20),
             ("dry", 10, 30, 0, "seedling", 20)]
    assert schedule(zones, 100) == ["dry"]


def test_all_zones_skipped():
    zones = [("wet", 10, 60, 0, "seedling", 20),
             ("rainy", 10, 30, 10, "flowering", 20)]
    assert schedule(zones, 0) == []


def test_exact_budget_is_accepted_and_remaining_budget_is_reduced():
    zones = [("first", 10, 30, 0, "seedling", 20),
             ("second", 10, 30, 0, "flowering", 20)]
    assert schedule(zones, 70) == ["first", "second"]
    assert schedule(zones, 69) == ["first"]


def test_over_budget_stops_before_later_affordable_zone():
    zones = [("first", 10, 30, 0, "seedling", 20),
             ("expensive", 10, 30, 0, "flowering", 20),
             ("cheap", 1, 30, 0, "seedling", 20)]
    assert schedule(zones, 25) == ["first"]


@pytest.mark.parametrize("budget", [0, 19.9])
def test_first_zone_exceeds_budget(budget):
    assert schedule([("dry", 10, 30, 0, "seedling", 20)], budget) == []


def test_invalid_area_propagates_for_zone_requiring_water():
    with pytest.raises(ValueError, match="^invalid area$"):
        schedule([("invalid", 0, 30, 0, "seedling", 20)], 100)
