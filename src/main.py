import sys
import threading
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
import PySimpleGUI as sg

# Logging setup
logging.basicConfig(
    filename="offloader.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("offloader")

# Configuration
EXTENSIONS = [
    ".mp4",
    ".mp3",
    ".zip",
    ".rar",
    ".iso",
    ".exe",
    ".msi",
    ".mov",
    ".mkv",
    ".jpg",
    ".png",
    ".pdf",
]
MIN_AGE_DAYS = 30
MIN_SIZE_BYTES = 50 * 1024**2

# Platform-specific drive roots and default excluded folders
if sys.platform.startswith("win"):
    DRIVES = [Path("C:/"), Path("D:/")]
    DEFAULT_EXCLUDED_FOLDERS = [
        "C:/Windows",
        "C:/Program Files",
        "D:/Unity/Projects",
        "D:/Games",
    ]
else:
    DRIVES = [Path("/")]
    DEFAULT_EXCLUDED_FOLDERS = []

# Regex for validating extensions: must start with dot, followed by 1-10 alphanumeric chars
EXT_REGEX = re.compile(r"^\.[A-Za-z0-9]{1,10}$")


def scan_and_summarize(stop_event, extensions, excluded_folders):
    cutoff = datetime.now() - timedelta(days=MIN_AGE_DAYS)
    counts = {ext: 0 for ext in extensions}
    for drive in DRIVES:
        if stop_event.is_set():
            break
        for ext in extensions:
            if stop_event.is_set():
                break
            for f in drive.rglob(f"*{ext}"):
                if stop_event.is_set():
                    break
                try:
                    stat = f.stat()
                except (OSError, PermissionError):
                    continue
                path_str = str(f)
                if (
                    datetime.fromtimestamp(stat.st_mtime) < cutoff
                    and stat.st_size > MIN_SIZE_BYTES
                    and not any(path_str.startswith(exc) for exc in excluded_folders)
                ):
                    counts[ext] += 1
    return counts


def worker_scan(window, stop_event, extensions, excluded_folders):
    summary = scan_and_summarize(stop_event, extensions, excluded_folders)
    if stop_event.is_set():
        window.write_event_value("-SCAN_CANCELLED-", None)
    else:
        window.write_event_value("-SCAN_DONE-", summary)


def main():
    sg.theme("SystemDefault")
    ext_list = sorted(EXTENSIONS.copy())
    folder_list = sorted(DEFAULT_EXCLUDED_FOLDERS.copy())

    layout = [
        [sg.Text("Offloader Control", font=("Segoe UI", 14))],
        [
            sg.Button("Start", key="-TOGGLE-", size=(10, 1)),
            sg.Button("Exit Gracefully", size=(14, 1)),
        ],
        [
            sg.Frame(
                "File Types",
                [
                    [
                        sg.Input(key="-NEW-EXT-", size=(10, 1)),
                        sg.Button("Add", key="-ADD-EXT-"),
                    ],
                    [sg.Listbox(values=ext_list, size=(20, 5), key="-EXT-LIST-")],
                    [sg.Button("Remove Selected", key="-REMOVE-EXT-")],
                ],
            )
        ],
        [
            sg.Frame(
                "Excluded Folders",
                [
                    [
                        sg.Input(key="-NEW-FOLDER-", size=(30, 1)),
                        sg.Button("Add", key="-ADD-FOLDER-"),
                    ],
                    [sg.Listbox(values=folder_list, size=(30, 5), key="-FOLDER-LIST-")],
                    [sg.Button("Remove Selected", key="-REMOVE-FOLDER-")],
                ],
            )
        ],
        [sg.Multiline(size=(60, 15), key="-LOG-")],
    ]

    window = sg.Window("Offloader", layout, element_justification="c", finalize=True)
    scan_thread = None
    stop_event = None

    def log(msg):
        window["-LOG-"].print(msg)
        logger.info(msg)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit Gracefully"):
            if scan_thread and scan_thread.is_alive():
                stop_event.set()
            log("Exiting gracefully…")
            break

        if event == "-ADD-EXT-":
            raw_input = values["-NEW-EXT-"]
            if raw_input and any(c.isspace() for c in raw_input):
                log("Extensions cannot contain spaces or whitespace characters.")
                window["-NEW-EXT-"].update("")
                continue
            raw = raw_input.strip().lower() if raw_input else ""
            if not raw:
                continue
            new_ext = raw if raw.startswith(".") else f".{raw}"
            if not EXT_REGEX.fullmatch(new_ext):
                log(
                    f"Invalid extension format: {new_ext}. Use a dot and 1–10 alphanumeric characters."
                )
            elif new_ext in ext_list:
                log(f"Extension already exists: {new_ext}")
            else:
                ext_list.append(new_ext)
                ext_list.sort()
                window["-EXT-LIST-"].update(ext_list)
                log(f"Added extension: {new_ext}")
            window["-NEW-EXT-"].update("")

        elif event == "-REMOVE-EXT-":
            sel = values["-EXT-LIST-"]
            if sel:
                for ext in sel:
                    ext_list.remove(ext)
                ext_list.sort()
                window["-EXT-LIST-"].update(ext_list)
                log(f'Removed extensions: {", ".join(sel)}')

        elif event == "-TOGGLE-":
            if not scan_thread or not scan_thread.is_alive():
                stop_event = threading.Event()
                log("Scanning drives...")
                scan_thread = threading.Thread(
                    target=worker_scan,
                    args=(window, stop_event, ext_list, folder_list),
                    daemon=True,
                )
                scan_thread.start()
                window["-TOGGLE-"].update("Stop")
            else:
                log("Kill command received")
                stop_event.set()
                window["-TOGGLE-"].update("Start")

        elif event == "-SCAN_DONE-":
            summary = values["-SCAN_DONE-"]
            log("Scan complete. Summary by extension:")
            for ext, cnt in summary.items():
                log(f"  * {ext}: {cnt} files")
            window["-TOGGLE-"].update("Start")

        elif event == "-SCAN_CANCELLED-":
            log("Scan cancelled.")
            window["-TOGGLE-"].update("Start")

    window.close()


if __name__ == "__main__":
    main()
