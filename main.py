import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime

class MonitorFolder(FileSystemEventHandler):
    def __init__(self, f):
        self.first = f

    def on_created(self, event):
        filepath = Path(event.src_path)

        filename = filepath.stem
        tokens: list[str] = filename.split("]", 1)
        if len(tokens) > 1:
           tokens = tokens[1].split("-", 1)
        
        # split always returns the original string if it can't find the delimiter
        txt: str = tokens[0].strip()

        absPath = Path(self.first)
        found_folder = list(absPath.glob(txt))

        time_now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        with open(absPath / "log.txt", "w") as opened_file:
            if len(found_folder) == 0:
                create_folder = absPath / txt
                create_folder.mkdir(exist_ok=True)
                filepath.replace(create_folder / filepath.name)
                opened_file.write(
                    f"[LOG]{time_now} - {filename}: Created folder '{txt}' and moved file into it."
                )
            elif len(found_folder) == 1:
                newPath = found_folder[0] / filepath.name
                filepath.replace(newPath)
                opened_file.write(
                    f"[LOG]{time_now} - {filename}: Folder found, moving file to '{txt}'."
                )
            else:
                opened_file.write(
                    f"[ERROR]{time_now} - {filename}: File not moved, found multiple possible folders."
                )

if __name__ == "__main__":
    src_path = sys.argv[1]
    src_deposit = sys.argv[2]

    event_handler = MonitorFolder(src_deposit)
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        observer.join()
