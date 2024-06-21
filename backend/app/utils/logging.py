from os import (
    remove, scandir, path, makedirs, rename,
)
from shutil import rmtree

from logging.handlers import TimedRotatingFileHandler
import datetime

# Function to clear the latest 'n' items (files or folders)
def clear_folder_items(
    path_, remaining_items: int, key=lambda item: item.stat().st_mtime
):
    """
    Clears the latest 'n' items (files or folders) in the specified path.

    Args:
        path (str): The path to the directory containing the items.
        n (int): The number of latest items to clear.

    Raises:
        FileNotFoundError: If the specified path is not found.
        OSError: If an error occurs during removal.
    """
    if not path.exists(path_):
        raise FileNotFoundError(f"Path not found: {path_}")

    # Get all items sorted by modification time (newest first)
    items = sorted(scandir(path_), key=key)

    # Clear the latest 'n' items
    items_len = len(items)
    if items_len >= remaining_items:
        to_remove = items[0 : items_len - remaining_items]

        for item in to_remove:
            if path.isfile(item.path):
                remove(item.path)
            else:
                # Remove directory (ignore errors)
                rmtree(item.path, ignore_errors=True)


class DailyHierarchicalFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, encoding=None, delay=False):
        """
        Custom TimedRotatingFileHandler that creates logs with a daily hierarchy in '{year}/{month}/{day}' format.

        Args:
            filename (str): The base filename for the log files.
            when (str, optional): Defines the rollover schedule. Defaults to 'midnight'.
            interval (int, optional): The rollover interval in units defined by 'when'. Defaults to 1.
            backupCount (int, optional): The number of old log files to keep. Defaults to 0 (keep none).
            encoding (str, optional): The encoding of the log file. Defaults to None.
            delay (bool, optional): Whether to delay opening the file until it is needed. Defaults to False.
        """
        self.base_dir = path.dirname(filename)  # Extract directory from filename
        
        makedirs(self.base_dir, exist_ok=True)
        
        self.filename_base = path.splitext(filename)[0]  # Extract filename without extension
        self.ext_style = "%Y-%m-%d"  # Extension format for daily rotation
        super().__init__(filename, when, interval, backupCount, encoding, delay)

    def doRollover(self):
        """
        Override default behavior to create a new log file with date in path and filename.
        """
        self.stream.close()
        now = datetime.datetime.now()

        # Create year/month/day folders
        new_folder = path.join(self.base_dir, now.strftime("%Y/%m/%d"))
        makedirs(new_folder, exist_ok=True)  # Create folders if they don't exist

        new_filename = path.join(new_folder, f"{self.filename_base}.{now.strftime(self.ext_style)}.{self.ext}")
        self.baseFilename = new_filename
        self.stream = self._open_stream()
        self.extMatches = [f".{now.strftime(self.ext_style)}"]
        self.dfn = self.baseFilename

        if self.backupCount > 0:
            for s in self.suffixes[::-1]:
                if s in self.extMatches:
                    break
                i = self.extMatches.index(s)
                suffix = self.extMatches[i + 1]

                # Rotate older logs based on the new filename with folder structure
                source = path.join(self.base_dir, \
                        path.dirname(self.baseFilename), \
                        self.baseFilename + s)
                dest = path.join(
                    self.base_dir, 
                    path.dirname(self.baseFilename), 
                    self.baseFilename + suffix
                )
                
                if path.exists(source) and not path.exists(dest):
                    try:
                        rename(source, dest)
                    except Exception as e:
                        print(f"Error moving archive file: {source} - {dest} ({e})")

        self.rolloverAt = self.rolloverAt + self.interval * self.intervalFactor

