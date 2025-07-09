modules = {
    "google_auth_oauthlib": "google_auth_oauthlib",
    "googleapiclient": "googleapiclient.discovery",
    "google_auth_httplib2": "google_auth_httplib2",
    "pydrive2": "pydrive2.auth",
    "watchdog": "watchdog.observers",
    "apscheduler": "apscheduler.schedulers.background",
    "PySimpleGUI": "PySimpleGUI",
    "sqlite3": "sqlite3",
}

for name, test_import in modules.items():
    try:
        __import__(test_import)
        print(f"[ OK ] {name}")
    except ImportError as e:
        print(f"[FAIL] {name}: {e}")
# validate_deps.py
modules = {}

for name, test_import in modules.items():
    try:
        __import__(test_import)
        print(f"[ OK ] {name}")
    except ImportError as e:
        print(f"[FAIL] {name}: {e}")
