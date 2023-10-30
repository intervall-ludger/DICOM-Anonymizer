import configparser
from PyQt6.QtWidgets import QTableWidget


def save_config(tagsTable: QTableWidget, file_path: str = "config.ini"):
    """
    Save the current configuration to a file.

    Args:
        tagsTable (QTableWidget): The table containing tag configurations.
        file_path (str, optional): Path to save the config file. Defaults to "config.ini".
    """
    config = configparser.ConfigParser()

    for row in range(tagsTable.rowCount()):
        tag = tagsTable.item(row, 1).text()  # Getting the tag name
        for col in range(3, 8):
            radio_button = tagsTable.cellWidget(row, col)
            if radio_button.isChecked():
                action = str(col)
                break
        config[tag] = {"Action": action}

    with open(file_path, "w") as configfile:
        config.write(configfile)


def load_config(tagsTable: QTableWidget, file_path: str = "config.ini"):
    """
    Load configurations from a file and apply to the table.

    Args:
        tagsTable (QTableWidget): The table to update with configurations.
        file_path (str, optional): Path to load the config file from. Defaults to "config.ini".
    """
    config = configparser.ConfigParser()
    config.read(file_path)

    for row in range(tagsTable.rowCount()):
        tag = tagsTable.item(row, 1).text()
        if tag in config:
            action = config[tag]["Action"]
            radio_button = tagsTable.cellWidget(row, int(action))
            radio_button.setChecked(True)


def auto_select(tagsTable: QTableWidget):
    """
    Automatically select configurations for known sensitive tags.

    Args:
        tagsTable (QTableWidget): The table to update with configurations.
    """

    for row in range(tagsTable.rowCount()):
        tag_name = tagsTable.item(row, 1).text()
        if "Patient" in tag_name or "Date" in tag_name or "ID" in tag_name:
            tagsTable.cellWidget(row, 5).setChecked(True)
