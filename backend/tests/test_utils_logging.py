import os
import time
from shutil import rmtree
from unittest.mock import patch

import pytest
import shutil

from backend.app.utils.logging import (
    clear_folder_items,
    DailyHierarchicalFileHandler,
)


def test_init_valid_daily(logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    assert handler.when == "D"
    assert handler.interval == 86400  # One day in seconds
    assert handler.suffix == "%Y-%m-%d"

    rmtree(logs_foldername, ignore_errors=True)


def test_init_valid_hourly(logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="H")

    assert handler.when == "H"
    assert handler.interval == 3600  # One hour in seconds
    assert handler.suffix == "%Y-%m-%d_%H"

    rmtree(logs_foldername, ignore_errors=True)


def test_init_valid_weekly(logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="W2")
    assert handler.when == "W2"
    assert handler.interval == 604800  # One week in seconds
    assert handler.dayOfWeek == 2
    assert handler.suffix == "%Y-%m-%d"

    rmtree(logs_foldername, ignore_errors=True)


def test_init_invalid_weekly_day(logs_foldername):
    with pytest.raises(ValueError):
        DailyHierarchicalFileHandler(logs_foldername, "test.log", when="W8")

    rmtree(logs_foldername, ignore_errors=True)


def test_calculate_filename_daily(logs_foldername):
    time_tuple = (2000, 1, 1, 12, 0, 0, 0, 0, 0)
    current_time = time.mktime(time_tuple)

    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")

    filename = handler.calculate_filename(current_time)
    assert filename.startswith(f"{logs_foldername}/2000/01/01/test.log.2000-01-01")

    rmtree(logs_foldername, ignore_errors=True)


def test_calculate_filename_utc(mocker, logs_foldername):
    current_time = int(time.time())
    time_tuple = (2000, 1, 1, 0, 0, 0, 0, 0, 0)

    handler = DailyHierarchicalFileHandler(
        logs_foldername, "test.log", when="D", utc=True
    )

    current_time = time.mktime(time_tuple)
    filename = handler.calculate_filename(current_time)
    assert filename.startswith(f"{logs_foldername}/2000/01/01/test.log.2000-01-01")

    rmtree(logs_foldername, ignore_errors=True)


@patch("backend.app.utils.logging.listdir")
def test_get_files_to_delete_no_backups(listdir_mocker, logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", backupCount=0)
    listdir_mocker.return_value=["other.log"]
    
    new_filename = "test.log.2000-01-01.log"
    files_to_delete = handler.get_files_to_delete(new_filename)
    assert files_to_delete == []

    rmtree(logs_foldername, ignore_errors=True)


@patch("backend.app.utils.logging.listdir")
def test_get_files_to_delete_excess_backups(listdir_mocker, logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", backupCount=1)
    listdir_mocker.return_value=["test.log.2000-01-01.log", "test.log.2000-01-02.log"]
    
    new_filename = "test.log.2000-01-03.log"
    files_to_delete = handler.get_files_to_delete(new_filename)
    assert files_to_delete == ["test.log.2000-01-01.log"]

    rmtree(logs_foldername, ignore_errors=True)


@patch("backend.app.utils.logging.time")
def test_do_rollover_calculates_new_filename(mocked_time, logs_foldername):
    time_tuple = (2000, 1, 1, 12, 0, 0, 0, 0, 0)
    log_test = f"{logs_foldername}/2000/01/02/test.log.2000-01-02"

    current_time = time.mktime(time_tuple)

    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    handler.rolloverAt = current_time

    handler.doRollover()

    next_filename=handler.calculate_filename(handler.rolloverAt)
    assert next_filename.startswith(log_test)

    rmtree(logs_foldername, ignore_errors=True)


def test_do_rollover_deletes_old_files(mocker, logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", backupCount=1)
    filename="test.log.2024-06-20.log"
    
    mocker.patch.object(os, "listdir", return_value=[
        "test.log.2024-06-20.log", 
        "other.log"
    ])
    mocker.patch.object(os, "remove")
    handler.doRollover()
    assert os.remove.called_once_with(filename)

    rmtree(logs_foldername, ignore_errors=True)


def test_do_rollover_handles_dst_change(mocker, logs_foldername):
    # Simulate DST turning on before next rollover (June to July)
    time_tuple=(2000, 1, 1, 2, 0, 0, 0, 0, 0)
    
    # June 20th, 2:00 AM (before DST)
    dst_on_time = time.mktime(time_tuple)
    
    # June 20th, 3:00 AM (after DST)
    mocker.patch.object(time, "time", return_value=dst_on_time + 3600)
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    handler.doRollover()

    # Rollover time should be adjusted for DST
    assert handler.rolloverAt > dst_on_time

    rmtree(logs_foldername, ignore_errors=True)


def test_clear_folder_items_success(logs_foldername):
    """Tests clear_latest_items with successful removal."""
    shutil.rmtree(logs_foldername, ignore_errors=True)

    os.makedirs(logs_foldername, exist_ok=True)
    os.makedirs(f"{logs_foldername}/1", exist_ok=True)
    os.makedirs(f"{logs_foldername}/2", exist_ok=True)
    os.makedirs(f"{logs_foldername}/3", exist_ok=True)

    # Provides key to ordenate by name
    def key_map_(item):
        return item.path

    clear_folder_items(logs_foldername, 2, key_map=key_map_)
    
    assert not os.path.exists(f"{logs_foldername}/1")
    assert os.path.exists(f"{logs_foldername}/2")
    assert os.path.exists(f"{logs_foldername}/3")

    rmtree(logs_foldername, ignore_errors=True)


def test_clear_folder_items_key_name(logs_foldername):
    """Tests clear_latest_items with a key name."""
    rmtree(logs_foldername, ignore_errors=True)

    os.makedirs(logs_foldername, exist_ok=True)
    os.makedirs(f"{logs_foldername}/1", exist_ok=True)
    os.makedirs(f"{logs_foldername}/2", exist_ok=True)
    os.makedirs(f"{logs_foldername}/3", exist_ok=True)

    def key_map_(item):
        return item.path

    clear_folder_items(logs_foldername, 2, key_map=key_map_)

    assert not os.path.exists(f"{logs_foldername}/1")
    assert os.path.exists(f"{logs_foldername}/2")
    assert os.path.exists(f"{logs_foldername}/3")

    rmtree(logs_foldername, ignore_errors=True)


def test_clear_folder_items_not_found(logs_foldername):
    """Tests clear_latest_items with a non-existent path."""
    rmtree(logs_foldername, ignore_errors=True)

    try:
        clear_folder_items(logs_foldername, 2)
    except FileNotFoundError as e:
        assert str(e) == f"Path not found: {logs_foldername}"
    else:
        assert False, "Expected FileNotFoundError."

    rmtree(logs_foldername, ignore_errors=True)


def test_clear_folder_items_not_enough_items(logs_foldername):
    """Tests clear_latest_items with fewer items than requested."""
    rmtree(logs_foldername, ignore_errors=True)

    os.makedirs(logs_foldername, exist_ok=True)
    os.makedirs(f"{logs_foldername}/1", exist_ok=True)
    os.makedirs(f"{logs_foldername}/2", exist_ok=True)

    clear_folder_items(logs_foldername, 3)

    assert os.path.exists(f"{logs_foldername}/1")
    assert os.path.exists(f"{logs_foldername}/2")

    rmtree(logs_foldername, ignore_errors=True)


def test_clear_folder_items_files(logs_foldername):
    """Tests clear_latest_items with files."""
    rmtree(logs_foldername, ignore_errors=True)

    os.makedirs(logs_foldername, exist_ok=True)
    with open(f"{logs_foldername}/1.txt", "w") as f:
        f.write("test")
    with open(f"{logs_foldername}/2.txt", "w") as f:
        f.write("test")
    with open(f"{logs_foldername}/3.txt", "w") as f:
        f.write("test")
    
    clear_folder_items(logs_foldername, 2)

    assert os.path.exists(f"{logs_foldername}/1.txt")
    assert os.path.exists(f"{logs_foldername}/2.txt")
    assert not os.path.exists(f"{logs_foldername}/3.txt")
    
    rmtree(logs_foldername, ignore_errors=True)


@pytest.mark.parametrize(
    "rollover_data",
    [
        (       "S",                1, "%Y-%m-%d_%H-%M-%S", r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"),
        (       "M",               60,    "%Y-%m-%d_%H-%M",       r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$"),
        (       "H",          60 * 60,       "%Y-%m-%d_%H",             r"^\d{4}-\d{2}-\d{2}_\d{2}$"),
        (       "D",     60 * 60 * 24,          "%Y-%m-%d",                   r"^\d{4}-\d{2}-\d{2}$"),
        ("MIDNIGHT",     60 * 60 * 24,          "%Y-%m-%d",                   r"^\d{4}-\d{2}-\d{2}$"),
        (      "W2", 60 * 60 * 24 * 7,          "%Y-%m-%d",                   r"^\d{4}-\d{2}-\d{2}$"),
    ],
)
def test_daily_handler_rollover(
    mocker, mock_time_functions, mock_strftime,
    test_time_tuple, test_current_time, logs_foldername,
    rollover_data
):
    # Unpack test data
    when, interval, suffix, ext_match_pattern = rollover_data

    # Create handler
    handler = DailyHierarchicalFileHandler(
        root_foldername=logs_foldername, filename="app.log", when=when
    )

    # Assert expected attributes
    assert handler.when == when
    assert handler.interval == interval
    assert handler.suffix == suffix
    assert handler.extMatch.pattern == ext_match_pattern

    if when[0] == "W":
        assert handler.dayOfWeek == int(when[1])

    # Assert calculated filename
    year = str(test_time_tuple[0]).zfill(4)
    month = str(test_time_tuple[1]).zfill(2)
    day = str(test_time_tuple[2]).zfill(2)
    filename = f"{logs_foldername}/{year}/{month}/{day}/app.log.{year}-{month}-{day}"
    assert handler.calculate_filename(test_current_time).startswith(filename)

    rmtree(logs_foldername, ignore_errors=True)

def test_weekly_handler_raises_3_digits(
    mocker, mock_time_functions, mock_strftime, 
    test_time_tuple, test_current_time, logs_foldername
):
    with pytest.raises(ValueError):
        DailyHierarchicalFileHandler(
            root_foldername=logs_foldername, filename="app.log", when="W42"
        )
        
    rmtree(logs_foldername, ignore_errors=True)


def test_weekly_handler_raises_digit_outside_0_6(
    mocker, mock_time_functions, mock_strftime, 
    test_time_tuple, test_current_time, logs_foldername
):
    with pytest.raises(ValueError):
        DailyHierarchicalFileHandler(
            root_foldername=logs_foldername, filename="app.log", when="W8"
        )
        
    rmtree(logs_foldername, ignore_errors=True)


def test_weekly_handler_raises_invalid_when(
    mocker, mock_time_functions, mock_strftime, 
    test_time_tuple, test_current_time, logs_foldername
):
    with pytest.raises(ValueError):
        DailyHierarchicalFileHandler(
            root_foldername=logs_foldername, filename="app.log", when="X"
        )
    
    rmtree(logs_foldername, ignore_errors=True)

def test_handler_rollover_repr(
    mocker, mock_time_functions, mock_strftime, 
    test_time_tuple, test_current_time, 
    logs_foldername
):
    from reprlib import repr

    handler = DailyHierarchicalFileHandler(
        root_foldername=logs_foldername, filename="app.log", when="D"
    )
    args = "'logs', 'app.log', 'D', 1, 0, None, False, False, None, '.log'"
    obj_repr = f"DailyHierarchicalFileHandler({args})"
    assert handler.__repr__() == repr(obj_repr)

    rmtree(logs_foldername, ignore_errors=True)
