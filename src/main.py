import PySimpleGUI as sg
from db import OffloaderDB

# Existing imports and setup here


def load_configs(db):
    return db.get_configs()


def save_configs(db, configs):
    db.save_configs(configs)


def config_editor_window(db):
    configs = load_configs(db)

    layout = [
        [sg.Text("Included File Extensions (one per line):")],
        [
            sg.Multiline(
                "\n".join(configs["extensions"]), key="extensions", size=(40, 5)
            )
        ],
        [sg.Text("Excluded Directories (one per line):")],
        [
            sg.Multiline(
                "\n".join(configs["excluded_dirs"]), key="excluded_dirs", size=(40, 5)
            )
        ],
        [sg.Text("Minimum File Size (MB):")],
        [sg.Input(configs["min_file_size_mb"], key="min_file_size_mb", size=(10, 1))],
        [sg.Text("File Age (Days):")],
        [sg.Input(configs["file_age_days"], key="file_age_days", size=(10, 1))],
        [sg.HorizontalSeparator()],
        [sg.Button("Save Config"), sg.Button("Reset to Defaults"), sg.Button("Cancel")],
    ]

    window = sg.Window("Offloader Configuration Editor", layout, modal=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Cancel"):
            break

        elif event == "Save Config":
            new_configs = {
                "extensions": [
                    ext.strip()
                    for ext in values["extensions"].splitlines()
                    if ext.strip()
                ],
                "excluded_dirs": [
                    d.strip() for d in values["excluded_dirs"].splitlines() if d.strip()
                ],
                "min_file_size_mb": int(values["min_file_size_mb"]),
                "file_age_days": int(values["file_age_days"]),
            }
            save_configs(db, new_configs)
            sg.popup("Configurations saved successfully!")
            break

        elif event == "Reset to Defaults":
            default_configs = db.get_default_configs()
            window["extensions"].update("\n".join(default_configs["extensions"]))
            window["excluded_dirs"].update("\n".join(default_configs["excluded_dirs"]))
            window["min_file_size_mb"].update(default_configs["min_file_size_mb"])
            window["file_age_days"].update(default_configs["file_age_days"])

    window.close()


# Main application flow
def main():
    db = OffloaderDB("~/.offloader/offloader_index.db")

    layout = [
        [sg.Text("Offloader Main Menu")],
        [sg.Button("Edit Configurations")],
        [sg.Button("Start Scan")],
        [sg.Button("Exit")],
    ]

    window = sg.Window("Offloader", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        elif event == "Edit Configurations":
            config_editor_window(db)

        elif event == "Start Scan":
            # Call your existing scanning logic here
            pass

    window.close()


if __name__ == "__main__":
    main()
