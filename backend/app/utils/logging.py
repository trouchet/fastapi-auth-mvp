from os import remove, scandir, path, makedirs, getpid, listdir
from shutil import rmtree
from time import (
    time,
    gmtime,
    localtime,
    strftime,
)
import datetime
import re


from logging.handlers import (
    TimedRotatingFileHandler,
    BaseRotatingHandler,
)


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
    def __init__(
        self,
        foldername: str,
        filename: str,
        when="h",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
        atTime=None,
        postfix=".log",
    ):
        self.folderName = foldername
        makedirs(foldername, exist_ok=True)

        self.origFileName = filename
        self.when = when.upper()
        self.interval = interval
        self.backupCount = backupCount
        self.utc = utc
        self.atTime = atTime
        self.postfix = postfix

        if self.when == "S":
            self.interval = 1  # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"

        elif self.when == "M":
            self.interval = 60  # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$"

        elif self.when == "H":
            self.interval = 60 * 60  # one hour
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}$"

        elif self.when == "D" or self.when == "MIDNIGHT":
            self.interval = 60 * 60 * 24  # one day
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}$"

        elif self.when.startswith("W"):
            self.interval = 60 * 60 * 24 * 7  # one week

            if len(self.when) != 2:
                message = (
                    f"Invalid weekly rollover from 0 to 6 (0 is Monday): {self.when}"
                )
                raise ValueError(message)

            if self.when[1] < "0" or self.when[1] > "6":
                message = "Invalid day specified for weekly rollover: {self.when}"
                raise ValueError(message)

            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}$"
        else:
            message = "Invalid rollover interval specified: {self.when}"
            raise ValueError(message)

        current_time = int(time())

        filename = self.calculate_filename(current_time)

        BaseRotatingHandler.__init__(self, filename, "a", encoding, delay)

        self.extMatch = re.compile(self.extMatch)
        self.interval = self.interval * interval

        self.rolloverAt = self.computeRollover(current_time)

    def calculate_filename(self, current_time: int):
        timeTuple = gmtime(current_time) if self.utc else localtime(current_time)
        now = datetime.datetime.fromtimestamp(current_time)

        base_folder = path.join(self.folderName, now.strftime("%Y/%m/%d"))

        makedirs(base_folder, exist_ok=True)

        pid_hash = str(getpid())
        basename = (
            self.origFileName + "." + strftime(self.suffix, timeTuple) + "." + pid_hash
        )
        new_filename = basename + self.postfix

        new_filepath = path.join(base_folder, new_filename)

        return new_filepath

    def get_files_to_delete(self, newFileName: str):
        dirName, fName = path.split(self.origFileName)
        dName, newFileName = path.split(newFileName)

        fileNames = listdir(dirName)
        result = []
        prefix = fName + "."
        postfix = self.postfix
        prelen = len(prefix)
        postlen = len(postfix)
        for fileName in fileNames:
            is_new = (
                fileName[:prelen] == prefix
                and fileName[-postlen:] == postfix
                and len(fileName) - postlen > prelen
                and fileName != newFileName
            )

            if is_new:
                suffix = fileName[prelen : len(fileName) - postlen]
                if self.extMatch.match(suffix):
                    filepath = path.join(dirName, fileName)
                    result.append(filepath)

        result.sort()
        if len(result) < self.backupCount:
            result = []
        else:
            until = len(result) - self.backupCount
            result = result[:until]

        return result

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        currentTime = self.rolloverAt
        newFileName = self.calculate_filename(currentTime)
        self.baseFilename = path.abspath(newFileName)
        self.mode = "a"
        self.stream = self._open()

        # Delete old log files
        if self.backupCount > 0:
            for s in self.get_files_to_delete(newFileName):
                try:
                    remove(s)
                except OSError:
                    pass

        # Calculate the next rollover time
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        is_when_dst = self.when == "MIDNIGHT" or self.when.startswith("W")
        is_dst = is_when_dst and not self.utc
        if is_dst:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                # if DST kicks in before next rollover, we deduct an hour. Otherwise, add an hour
                newRolloverAt = (
                    newRolloverAt - 3600 if not dstNow else newRolloverAt + 3600
                )

        self.rolloverAt = newRolloverAt

    def __repr__(self):
        from reprlib import repr

        args_1 = f"{self.baseFilename!r}, '{self.when}', {self.interval},"
        args_2 = f"{self.backupCount}, '{self.encoding}', {self.utc},"
        args_3 = f"{self.atTime!r}, '{self.postfix}'"

        args_str = f"{args_1} {args_2} {args_3}"
        return repr(f"{self.__class__.__name__}({args_str})")
