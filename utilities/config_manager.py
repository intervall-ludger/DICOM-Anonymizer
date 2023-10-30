import configparser
from PyQt6.QtWidgets import QTableWidget


def save_config(tagsTable: QTableWidget, file_path: str = "config.ini") -> None:
    """
    Save the current configuration of DICOM tags to a file.

    Parameters:
        tagsTable (QTableWidget): Table containing the tag configurations.
        file_path (str, optional): Path to save the config file. Defaults to "config.ini".
    """
    config = configparser.ConfigParser()

    # Iterate over each row in the table to extract tag configurations
    for row in range(tagsTable.rowCount()):
        tag = tagsTable.item(row, 1).text()  # Getting the tag name
        for col in range(3, 8):
            radio_button = tagsTable.cellWidget(row, col)
            if radio_button.isChecked():
                action = str(col)
                break
        config[tag] = {"Action": action}

    # Save the configurations to the specified file
    with open(file_path, "w") as configfile:
        config.write(configfile)


def load_config(tagsTable: QTableWidget, file_path: str = "config.ini") -> None:
    """
    Load configurations of DICOM tags from a file and apply them to the table.

    Parameters:
        tagsTable (QTableWidget): Table to update with loaded configurations.
        file_path (str, optional): Path to load the config file from. Defaults to "config.ini".
    """
    config = configparser.ConfigParser()
    config.read(file_path)

    # Apply the loaded configurations to the table
    for row in range(tagsTable.rowCount()):
        tag = tagsTable.item(row, 1).text()
        if tag in config:
            action = config[tag]["Action"]
            radio_button = tagsTable.cellWidget(row, int(action))
            radio_button.setChecked(True)


def auto_select(tagsTable: QTableWidget) -> None:
    """
    Automatically select configurations for known sensitive DICOM tags.

    Parameters:
        tagsTable (QTableWidget): Table to update with auto-selected configurations.
    """

    # Auto-select configurations for tags with sensitive information
    for row in range(tagsTable.rowCount()):
        tag_name = tagsTable.item(row, 1).text().lower()
        if (
            "patient" in tag_name
            or "date" in tag_name
            or "id" in tag_name
            or "name" in tag_name
        ):
            tagsTable.cellWidget(row, 5).setChecked(True)
        else:
            tagsTable.cellWidget(row, 3).setChecked(True)
