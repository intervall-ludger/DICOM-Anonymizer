import os
import pydicom
import configparser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidget, QPushButton, QVBoxLayout,
                             QWidget, QRadioButton, QLabel, QButtonGroup, QMenuBar, QMenu, QTableWidgetItem,
                             QHeaderView, QHBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from pathlib import Path
from utilities.helper_function import load_dcm_files


class DICOMAnonymizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DICOM Anonymizer')
        self.setGeometry(100, 100, 800, 600)

        # Menu Bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        file_menu = QMenu('File', self)
        menubar.addMenu(file_menu)

        save_action = QAction(QIcon(), 'Save Config', self)
        save_action.triggered.connect(self.saveConfig)
        file_menu.addAction(save_action)

        load_action = QAction(QIcon(), 'Load Config', self)
        load_action.triggered.connect(self.loadConfig)
        file_menu.addAction(load_action)

        # Main Layout
        main_layout = QVBoxLayout()

        # Folder Selector
        self.folderBtn = QPushButton('Select Folder', self)
        self.folderBtn.clicked.connect(self.selectFolder)
        main_layout.addWidget(self.folderBtn)

        # Tags Table
        self.tagsTable = QTableWidget(0, 8)
        self.tagsTable.setHorizontalHeaderLabels(
            ['Tag (Flag)', 'Tag Name', "value", 'Unchanged', 'Change', 'Dummy value', 'Delete', 'Encrypt'])
        self.tagsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.tagsTable)

        # Radio buttons for Anonymize or Encrypt
        radio_layout = QHBoxLayout()

        # Password input for encryption
        self.passwordLabel = QLabel("Encryption Password:")
        self.passwordInput = QLineEdit(self)
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        radio_layout.addWidget(self.passwordLabel)
        radio_layout.addWidget(self.passwordInput)
        self.passwordLabel.setVisible(True)
        self.passwordInput.setVisible(True)


        main_layout.addLayout(radio_layout)

        self.autoSelectBtn = QPushButton('Auto Select', self)
        self.autoSelectBtn.clicked.connect(self.autoSelect)
        main_layout.addWidget(self.autoSelectBtn)

        # Process Button
        self.processBtn = QPushButton('Process', self)
        self.processBtn.clicked.connect(self.processFiles)
        main_layout.addWidget(self.processBtn)

        centralWidget = QWidget(self)
        centralWidget.setLayout(main_layout)
        self.setCentralWidget(centralWidget)

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder = folder
            self.getDICOMTags()

    def getDICOMTags(self):
        self.tagsTable.setRowCount(0)
        tags_set = set()

        # Lesen Sie einen repräsentativen DICOM-Datei, um die Tag-Werte zu erhalten
        flags = []
        for representative_file in load_dcm_files(self.folder):
            ds = pydicom.dcmread(str(representative_file))

            for elem in ds:
                tag_flag = str(elem.tag)
                if tag_flag in flags:
                    continue
                flags.append(tag_flag)
                tag_name = elem.keyword
                if tag_name:
                    value = str(elem.value)[:20]
                    tags_set.add((tag_flag, tag_name, value))

        for tag_flag, tag_name, value in sorted(tags_set, key=lambda x: x[1]):
            row_position = self.tagsTable.rowCount()
            self.tagsTable.insertRow(row_position)

            self.tagsTable.setItem(row_position, 0, QTableWidgetItem(tag_flag))
            self.tagsTable.setItem(row_position, 1, QTableWidgetItem(tag_name))

            value_input = QLineEdit(value)
            self.tagsTable.setCellWidget(row_position, 2, value_input)

            self.addActionsToRow(row_position)

    def addActionsToRow(self, row):
        radio_group = QButtonGroup(self)
        unchanged_radio = QRadioButton("")
        change_dummy_radio = QRadioButton("")
        change_value_radio = QRadioButton("")
        delete_radio = QRadioButton("")
        encryptRadio =  QRadioButton("")

        radio_group.addButton(unchanged_radio)
        radio_group.addButton(change_dummy_radio)
        radio_group.addButton(change_value_radio)
        radio_group.addButton(delete_radio)
        radio_group.addButton(encryptRadio)

        self.tagsTable.setCellWidget(row, 3, unchanged_radio)
        self.tagsTable.setCellWidget(row, 4, change_dummy_radio)
        self.tagsTable.setCellWidget(row, 5, change_value_radio)
        self.tagsTable.setCellWidget(row, 6, delete_radio)
        self.tagsTable.setCellWidget(row, 7, encryptRadio)
        unchanged_radio.setChecked(True)

    def saveConfig(self):
        config = configparser.ConfigParser()

        for row in range(self.tagsTable.rowCount()):
            tag = self.tagsTable.item(row, 1).text()  # Getting the tag name
            for col in range(3, 8):
                radio_button = self.tagsTable.cellWidget(row, col)
                if radio_button.isChecked():
                    action = str(col)
                    break
            config[tag] = {"Action": action}

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        for row in range(self.tagsTable.rowCount()):
            tag = self.tagsTable.item(row, 1).text()
            if tag in config:
                action = config[tag]["Action"]
                radio_button = self.tagsTable.cellWidget(row, int(action))
                radio_button.setChecked(True)


    def autoSelect(self):
        # Define a default mapping here
        default_mapping = {
            "PatientName": "Change",
            "PatientID": "Delete",
            "PatientBirthDate": "Change",
            "PatientSex": "Delete"
        }

        for row in range(self.tagsTable.rowCount()):
            tag_name = self.tagsTable.item(row, 1).text()
            if tag_name in default_mapping:
                action = default_mapping[tag_name]
                if action == "Unchanged":
                    self.tagsTable.cellWidget(row, 2).setChecked(True)
                elif action == "Change":
                    self.tagsTable.cellWidget(row, 3).setChecked(True)
                elif action == "Delete":
                    self.tagsTable.cellWidget(row, 4).setChecked(True)
                elif action == "Encrypt":
                    self.tagsTable.cellWidget(row, 5).setChecked(True)

    def processFiles(self):
        dummy_ds = pydicom.dcmread(pydicom.data.get_testdata_file("CT_small.dcm"))

        for root, _, files in os.walk(self.folder):
            for file in files:
                if file.endswith('.dcm'):
                    filepath = os.path.join(root, file)
                    output_filepath = os.path.join(root + '_new', file)
                    ds = pydicom.dcmread(filepath)

                    for row in range(self.tagsTable.rowCount()):
                        tag_name = self.tagsTable.item(row, 1).text()
                        if tag_name in ds:
                            action = self.getActionForRow(row)
                            tag = pydicom.datadict.tag_for_keyword(tag_name)

                            if action == "Change with Dummy Value":
                                ds[tag].value = dummy_ds.get(tag_name, "")
                            elif action == "Change with Value":
                                new_value = self.tagsTable.cellWidget(row, 2).text()
                                ds[tag].value = new_value
                            elif action == "Delete":
                                del ds[tag]
                            if 'Encrypt':
                                pass

                    Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
                    ds.save_as(output_filepath)

    def getActionForRow(self, row):
        if self.tagsTable.cellWidget(row, 3).isChecked():
            return "Unchanged"
        elif self.tagsTable.cellWidget(row, 5).isChecked():
            return "Change with Dummy Value"
        elif self.tagsTable.cellWidget(row, 4).isChecked():
            return "Change with Value"
        elif self.tagsTable.cellWidget(row, 7).isChecked():
            return 'Encrypt'
        else:
            return "Delete"

    def findRowForTag(self, tag_name):
        """Findet die Zeile in der Tabelle, die einem gegebenen DICOM-Tag entspricht."""
        for row in range(self.tagsTable.rowCount()):
            if self.tagsTable.item(row, 1).text() == tag_name:
                return row
        return None


if __name__ == '__main__':
    app = QApplication([])
    window = DICOMAnonymizer()
    window.show()
    app.exec()
