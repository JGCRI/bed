# Import libraries
import pytest
import bed


def test_class():
    """
    test class
    :return:
    """
    a1 = bed.Bed()  # Coming from Model.py
    assert a1.degree_hours == 1
    assert a1.demand_heat == 0


def test_demand():
    """
    test demand function
    :return:
    """
    val = bed.demand()

    assert val == 0


def test_temperature_to_degree_hours():
    """
    test temperature_to_degree_hours function
    :return:
    """
    val = bed.temperature_to_degree_hours()

    assert val == 1