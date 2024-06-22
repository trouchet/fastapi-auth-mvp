import os
import pytest
import datetime
from pathlib import Path
from unittest.mock import patch

from backend.app.logging import DailyHierarchicalFileHandler


def test_init_filename_extraction(tmp_path):
    filename = Path(tmp_path, "subfolder/my_app.log")
    handler = DailyHierarchicalFileHandler(str(filename))
    assert handler.base_dir == str(filename.parent)
    assert handler.filename_base == "my_app"

fake_now_datetimes=[
    datetime.datetime(2024, 6, 20), 
    datetime.datetime(2024, 6, 21, 12, 0)
]
@pytest.mark.parametrize("now", fake_now_datetimes)
def test_doRollover_folder_creation(now, tmp_path):
    filename = Path(tmp_path, "my_app.log")
    handler = DailyHierarchicalFileHandler(str(filename))
    with patch.object(datetime, "datetime", return_value=now):
        handler.doRollover()
    expected_folder = Path(filename.parent, now.strftime("%Y/%m/%d"))
    assert expected_folder.exists()


fake_now_datetime=[
    datetime.datetime(2024, 6, 21, 12, 0)
]
@pytest.mark.parametrize("now", fake_now_datetime)
def test_doRollover_filename(now, tmp_path):
    filename = Path(tmp_path, "my_app.log")
    handler = DailyHierarchicalFileHandler(str(filename))
    with patch.object(datetime, "datetime", return_value=now):
        handler.doRollover()
    expected_filename = Path(
        filename.parent, 
        now.strftime("%Y/%m/%d"), 
        f"{filename.stem}.{now.strftime(handler.ext_style)}.{handler.ext}"
    )
    assert handler.baseFilename == str(expected_filename)


def test_doRollover_error_creating_folder(tmp_path, mocker):
    os_access_mock = mocker.patch("os.access", return_value=False)
    filename = Path(tmp_path, "my_app.log")
    handler = DailyHierarchicalFileHandler(str(filename))
    with patch.object(datetime, "datetime") as mock_now:
        mock_now.return_value = datetime(2024, 6, 21)
        handler.doRollover()
    os_access_mock.assert_called_once_with(filename.parent, os.W_OK)
