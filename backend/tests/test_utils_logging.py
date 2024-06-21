import os
from os import path
import time

import pytest
import datetime
from datetime import timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from backend.app.logging import DailyHierarchicalFileHandler


def test_init_valid_daily(logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    assert handler.when == "D"
    assert handler.interval == 86400  # One day in seconds
    assert handler.suffix == "%Y-%m-%d"


def test_init_valid_hourly(logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="H")
    assert handler.when == "H"
    assert handler.interval == 3600  # One hour in seconds
    assert handler.suffix == "%Y-%m-%d_%H"


def test_init_invalid_when(logs_foldername):
    with pytest.raises(ValueError):
        DailyHierarchicalFileHandler(logs_foldername, "test.log", when="X")


def test_init_valid_weekly(logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="W2")
    assert handler.when == "W2"
    assert handler.interval == 604800  # One week in seconds
    assert handler.dayOfWeek == 2
    assert handler.suffix == "%Y-%m-%d"


def test_init_invalid_weekly_day(logs_foldername):
    with pytest.raises(ValueError):
        DailyHierarchicalFileHandler(logs_foldername, "test.log", when="W8")


def test_calculate_filename_daily(mocker, logs_foldername):
    current_time = int(time.time())
    time_tuple=(2024, 6, 21, 12, 0, 0, 0, 0, 0)
    mocker.patch.object(time, "localtime", return_value=time_tuple)
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    filename = handler.calculate_fileName(current_time)
    assert filename == f"{logs_foldername}/test.log.2024-06-21.log"


def test_calculate_filename_utc(mocker, logs_foldername):
    current_time = int(time.time())
    time_tuple=(2024, 6, 21, 12, 0, 0, 0, 0, 0)
    mocker.patch.object(time, "gmtime", return_value=time_tuple)
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", utc=True)
    filename = handler.calculate_fileName(current_time)
    assert filename == f"{logs_foldername}/test.log.2024-06-21.log"


def test_get_files_to_delete_no_backups(mocker, logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", backupCount=0)
    mocker.patch.object(os, "listdir", return_value=["other.log"])
    new_filename = "test.log.2024-06-21.log"
    files_to_delete = handler.get_files_to_delete(new_filename)
    assert files_to_delete == []


def test_get_files_to_delete_excess_backups(mocker, logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", backupCount=1)
    mocker.patch.object(os, "listdir", return_value=[
        "test.log.2024-06-20.log", 
        "test.log.2024-06-19.log", 
        "other.log"
    ])
    new_filename = "test.log.2024-06-21.log"
    files_to_delete = handler.get_files_to_delete(new_filename)
    assert files_to_delete == ["test.log.2024-06-19.log"]



def test_do_rollover_calculates_new_filename(mocker, logs_foldername):
    current_time = int(time.time())
    
    time_tuple=(2024, 6, 21, 12, 0, 0, 0, 0, 0)
    mocker.patch.object(time, "localtime", return_value=time_tuple)
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    handler.doRollover()
    
    log_test="test.log.2024-06-22.log"
    assert handler.baseFilename.endswith(log_test)


def test_do_rollover_deletes_old_files(mocker, logs_foldername):
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D", backupCount=1)
    filename="test.log.2024-06-20.log"
    
    mocker.patch.object(os, "listdir", return_value=[
        "test.log.2024-06-20.log", "other.log"
    ])
    mocker.patch.object(os, "remove")
    handler.doRollover()
    assert os.remove.called_once_with(filename)


def test_do_rollover_handles_dst_change(mocker, logs_foldername):
    # Simulate DST turning on before next rollover (June to July)
    time_tuple=(2024, 6, 20, 2, 0, 0, 0, 0, 0)
    
    dst_on_time = time.mktime(time_tuple)  # June 20th, 2:00 AM (before DST)
    mocker.patch.object(time, "time", return_value=dst_on_time + 3600)  # June 20th, 3:00 AM (after DST)
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    handler.doRollover()
    
    # Rollover time should be adjusted for DST
    assert handler.rolloverAt > dst_on_time


def test_do_rollover_handles_dst_change_back(mocker, logs_foldername):
    # Simulate DST turning off before next rollover (October to November)
    time_tuple=(2023, 10, 29, 2, 0, 0, 0, 0, 0)
    
    dst_off_time = time.mktime(time_tuple)  # Oct 29th, 2:00 AM (DST)
    mocker.patch.object(time, "time", return_value=dst_off_time + 3600)  # Oct 29th, 3:00 AM (after DST ends)
    handler = DailyHierarchicalFileHandler(logs_foldername, "test.log", when="D")
    handler.doRollover()
    assert handler.rolloverAt > dst_off_time  # Rollover time should be adjusted for DST ending
