# Import libraries
import pytest
import bed
import os


def test_class():
    """
    test class
    :return:
    """
    downloaded_data_path = bed.get_data()
    example_config = os.path.join(downloaded_data_path, 'example_config.yml')
    c = bed.Bed(config_file=example_config)  # Coming from Model.py
    assert c.degree_hours == 1
    assert c.demand_heat == 0
    assert list(c.config.keys()) == ['dir_root', 'dir_outputs', 'path_example_data_set', 'path_temperature_ncdf']


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


def test_get_data():
    """
    test clean_up function
    :return:
    """
    assert os.path.abspath(bed.get_data()) == os.path.abspath(os.path.join(os.getcwd(), 'downloaded_data/examples'))


def test_read_config():
    """
    test read_config
    :return:
    """
    downloaded_data_path = bed.get_data()
    example_config = os.path.join(downloaded_data_path, 'example_config.yml')
    assert list(bed.read_config(example_config).keys()) == ['dir_root', 'dir_outputs', 'path_example_data_set', 'path_temperature_ncdf']


def test_read_data():
    """
    test method
    :return:
    """
    downloaded_data_path = bed.get_data()
    example_config = os.path.join(downloaded_data_path, 'example_config.yml')
    config = bed.read_config(example_config)
    example_key = list(config.keys())[0]
    example_value = os.path.join(downloaded_data_path, list(config.values())[0])
    updated_config = config
    updated_config[example_key] = example_value
    df = (bed.Data(updated_config)).example_dataset
    assert list(df.name) == ['a', 'b', 'c']
    assert list(df.value) == [1, 2, 3]


def test_method():
    """
    test method
    :return:
    """
    assert bed.demand(2, 2) == 1
    assert bed.temperature_to_degree_hours(2, 3) == 1


def test_write_outputs():
    """
    test diagnostics function
    :return:
    """
    assert bed.write_outputs() == 'outputs'


def test_diagnostics():
    """
    test diagnostics function
    :return:
    """
    assert bed.diagnostics() == 'diagnostics'


def test_clean_up():
    """
    test clean_up function
    :return:
    """
    assert bed.clean_up() == 'clean up'


def test_class():
    """
    test class
    :return:
    """
    assert bed.Bed().config == ''
    assert bed.Bed().degree_hours == 1
    assert bed.Bed().demand_heat == 0
